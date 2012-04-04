# -*- coding: utf-8 -*-
"""
    flask_encryptedsession.encryptedsession
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements cookie based sessions based on Werkzeug's encrypted cookie
    system.

    :license: BSD, see LICENSE for more details.
"""
from flask.sessions import SessionMixin, SessionInterface

from flask_encryptedsession.encryptedcookie import EncryptedCookie


class EncryptedCookieSession(EncryptedCookie, SessionMixin):
    """Expands the session with support for switching between permanent
    and non-permanent sessions.
    """


class EncryptedCookieSessionInterface(SessionInterface):
    """The cookie session interface that uses the Werkzeug encryptedcookie
    as client side session backend.
    """
    session_class = EncryptedCookieSession

    def open_session(self, app, request):
        keys_location = app.config.get('SESSION_ENCRYPTION_KEYS_LOCATION')
        if keys_location is not None:
            return self.session_class.load_cookie(request,
                                                  app.session_cookie_name,
                                                  keys_location=keys_location)

    def save_session(self, app, session, response):
        expires = self.get_expiration_time(app, session)
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        if session.modified and not session:
            response.delete_cookie(app.session_cookie_name, path=path,
                                   domain=domain)
        else:
            session.save_cookie(response, app.session_cookie_name, path=path,
                                expires=expires, httponly=httponly,
                                secure=secure, domain=domain)
