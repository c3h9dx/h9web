import json
import logging
import struct
import weakref
import tornado.web
import tornado.websocket
import pty
import fcntl
import os
import termios
from tornado.ioloop import IOLoop
from json.decoder import JSONDecodeError
from h9web.worker import Worker


class CliWSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, loop):
        self.loop = loop
        self.worker_ref = None
        self.cli = self.settings['cli']

    def get_current_user(self):
        #TODO: add expired date
        return self.get_signed_cookie(self.AUTH_COOKIE)

    def get_client_addr(self) -> (str, int):
        #TODO: add support for X-Headers
        return self.request.connection.context.address[:2]

    def check_origin(self, origin):
        return True

    def prepare(self):
        pass
        #return True
        #if not self.get_current_user():
        #    raise tornado.web.HTTPError(401)

    def spawn_cli(self):
        (child_pid, fd) = pty.fork()
        if child_pid == 0:
            # this is the child process fork.
            # anything printed here will show up in the pty, including the output
            # of this subprocess
            os.execv(self.cli, [self.cli.split('/')[-1]])

        flag = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)

        worker = Worker(self.loop, child_pid, fd)
        worker.encoding = 'utf-8'
        return worker

    # h9cli exits when it loses its connection to h9d - it is restarted after these delays [s],
    # the sequence starts over once h9cli has been running for STABLE_RUN seconds
    RESTART_DELAYS = (1, 2, 5, 10)
    STABLE_RUN = 10

    def open(self):
        self.src_addr = self.get_client_addr()
        logging.info('Connected from {}:{}'.format(*self.src_addr))
        self.set_nodelay(True)

        self.client_gone = False
        self.restarts = 0
        self.restart_handle = None
        self.started_at = 0
        self.start_cli()

    def start_cli(self):
        self.restart_handle = None
        if self.client_gone:
            return

        worker = self.spawn_cli()
        worker.set_handler(self)
        self.worker_ref = weakref.ref(worker)
        self.worker = worker  # keep it alive while it runs
        self.started_at = self.loop.time()
        self.loop.add_handler(worker.fd, worker, IOLoop.READ)

    def on_cli_exit(self, reason):
        """Called by the worker once the h9cli process has ended."""
        self.worker = None
        if self.client_gone:
            return

        if self.loop.time() - self.started_at >= self.STABLE_RUN:
            self.restarts = 0
        delay = self.RESTART_DELAYS[min(self.restarts, len(self.RESTART_DELAYS) - 1)]
        self.restarts += 1

        try:
            self.write_message('\r\n\x1b[33m[h9cli exited ({}) - restarting in {} s]\x1b[0m\r\n'.format(reason, delay),
                               binary=True)
        except tornado.websocket.WebSocketClosedError:
            return
        self.restart_handle = self.loop.call_later(delay, self.start_cli)

    def on_message(self, message):
        logging.debug('{!r} from {}:{}'.format(message, *self.src_addr))
        worker = self.worker_ref() if self.worker_ref else None
        if not worker or worker.closed:
            return  # h9cli is being restarted
        worker.data_to_dst.append(message)
        worker.on_write()
        # try:
        #     msg = json.loads(message)
        # except JSONDecodeError:
        #     return
        #
        # if not isinstance(msg, dict):
        #     return
        #
        # resize = msg.get('resize')
        # if resize and len(resize) == 2:
        #     winsize = struct.pack("HHHH", resize[1], resize[0], 0, 0)
        #     fcntl.ioctl(worker.fd, termios.TIOCSWINSZ, winsize)
        #
        # data = msg.get('data')
        # if data and isinstance(data, str):
        #     worker.data_to_dst.append(data)
        #     worker.on_write()

    def on_close(self):
        logging.info('Disconnected from {}:{}'.format(*self.src_addr))
        if not self.close_reason:
            self.close_reason = 'client disconnected'

        self.client_gone = True
        if self.restart_handle:
            self.loop.remove_timeout(self.restart_handle)
            self.restart_handle = None

        worker = self.worker_ref() if self.worker_ref else None
        if worker:
            worker.close(reason=self.close_reason)
