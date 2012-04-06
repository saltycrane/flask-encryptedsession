# -*- coding: utf-8 -*-
"""
    flask_encryptedsession.tests.test_encryptedsession
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests the encrypted session.

    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

import os.path
import re
import unittest
from datetime import datetime

import flask
from flask.testsuite import FlaskTestCase
from werkzeug.http import parse_date

from flask_encryptedsession.encryptedsession import (
    EncryptedCookieSessionInterface)


KEYS_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys')
KEYS_DIR_BADKEY = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys_badkey')
KEYS_DIR_NONEXISTENT = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'testkeys_nonexistent')


class BasicFunctionalityTestCase(FlaskTestCase):
    def test_session(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)

        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'

        @app.route('/get')
        def get():
            return flask.session['value']

        c = app.test_client()
        self.assert_equal(c.post('/set', data={'value': '42'}).data, 'value set')
        self.assert_equal(c.get('/get').data, '42')

    def test_bad_key(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)

        @app.route('/set', methods=['POST'])
        def set():
            flask.session['value'] = flask.request.form['value']
            return 'value set'

        @app.route('/get')
        def get():
            return flask.session.get('value', 'value is not there')

        c = app.test_client()
        self.assert_equal(c.post('/set', data={'value': '42'}).data, 'value set')
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR_BADKEY)
        self.assert_equal(c.get('/get').data, 'value is not there')

    def test_session_using_server_name(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)
        app.config.update(
            SERVER_NAME='example.com'
        )

        @app.route('/')
        def index():
            flask.session['testing'] = 42
            return 'Hello World'
        rv = app.test_client().get('/', 'http://example.com/')
        self.assert_('domain=.example.com' in rv.headers['set-cookie'].lower())
        self.assert_('httponly' in rv.headers['set-cookie'].lower())

    def test_session_using_server_name_and_port(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)
        app.config.update(
            SERVER_NAME='example.com:8080'
        )

        @app.route('/')
        def index():
            flask.session['testing'] = 42
            return 'Hello World'
        rv = app.test_client().get('/', 'http://example.com:8080/')
        self.assert_('domain=.example.com' in rv.headers['set-cookie'].lower())
        self.assert_('httponly' in rv.headers['set-cookie'].lower())

    def test_session_using_application_root(self):
        class PrefixPathMiddleware(object):
            def __init__(self, app, prefix):
                self.app = app
                self.prefix = prefix

            def __call__(self, environ, start_response):
                environ['SCRIPT_NAME'] = self.prefix
                return self.app(environ, start_response)

        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)
        app.wsgi_app = PrefixPathMiddleware(app.wsgi_app, '/bar')
        app.config.update(
            APPLICATION_ROOT='/bar'
        )

        @app.route('/')
        def index():
            flask.session['testing'] = 42
            return 'Hello World'
        rv = app.test_client().get('/', 'http://example.com:8080/')
        self.assert_('path=/bar' in rv.headers['set-cookie'].lower())

    def test_session_using_session_settings(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)
        app.config.update(
            SERVER_NAME='www.example.com:8080',
            APPLICATION_ROOT='/test',
            SESSION_COOKIE_DOMAIN='.example.com',
            SESSION_COOKIE_HTTPONLY=False,
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_PATH='/'
        )

        @app.route('/')
        def index():
            flask.session['testing'] = 42
            return 'Hello World'
        rv = app.test_client().get('/', 'http://www.example.com:8080/test/')
        cookie = rv.headers['set-cookie'].lower()
        self.assert_('domain=.example.com' in cookie)
        self.assert_('path=/;' in cookie)
        self.assert_('secure' in cookie)
        self.assert_('httponly' not in cookie)

    def test_missing_session(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(
            KEYS_DIR_NONEXISTENT)

        def expect_exception(f, *args, **kwargs):
            try:
                f(*args, **kwargs)
            except RuntimeError, e:
                self.assert_(
                    e.args and
                    'EncryptedCookieSession is unavailable' in e.args[0])
            else:
                self.assert_(False, 'expected exception')
        with app.test_request_context():
            self.assert_(flask.session.get('missing_key') is None)
            expect_exception(flask.session.__setitem__, 'foo', 42)
            expect_exception(flask.session.pop, 'foo')

    def test_session_expiration(self):
        permanent = True
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)

        @app.route('/')
        def index():
            flask.session['test'] = 42
            flask.session.permanent = permanent
            return ''

        @app.route('/test')
        def test():
            return unicode(flask.session.permanent)

        client = app.test_client()
        rv = client.get('/')
        self.assert_('set-cookie' in rv.headers)
        match = re.search(r'\bexpires=([^;]+)', rv.headers['set-cookie'])
        expires = parse_date(match.group())
        expected = datetime.utcnow() + app.permanent_session_lifetime
        self.assert_equal(expires.year, expected.year)
        self.assert_equal(expires.month, expected.month)
        self.assert_equal(expires.day, expected.day)

        rv = client.get('/test')
        self.assert_equal(rv.data, 'True')

        permanent = False
        rv = app.test_client().get('/')
        self.assert_('set-cookie' in rv.headers)
        match = re.search(r'\bexpires=([^;]+)', rv.headers['set-cookie'])
        self.assert_(match is None)

    def test_flashes(self):
        app = flask.Flask(__name__)
        app.session_interface = EncryptedCookieSessionInterface(KEYS_DIR)

        with app.test_request_context():
            self.assert_(not flask.session.modified)
            flask.flash('Zap')
            flask.session.modified = False
            flask.flash('Zip')
            self.assert_(flask.session.modified)
            self.assert_equal(list(flask.get_flashed_messages()), ['Zap', 'Zip'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicFunctionalityTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
