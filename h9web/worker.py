import logging
import tornado.websocket
import os
import signal
import json
import base64
from io import TextIOWrapper
import codecs

from tornado.ioloop import IOLoop
from tornado.iostream import _ERRNO_CONNRESET
from tornado.util import errno_from_exception


BUF_SIZE = 24
clients = {}  # {ip: {id: worker}}


def clear_worker(worker, clients):
    ip = worker.src_addr[0]
    workers = clients.get(ip)
    assert worker.id in workers
    workers.pop(worker.id)

    if not workers:
        clients.pop(ip)
        if not clients:
            clients.clear()


def recycle_worker(worker):
    if worker.handler:
        return
    logging.warning('Recycling worker {}'.format(worker.id))
    worker.close(reason='worker recycled')


class Worker(object):
    def __init__(self, loop, pid, fd):
        self.loop = loop
        self.pid = pid
        self.fd = fd
        self.handler = None
        self.mode = IOLoop.READ
        self.closed = False
        self.id = str(id(self))
        self.data_to_dst = []
        decoder_factory = codecs.getincrementaldecoder('utf8')
        self.decoder_instance = decoder_factory()

    def __call__(self, fd, events):
        if events & IOLoop.READ:
            self.on_read()
        if events & IOLoop.WRITE:
            self.on_write()
        if events & IOLoop.ERROR:
            self.close(reason='error event occurred')

    def set_handler(self, handler):
        if not self.handler:
            self.handler = handler

    def update_handler(self, mode):
        if self.mode != mode:
            self.loop.update_handler(self.fd, mode)
            self.mode = mode
        if mode == IOLoop.WRITE:
            self.loop.call_later(0.1, self, self.fd, IOLoop.WRITE)

    def on_read(self):
        logging.debug('worker {} on read'.format(self.id))
        try:
            chunk = os.read(self.fd, BUF_SIZE)
#             data = self.testwrapper.read()#errors='replace')
        except (OSError, IOError) as e:
            logging.error(e)
            self.close(reason='chan error on reading')
        else:
            if not chunk:
                self.close(reason='chan closed')
                return
#             logging.warning(data)
            #data = base64.b64encode(data.encode('utf-8')).decode('ascii')
            #js = json.dumps({"data": data.decode('utf-8')})

            data = self.decoder_instance.decode(chunk)
            js = json.dumps({"data": data})

            #logging.debug('{} to {}:{}'.format(js, *self.handler.src_addr))
            #logging.debug('{}'.format(js))
            #logging.debug('{}'.format(data.decode('utf-8')))
            try:
                # self.handler.write_message(js, binary=False)
                self.handler.write_message(data, binary=True)
            except tornado.websocket.WebSocketClosedError:
                self.close(reason='websocket closed')

    def on_write(self):
        logging.debug('worker {} on write'.format(self.id))
        if not self.data_to_dst:
            return

        data = ''.join(self.data_to_dst)
        logging.debug('{!r} from {}:{}'.format(data, *self.handler.src_addr))

        try:
            sent = os.write(self.fd, data.encode('UTF-8'))
            #sent =self.testwrapper.write(data)
        except (OSError, IOError) as e:
            logging.error(e)
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close(reason='chan error on writing')
            else:
                self.update_handler(IOLoop.WRITE)
        else:
            self.data_to_dst = []
            data = data[sent:]
            if data:
                self.data_to_dst.append(data)
                self.update_handler(IOLoop.WRITE)
            else:
                self.update_handler(IOLoop.READ)

    def close(self, reason=None):
        if self.closed:
            return
        self.closed = True

        logging.info(
            'Closing worker {} with reason: {}'.format(self.id, reason)
        )
        if self.handler:
            self.loop.remove_handler(self.fd)

        os.close(self.fd)
        try:
            os.kill(self.pid, signal.SIGTERM)
            logging.info('Kill subprocess {}'.format(self.pid))
        except ProcessLookupError:
            pass
        self._reap()

        if self.handler:
            # the handler decides what next: restart h9cli or nothing if the websocket is gone
            self.handler.on_cli_exit(reason)

    def _reap(self, attempts=10):
        """Collect the exit status of the child, otherwise it stays as a zombie process."""
        try:
            pid, _ = os.waitpid(self.pid, os.WNOHANG)
        except ChildProcessError:
            return
        if pid == 0 and attempts > 0:
            self.loop.call_later(0.5, self._reap, attempts - 1)
        elif pid == 0:
            os.kill(self.pid, signal.SIGKILL)
            self.loop.call_later(0.5, self._reap, 0)
