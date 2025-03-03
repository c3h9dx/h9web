import logging

import tornado
from tornado import gen
from tornado.iostream import StreamClosedError
from asyncio import IncompleteReadError, Future
import json
from .event import Event
import jsonrpc
from h9.asyncmsgstream import H9msgStream
from h9web.stats import Stats
from h9web.frames import Frames
from h9web.dev import Dev


class H9d:
    class H9dException(Exception):
        def __init__(self, message):
            super().__init__(message)

    class H9dDisconnect(H9dException):
        def __init__(self):
            super().__init__("H9d disconnected")

    class H9MsgException(H9dException):
        def __init__(self, code, message):
            self.code = code
            self.message = message
            super().__init__(self.message)

    entity = "h9web"

    def __init__(self, address, port):
        self.result_queue = {}
        self.h9d_address = address
        self.h9d_port = port
        self.subscribers = []
        self.msg_stream = None
        self.retry_count = 0
        self.is_close = True

    def _send_message(self, rpc_message):
        if self.is_close:
            raise H9d.H9dDisconnect()
        self.msg_stream.write_json_str(json.dumps(rpc_message))

    def flush_result_queue(self):
        for key, result_future in self.result_queue.items():
            result_future.set_exception(H9d.H9dDisconnect())
            del key

    async def on_disconnect(self):
        self.is_close = True
        self.flush_result_queue()
        await Stats.clean_stats(self)

    async def run(self):
        self.msg_stream = H9msgStream(self.h9d_address, self.h9d_port)
        while True:
            try:
                await self.msg_stream.connect(self.entity)

                req = jsonrpc.request("subscribe", params={"event": "frame"})
                self.msg_stream.write_json_str(json.dumps(req))
                data = await self.msg_stream.read_json_str()
                res = jsonrpc.parse_json(data)

                if not isinstance(res, jsonrpc.Ok) or res.id != req["id"]:
                    logging.error("H9d frame subscribe error - {}".format(res))

                req = jsonrpc.request("subscribe", params={"event": "dev_status"})
                self.msg_stream.write_json_str(json.dumps(req))
                data = await self.msg_stream.read_json_str()
                res = jsonrpc.parse_json(data)

                self.is_close = False
                self.flush_result_queue()

                if not isinstance(res, jsonrpc.Ok) or res.id != req["id"]:
                    logging.error("H9d dev_status subscribe error - {}".format(res))

                tornado.ioloop.IOLoop.current().add_callback(lambda : Stats.refresh_base_stats(self) )
                # await Stats.refresh_base_stats(self)

            except (StreamClosedError, OSError) as e:
                self.is_close = True
                if self.retry_count == 0:
                    logging.error("Unable connect to h9d - retry in 10 seconds...")
                else:
                    logging.warning("Unable connect to h9d - retry in 10 seconds...")

                # await self.on_disconnect()

                await gen.sleep(10)
                self.retry_count = self.retry_count + 1
                continue

            logging.info("Connected to h9d: {}@{}:{}".format(self.entity, self.h9d_address, self.h9d_port))
            while True:
                try:
                    data = await self.msg_stream.read_json_str()

                    msg = jsonrpc.parse_json(data)
                    if isinstance(msg, jsonrpc.Notification) and msg.method == 'on_frame':
                        logging.warning(msg)
                        await Frames.on_frame(msg.params["frame"])
                    elif isinstance(msg, jsonrpc.Notification) and msg.method == 'dev_status_update':
                        logging.warning(msg)
                        await Dev.on_dev_state_update(msg.params["dev"], msg.params["status"])
                    elif isinstance(msg, jsonrpc.Ok):
                        # logging.warning("Ok result")
                        # logging.info(msg)
                        if msg.id in self.result_queue:
                            self.result_queue[msg.id].set_result(msg.result)
                            del self.result_queue[msg.id]
                    elif isinstance(msg, jsonrpc.Error):
                        logging.warning(data)
                        if msg.id in self.result_queue:
                            self.result_queue[msg.id].set_exception(H9d.H9MsgException(msg.code, msg.message))
                            del self.result_queue[msg.id]
                    else:
                        logging.warning("Recv unsupported message {}".format(msg))
                except (StreamClosedError, IncompleteReadError, ConnectionError):
                    logging.error("Disconnected from h9d - retry in 5 seconds...")
                    await self.on_disconnect()
                    await gen.sleep(5)
                    break
                except Exception as e:
                    logging.error("Error {}".format(type(e)))
                    logging.error("Error {} on message: {}".format(e, data))

    async def call_request(self, rpc_request):
        result_future = Future()
        self._send_message(rpc_request)
        self.result_queue[rpc_request["id"]] = result_future
        # logging.debug("### a.1 ###")
        res = await result_future
        # logging.debug("### a.2 ###")
        # logging.critical(res)
        return res
