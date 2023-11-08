import logging
import tornado.web
import json
import traceback
from dateutil import parser
from dateutil import tz
from asyncio import IncompleteReadError
from tornado.queues import Queue
from h9web.handler import BaseHandler
# from h9.msg import H9SendFrame, H9ExecuteMethod, H9MethodResponse, H9ExecuteDeviceMethod, H9DeviceMethodResponse, H9Error
from h9.asyncmsgstream import H9msgStream
import jsonrpc
#from h9web.h9d import H9dException


class BaseAPIHandler(BaseHandler):
    h9d_connection_pool = None

    def initialize(self, h9d_int):
        super(BaseAPIHandler, self).initialize()
        self.debug = self.settings.get('debug', False)
        self.h9d = h9d_int

    def options(self, *args):
        self.set_status(204)
        self.finish()

    async def get_h9d_connection(self):
        if BaseAPIHandler.h9d_connection_pool is None:
            BaseAPIHandler.h9d_connection_pool = Queue()
            for i in range(5):
                h9d_stream = H9msgStream(self.settings.get('h9d_address'), self.settings.get('h9d_port'))
                await h9d_stream.connect("h9web_cp")
                await BaseAPIHandler.h9d_connection_pool.put(h9d_stream)
        return await BaseAPIHandler.h9d_connection_pool.get()

    def return_h9d_connection(self, connection):
        BaseAPIHandler.h9d_connection_pool.put_nowait(connection)

    async def h9d_connection_send_msg_get_response(self, msg):
        h9d_connection = await self.get_h9d_connection()
        h9d_connection.writemsg(msg)
        try:
            msg = await h9d_connection.readmsg()
        except IncompleteReadError as e:
            logging.warning("Restoring h9d connection...")
            h9d_connection = H9msgStream(self.settings.get('h9d_address'), self.settings.get('h9d_port'))
            await h9d_connection.connect("h9web_cp")
            h9d_connection.writemsg(msg)
            msg = await h9d_connection.readmsg()
        self.return_h9d_connection(h9d_connection)
        return msg


    def set_default_headers(self):
        super(BaseAPIHandler, self).set_default_headers()
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))

    def prepare(self):
        super(BaseAPIHandler, self).prepare()
        if not self.get_current_user():
            raise tornado.web.HTTPError(401)


class SendFrameAPI(BaseAPIHandler):
    #@tornado.web.authenticated
    async def post(self):
        try:
            frame = json.loads(self.request.body)
            logging.debug(frame)
        except json.JSONDecodeError:
            raise tornado.web.HTTPError(400, reason='Invalid JSON')
        except ValueError:
            raise tornado.web.HTTPError(400, reason='Invalid frame parameters')
        logging.debug('Send frame: ' + str(frame))

        frame["priority"] = "H" if frame["priority"] == 0 else "L"
        frame["data"] = frame["data"][:frame["dlc"]]

        rpc_req = jsonrpc.request("send_frame", params={"frame": frame, "raw": False})

        res = await self.h9d.call_request(rpc_req)
        self.write(res)

class GetDevicesAPI(BaseAPIHandler):
    #@tornado.web.authenticated
    async def get(self):
        rpc_req = jsonrpc.request("get_nodes_list")

        res = await self.h9d.call_request(rpc_req)
        self.write(json.dumps(res))

class GetDevicesInfoAPI(BaseAPIHandler):
    #@tornado.web.authenticated
    async def get(self, device_id):
        device_id = int(device_id)
        rpc_req = jsonrpc.request("get_node_info", params={"node_id": device_id})
        res = await self.h9d.call_request(rpc_req)
        rpc_req = jsonrpc.request("get_registers_list", params={"node_id": device_id})
        req_info = await self.h9d.call_request(rpc_req)
        res["registers_list"] = req_info
        self.write(json.dumps(res))

class DeviceRegisterAPI(BaseAPIHandler):
    async def get(self, device_id, register):
        device_id = int(device_id)
        register = int(register)
        rpc_req = jsonrpc.request("get_register_value", params={"node_id": device_id, "reg": register})
        try:
            res = await self.h9d.call_request(rpc_req)
            self.write(json.dumps(res))
        except self.h9d.H9dException as e:
            self.set_status(400)
            self.write({"code": e.code, "message": e.message})

    async def put(self, device_id, register):
        device_id = int(device_id)
        register = int(register)
        logging.warning(self.request.body)
        data = json.loads(self.request.body)
        logging.warning(data)
        rpc_req = jsonrpc.request("set_register_value", params={"node_id": device_id, "reg": register, "value": data["value"]})
        try:
            res = await self.h9d.call_request(rpc_req)
            self.write(json.dumps(res))
        except self.h9d.H9dException as e:
            self.set_status(400)
            self.write({"code": e.code, "message": e.message})

class ExecuteDevMethodAPI(BaseAPIHandler):
    async def put(self, dev_id, method):
        logging.warning(self.request.body)
        data = json.loads(self.request.body)
        logging.warning(data)
        rpc_req = jsonrpc.request("dev_call", params={"dev_id": dev_id, "method": method} | data)
        try:
            res = await self.h9d.call_request(rpc_req)
            self.write(json.dumps(res))
        except self.h9d.H9dException as e:
            self.set_status(400)
            self.write({"code": e.code, "message": e.message})
    async def get(self, dev_id, method):
        rpc_req = jsonrpc.request("dev_call", params={"dev_id": dev_id, "method": method})
        try:
            res = await self.h9d.call_request(rpc_req)
            self.write(json.dumps(res))
        except self.h9d.H9dException as e:
            self.set_status(400)
            self.write({"code": e.code, "message": e.message})
    #@tornado.web.authenticated
    # async def get(self, device_id, method_name):
    #     await self.post(device_id, method_name)
