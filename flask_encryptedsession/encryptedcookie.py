# -*- coding: utf-8 -*-
r"""
    flask_encryptedsession.encryptedcookie
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements an encrypted cookie using the keyczar libary.

    Create keyczar keys
    ===================

        $ mkdir -p /tmp/keys
        $ keyczart create --location=/tmp/keys --purpose=crypt
        $ keyczart addkey --location=/tmp/keys --status=primary

    Example usage
    =============

    >>> from flask_encryptedsession.encryptedcookie import EncryptedCookie
    >>> x = EncryptedCookie({"foo": 42, "baz": (1, 2, 3)}, "/tmp/keys")

    Dumping into a string so that one can store it in a cookie:

    >>> value = x.serialize()

    Loading from that string again:

    >>> x = EncryptedCookie.unserialize(value, "/tmp/keys")
    >>> x["baz"]
    (1, 2, 3)

    If a bad key is provided, the unserialize method will fail silently and
    return a new empty `EncryptedCookie` object.

    Application Integration
    =======================

    If you are using the werkzeug request objects you could integrate the
    encrypted cookie into your application like this::

        from werkzeug.utils import cached_property
        from werkzeug.wrappers import BaseRequest
        from flask_encryptedsession.encryptedcookie import EncryptedCookie

        # generate keyczar keys and specify the keys directory here
        KEYS_DIR = '/tmp/keys'

        class Request(BaseRequest):

            @cached_property
            def client_session(self):
                data = self.cookies.get('session_data')
                if not data:
                    return EncryptedCookie(keys_location=KEYS_DIR)
                return EncryptedCookie.unserialize(data, KEYS_DIR)

        def application(environ, start_response):
            request = Request(environ, start_response)

            # get a response object here
            response = ...

            if request.client_session.should_save:
                session_data = request.client_session.serialize()
                response.set_cookie('session_data', session_data,
                                    httponly=True)
            return response(environ, start_response)

    A less verbose integration can be achieved by using shorthand methods::

        class Request(BaseRequest):

            @cached_property
            def client_session(self):
                return EncryptedCookie.load_cookie(self, keys_location=KEYS_DIR)

        def application(environ, start_response):
            request = Request(environ, start_response)

            # get a response object here
            response = ...

            request.client_session.save_cookie(response)
            return response(environ, start_response)

    :license: BSD, see LICENSE for more details.
"""
from time import time

from keyczar import keyczar
from werkzeug._internal import _date_to_unix
from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.contrib.sessions import ModificationTrackingDict


class UnquoteError(Exception):
    """Internal exception used to signal failures on quoting."""


class EncryptedCookie(SecureCookie):
    """Represents an encrypted cookie.

    Example usage:

    >>> x = EncryptedCookie({"foo": 42, "baz": (1, 2, 3)}, "/tmp/keys")
    >>> x["foo"]
    42
    >>> x["baz"]
    (1, 2, 3)
    >>> x["blafasel"] = 23
    >>> x.should_save
    True

    :param data: the initial data.  Either a dict, list of tuples or `None`.
    :param keys_location: the directory containing the keyczar keys.
                       If not set `None` or not specified
                       it has to be set before :meth:`serialize` is called.
    :param new: The initial value of the `new` flag.
    """

    def __init__(self, data=None, crypter_or_keys_location=None, new=True):
        ModificationTrackingDict.__init__(self, data or ())
        self.crypter = self._get_crypter(crypter_or_keys_location)
        self.new = new

    @staticmethod
    def _get_crypter(crypter_or_keys_location):
        """
        :param crypter_or_keys_location: may be None, a string, or a
            keyczar.Crypter instance.
        """
        if isinstance(crypter_or_keys_location, basestring):
            return keyczar.Crypter.Read(crypter_or_keys_location)
        return crypter_or_keys_location

    def serialize(self, expires=None):
        """Serialize the cookie into a string and encrypt.

        If expires is provided, the session will be automatically invalidated
        after expiration when you unseralize it. This provides better
        protection against session cookie theft.

        :param expires: an optional expiration date for the cookie (a
                        :class:`datetime.datetime` object)
        """
        if expires:
            self['_expires'] = _date_to_unix(expires)
        result = self.serialization_method.dumps(dict(self))
        return self.crypter.Encrypt(result)

    @classmethod
    def unserialize(cls, string, crypter_or_keys_location):
        """Decrypt and load the cookie from a serialized string.

        :param string: the cookie value to decrypt and deserialize.
        :param crypter_or_keys_location: the Crypter instance or the location
            of the keyczar keys
        :return: a new :class:`EncryptedCookie`.
        """
        if isinstance(string, unicode):
            string = string.encode('utf-8', 'replace')

        crypter = cls._get_crypter(crypter_or_keys_location)
        try:
            data = crypter.Decrypt(string)
        except:
            # if decryption fails, return new empty EncryptedCookie object
            items = ()
        else:
            items = cls.serialization_method.loads(data)
            # check if cookie is expired
            if '_expires' in items:
                if time() > items['_expires']:
                    items = ()
                else:
                    del items['_expires']

        return cls(items, crypter, False)

    @classmethod
    def load_cookie(cls, request, key='session', crypter_or_keys_location=None):
        """Loads a :class:`EncryptedCookie` from a cookie in request. If the
        cookie is not set, a new :class:`EncryptedCookie` instance is
        returned.

        :param request: a request object that has a `cookies` attribute
                        which is a dict of all cookie values.
        :param key: the name of the cookie.
        :param crypter_or_keys_location: the Crypter instance or the location
                           of the keyczar keys.
                           Always provide the value even though it has
                           no default!
        """
        data = request.cookies.get(key)
        if not data:
            return cls(crypter_or_keys_location=crypter_or_keys_location)
        return cls.unserialize(data, crypter_or_keys_location)
