import logging
import json
import jsonrpc
from tornado import gen
from h9web.api import APIHandler
from h9web.event import Event


class DevsList(APIHandler):
    async def get(self):
        try:
            res = await self.h9d.call_request(jsonrpc.request("get_devs_list"))
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")


class DevInfo(APIHandler):
    """Device description (type, plugin version, nodes, methods, CPU usage) and current state."""
    async def get(self, dev_name):
        try:
            description, state = await gen.multi([
                self.h9d.call_request(jsonrpc.request("get_dev_description", params={"dev_name": dev_name})),
                self.h9d.call_request(jsonrpc.request("get_dev_status", params={"dev_name": dev_name})),
            ])
            self.return_success({"description": description, "state": state})
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")


class Dev(APIHandler):
    async def post(self, dev_name, method):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
            logging.warning(self.request.body)
            data = {}
        if not isinstance(data, dict):
            self.return_error(400, 400, "Method parameters must be a JSON object")
            return
        logging.warning(data)
        rpc_req = jsonrpc.request("dev_method_call", params={"dev_name": dev_name, "method": method} | data)
        try:
            res = await self.h9d.call_request(rpc_req)

            self.return_success(res)

            logging.debug(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")

    @classmethod
    async def on_dev_state_update(cls, dev, state):
        await Event.publish_to_all(Event.DEV_EVENT, {"dev_name": dev, "state": state})
