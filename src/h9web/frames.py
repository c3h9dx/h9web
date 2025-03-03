import logging
import tornado.web
import json
import jsonrpc
from collections import deque
from h9web.api import APIHandler
from h9web.event import Event


class Frames(APIHandler):
    last_frames = deque(maxlen=10)

    async def get(self):
        self.return_success(list(Frames.last_frames))

    async def post(self):
        try:
            tmp = json.loads(self.request.body)
            frame = tmp['frame']
            logging.debug(tmp)

            frame["priority"] = "H" if frame["priority"] == 0 else "L"
            frame["data"] = frame["data"][:frame["dlc"]]

            try:
                raw = True if tmp['raw'] else False
            except KeyError:
                raw = False

        except (KeyError, json.JSONDecodeError):
            raise tornado.web.HTTPError(400, reason='Invalid JSON')
        except ValueError:
            raise tornado.web.HTTPError(400, reason='Invalid frame parameters')
        logging.debug('Send frame: ' + str(frame))

        rpc_req = jsonrpc.request("send_frame", params={"frame": frame, "raw": raw})

        try:
            res = await self.h9d.call_request(rpc_req)
            self.return_success(res)
        except self.h9d.H9MsgException as e:
            self.return_error(500, e.code, e.message)
        except self.h9d.H9dDisconnect as e:
            self.return_error(501, 501, "H9d disconnected")

    @classmethod
    async def on_frame(cls, frame):
        cls.last_frames.append(frame)
        await Event.publish_to_all(Event.FRAME_EVENT, frame)
