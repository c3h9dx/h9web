import logging
import json

import tornado.web
from tornado.iostream import StreamClosedError
from h9web.api import BaseAPIHandler
from h9.msg import H9frame


#TODO: https://github.com/mpetazzoni/sse.js ?

class Event(BaseAPIHandler):
    def initialize(self):
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')

        self.run = True
        self.context = self.request.connection.context

        Event.subscribers.append(self)
        logging.info('Connected event subscribers {}:{}'.format(*self.context.address[:2]))

    async def publish_h9bus_frame(self, msg):
        try:
            dict_data = {"type": "h9frame", "data": msg.to_dict()}
            json_data = json.dumps(dict_data)
            logging.debug('Event send {!r}'.format(json_data))

            self.write('data: {}\n\n'.format(json_data))
            await self.flush()
        except StreamClosedError:
            self.run = False

    @tornado.web.authenticated
    async def get(self):
        while self.run:
            await tornado.web.gen.sleep(10)

    def on_finish(self):
        logging.info('Disconnected event subscribers {}:{}'.format(*self.context.address[:2]))
        Event.subscribers.remove(self)

    subscribers = []

    @classmethod
    async def publish_to_all(cls, message):
        print("Writing to Clients")
        if isinstance(message, H9frame):
            await tornado.web.gen.multi([sub.publish_h9bus_frame(message) for sub in cls.subscribers])
