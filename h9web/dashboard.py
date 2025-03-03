import logging
import json
import jsonrpc
from h9web.api import APIHandler
from h9web.event import Event


class Dashboard(APIHandler):
    layout = [
        {"x": 0, "y": 0, "w": 3, "h": 3, "i": 'shack_switch', "static": False, "component": 'MainPowerSwitch'},
        {"x": 3, "y": 0, "w": 3, "h": 3, "i": 'antenna_switch', "static": False, "component": 'AntennaSwitch'},
        {"x": 0, "y": 5, "w": 3, "h": 4, "i": 'doublet_atu', "static": False, "component": 'ATU'}
    ]

    async def get(self):
        self.write(json.dumps({
            "status": "success",
            "response": Dashboard.layout
        }))

    async def post(self):
        data = json.loads(self.request.body)
        Dashboard.layout = data['layout']

        logging.debug(Dashboard.layout)

        self.write(json.dumps({
            "status": "success"
        }))
