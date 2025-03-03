import logging
import json
import jsonrpc
from h9web.api import APIHandler
from h9web.event import Event


class Dev(APIHandler):
    async def post(self, dev_name, method):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError as e:
            logging.warning(self.request.body)
            data = {}
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
