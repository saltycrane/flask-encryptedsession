# -*- coding: utf-8 -*-
"""
    flask_encryptedsession.encryptedsession
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements cookie based sessions based on Werkzeug's encrypted cookie
    system.

    :license: BSD, see LICENSE for more details.
"""
from flask.sessions import SessionMixin, SessionInterface
from keyczar import keyczar

from flask_encryptedsession.encryptedcookie import EncryptedCookie


class EncryptedCookieSession(EncryptedCookie, SessionMixin):
    """Expands the session with support for switching between permanent
    and non-permanent sessions.
    """


class NullSession(EncryptedCookieSession):
    """Class used to generate nicer error messages if sessions are not
    available.  Will still allow read-only access to the empty session
    but fail on setting.
    """

    def __init__(self, exc):
        self.exc = exc

    def _fail(self, *args, **kwargs):
        raise RuntimeError(
            'EncryptedCookieSession is unavailable because keyczar.Crypter '
            'failed to read the keys: %s: %s' % (
                str(self.exc.__class__.__name__), str(self.exc)))
    __setitem__ = __delitem__ = clear = pop = popitem = \
        update = setdefault = _fail
    del _fail


class EncryptedCookieSessionInterface(SessionInterface):
    """The cookie session interface that uses the Werkzeug encryptedcookie
    as client side session backend.
    """
    session_class = EncryptedCookieSession
    null_session_class = NullSession

    def __init__(self, keys_location):
        """
        :param keys_location: the directory containing the keyczar keys
        """
        try:
            self.crypter = keyczar.Crypter.Read(keys_location)
        except Exception, e:
            self.crypter = None
            self.crypter_exc = e

    def make_null_session(self, app):
        return self.null_session_class(self.crypter_exc)

    def open_session(self, app, request):
        if self.crypter is not None:
            return self.session_class.load_cookie(
                request, app.session_cookie_name,
                crypter_or_keys_location=self.crypter)

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
