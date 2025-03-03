import logging
import tornado.web
import json
import traceback
from h9web.handler import BaseHandler


class BaseAPIHandler(BaseHandler):
    H9D_ERROR_STATUS_CODE = 500
    H9WEB_ERROR_STATUS_CODE = 400

    def initialize(self):
        super(BaseAPIHandler, self).initialize()

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def prepare(self):
        super(BaseAPIHandler, self).prepare()
        logging.warning(self.get_current_user())
        if not self.get_current_user():
            raise tornado.web.HTTPError(401)

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
                "status": "error",
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'tt': str(kwargs),
                    'traceback': lines,
                }
            }))
        else:
            self.return_error(status_code, status_code, self._reason)

    def return_success(self, response):
        self.write(json.dumps({
            "status": "success",
            "response": response
        }))

    def return_error(self, status_codes, code, message):
        self.set_status(status_codes)
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps({
            "status": "error",
            'error': {
                'code': code,
                'message': message,
            }
        }))

class APIHandler (BaseAPIHandler):
    def initialize(self, h9d_int):
        super(APIHandler, self).initialize()
        self.debug = self.settings.get('debug', False)
        self.h9d = h9d_int

    # async def get_h9d_connection(self):
    #     if APIHandler.h9d_connection_pool is None:
    #         APIHandler.h9d_connection_pool = Queue()
    #         for i in range(5):
    #             h9d_stream = H9msgStream(self.settings.get('h9d_address'), self.settings.get('h9d_port'))
    #             await h9d_stream.connect("h9web_cp")
    #             await APIHandler.h9d_connection_pool.put(h9d_stream)
    #     return await APIHandler.h9d_connection_pool.get()
    #
    # def return_h9d_connection(self, connection):
    #     APIHandler.h9d_connection_pool.put_nowait(connection)
    #
    # async def h9d_connection_send_msg_get_response(self, msg):
    #     h9d_connection = await self.get_h9d_connection()
    #     h9d_connection.writemsg(msg)
    #     try:
    #         msg = await h9d_connection.readmsg()
    #     except IncompleteReadError as e:
    #         logging.warning("Restoring h9d connection...")
    #         h9d_connection = H9msgStream(self.settings.get('h9d_address'), self.settings.get('h9d_port'))
    #         await h9d_connection.connect("h9web_cp")
    #         h9d_connection.writemsg(msg)
    #         msg = await h9d_connection.readmsg()
    #     self.return_h9d_connection(h9d_connection)
    #     return msg

