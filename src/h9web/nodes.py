import logging
import json
import jsonrpc
from h9web.api import APIHandler


class Nodes (APIHandler):
    async def get(self):
        rpc_req = jsonrpc.request("get_nodes_list")

        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")


class NodesDiscovery (APIHandler):
    async def post(self):
        rpc_req = jsonrpc.request("discover_nodes")

        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")
