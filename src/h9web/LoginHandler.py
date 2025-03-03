import logging
import tornado.web
import json
from h9web.api import BaseAPIHandler

class LoginHandler(BaseAPIHandler):
    def prepare(self):
        pass

    def post(self):
        logging.warning("Restoring h9d connection...")
        try:
            credentials = json.loads(self.request.body)
            logging.warning(credentials)
            password = credentials['password']
            user = credentials['user']
        except (KeyError, json.JSONDecodeError):
            raise tornado.web.HTTPError(400, reason='Invalid JSON')
        except ValueError:
            raise tornado.web.HTTPError(400, reason='Invalid frame parameters')

        if user == 'sq8kfh' and password == 'kfh': #TODO: do it little more secure:P
            self.set_signed_cookie(self.AUTH_COOKIE, user)
            self.redirect("/")
        else:
            self.clear_cookie(self.AUTH_COOKIE)
            self.return_error(400, 400, "Invalid credentials")

    def get(self):
        self.clear_cookie(self.AUTH_COOKIE)
        self.return_success(None)
