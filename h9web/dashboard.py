import logging
import json
import os
import jsonrpc
from tornado import gen
from tornado.options import options
from h9web.api import APIHandler


class Dashboard(APIHandler):
    """One tile per h9d device. Tile positions are kept in options.dashboard_file,
    the device list, types, methods and current state come from h9d on every GET."""

    GRID_COLS = 12
    TILE_W = 3
    TILE_H = 4
    LAYOUT_KEYS = ("i", "x", "y", "w", "h")

    _layout = None  # cached content of dashboard_file

    @classmethod
    def _path(cls):
        return os.path.expanduser(options.dashboard_file)

    @classmethod
    def load_layout(cls):
        if cls._layout is None:
            try:
                with open(cls._path()) as f:
                    cls._layout = json.load(f)
            except FileNotFoundError:
                cls._layout = []
            except (OSError, ValueError) as e:
                logging.error("Unable to read dashboard layout {} - {}".format(cls._path(), e))
                cls._layout = []
        return cls._layout

    @classmethod
    def save_layout(cls, layout):
        cls._layout = layout
        path = cls._path()
        try:
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            tmp = path + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(layout, f, indent=1)
            os.replace(tmp, path)
        except OSError as e:
            logging.error("Unable to save dashboard layout {} - {}".format(path, e))

    @classmethod
    def merge_layout(cls, layout, dev_names):
        """Drop tiles of devices h9d no longer has, add tiles for new ones below the existing."""
        merged = [item for item in layout if item["i"] in dev_names]
        placed = {item["i"] for item in merged}
        bottom = max((item["y"] + item["h"] for item in merged), default=0)
        per_row = cls.GRID_COLS // cls.TILE_W
        new = [name for name in dev_names if name not in placed]
        for n, name in enumerate(new):
            merged.append({"i": name,
                           "x": (n % per_row) * cls.TILE_W,
                           "y": bottom + (n // per_row) * cls.TILE_H,
                           "w": cls.TILE_W,
                           "h": cls.TILE_H})
        return merged

    async def _call(self, method, **params):
        return await self.h9d.call_request(jsonrpc.request(method, params=params or None))

    async def get(self):
        try:
            devs = await self._call("get_devs_list")
            names = [d["name"] for d in devs]
            descriptions, states = await gen.multi([
                gen.multi([self._call("get_dev_description", dev_name=n) for n in names]),
                gen.multi([self._call("get_dev_status", dev_name=n) for n in names]),
            ])
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
            return
        except self.h9d.H9dDisconnect:
            self.return_error(501, 501, "H9d disconnected")
            return

        self.return_success({
            "layout": self.merge_layout(self.load_layout(), names),
            "devs": {d["name"]: {"type": d["type"],
                                 "methods": desc.get("dev_methods", []),
                                 "state": state}
                     for d, desc, state in zip(devs, descriptions, states)},
        })

    async def post(self):
        try:
            layout = [{k: item[k] for k in self.LAYOUT_KEYS} for item in json.loads(self.request.body)["layout"]]
        except (KeyError, TypeError, ValueError):
            self.return_error(400, 400, "Invalid layout")
            return

        self.save_layout(layout)
        self.return_success(None)
