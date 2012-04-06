# -*- coding: utf-8 -*-
"""
    flask_encryptedsession.tests.test_encryptedcookie
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests the encrypted cookie.

    :license: BSD, see LICENSE for more details.
"""
import os.path
import unittest

from werkzeug.testsuite import WerkzeugTestCase

from werkzeug.utils import parse_cookie
from werkzeug.wrappers import Request, Response

from flask_encryptedsession.encryptedcookie import EncryptedCookie


KEYS_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys')
KEYS_DIR_BADKEY = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys_badkey')
KEYS_DIR_NONEXISTENT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys_nonexistent')


class EncryptedCookieTestCase(WerkzeugTestCase):

    def test_basic_support(self):
        c = EncryptedCookie(crypter_or_keys_location=KEYS_DIR)
        assert c.new
        assert not c.modified
        assert not c.should_save
        c['x'] = 42
        assert c.modified
        assert c.should_save
        s = c.serialize()

        c2 = EncryptedCookie.unserialize(s, KEYS_DIR)
        assert c is not c2
        assert not c2.new
        assert not c2.modified
        assert not c2.should_save
        assert c2 == c

        c3 = EncryptedCookie.unserialize(s, KEYS_DIR_BADKEY)
        assert not c3.modified
        assert not c3.new
        assert c3 == {}

    def test_fail_to_read_keys(self):
        self.assert_raises(
            Exception, EncryptedCookie,
            crypter_or_keys_location=KEYS_DIR_NONEXISTENT)
        self.assert_raises(
            Exception, EncryptedCookie.unserialize, 'some string',
            KEYS_DIR_NONEXISTENT)

    def test_wrapper_support(self):
        req = Request.from_values()
        resp = Response()
        c = EncryptedCookie.load_cookie(req, crypter_or_keys_location=KEYS_DIR)
        assert c.new
        c['foo'] = 42
        assert c.crypter is not None
        c.save_cookie(resp)

        req = Request.from_values(headers={
            'Cookie':  'session="%s"' % parse_cookie(resp.headers['set-cookie'])['session']
        })
        c2 = EncryptedCookie.load_cookie(req, crypter_or_keys_location=KEYS_DIR)
        assert not c2.new
        assert c2 == c


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EncryptedCookieTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
