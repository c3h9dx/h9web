import logging
import json

import tornado.web
from tornado.iostream import StreamClosedError
from h9web.api import BaseAPIHandler


class Event(BaseAPIHandler):
    STATS_EVENT = "stats"
    FRAME_EVENT = "frame"
    DEV_EVENT = "dev"

    event_id = 0
    subscribers = []

    def initialize(self):
        super(Event, self).initialize()
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('X-Accel-Buffering', 'no')
        self.set_header('Connection', 'keep-alive')
        self.run = True
        self.context = self.request.connection.context

    def convert_uptime(self, n):
        n = int(n)
        day = n // (24 * 3600)
        n = n % (24 * 3600)
        hour = n // 3600
        n %= 3600
        minutes = n // 60
        n %= 60
        seconds = n
        ret = ''
        if day:
            ret = ret + str(day) + ' days'
        if hour:
            ret = ret + str(hour) + ' hours '
        if minutes:
            ret = ret + str(minutes) + ' minutes'
        if not ret:
            ret = ret + str(seconds) + ' seconds'
        return ret

    async def publish_event(self, event, data):
        if self.isEventPassFilter(event):
            try:
                logging.debug('Event on_{} {!r}'.format(event, data))
                self.write('event: {}\n'.format(event))
                self.write('id: {}\n'.format(Event.event_id))
                self.write('data: {}\n\n'.format(json.dumps(data)))
                await self.flush()
            except StreamClosedError:
                self.run = False

    def isEventPassFilter(self, event):
        return len(self.event_filter) == 0 or event in self.event_filter

    # @tornado.web.authenticated
    async def get(self):
        self.event_filter = self.get_arguments("filter", False)

        Event.subscribers.append(self)

        logging.info('Connected event subscribers {}:{} filter={}'.format(*self.context.address[:2], self.event_filter))
        try:
            self.write('event: connection\n')
            self.write('id: {}\n'.format(Event.event_id))
            self.write('data: established\n\n')
            await self.flush()
        except StreamClosedError:
            self.run = False
        while self.run:
            await tornado.web.gen.sleep(60)

    def on_finish(self):
        logging.info('Disconnected event subscribers {}:{}'.format(*self.context.address[:2]))
        Event.subscribers.remove(self)

    @classmethod
    async def publish_to_all(cls, event, data):
        cls.event_id += 1
        if event == Event.FRAME_EVENT:
            frame = data
            frame["priority"] = 0 if frame["priority"] == "H" else 1
            await tornado.web.gen.multi([sub.publish_event(Event.FRAME_EVENT, frame) for sub in cls.subscribers])
        else:
            await tornado.web.gen.multi([sub.publish_event(event, data) for sub in cls.subscribers])
