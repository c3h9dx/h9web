import logging
import json
import jsonrpc
from h9web.api import APIHandler

class GetNodeInfo(APIHandler):
    #@tornado.web.authenticated
    async def get(self, node_id):
        node_id = int(node_id)

        try:
            rpc_req = jsonrpc.request("get_node_info", params={"node_id": node_id})
            res = await self.h9d.call_request(rpc_req)
            rpc_req = jsonrpc.request("get_registers_list", params={"node_id": node_id})

            req_info = await self.h9d.call_request(rpc_req)
            res["registers_list"] = req_info
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")


class NodeRegister(APIHandler):
    async def get(self, node_id, register):
        node_id = int(node_id)
        register = int(register)
        rpc_req = jsonrpc.request("get_register_value", params={"node_id": node_id, "reg": register})
        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")

    async def put(self, node_id, register):
        node_id = int(node_id)
        register = int(register)
        logging.warning(self.request.body)
        data = json.loads(self.request.body)
        logging.warning(data)
        rpc_req = jsonrpc.request("set_register_value", params={"node_id": node_id, "reg": register, "value": data["value"]})
        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")


class NodeReset (APIHandler):
    async def post(self, node_id):
        node_id = int(node_id)
        rpc_req = jsonrpc.request("node_reset",  params={"node_id": node_id})

        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")
