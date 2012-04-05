Flask-EncryptedSession is a replacement for the default Flask session. In
addition to signing, it encrypts the cookie using the keyczar libary. It is
based on (and provides a similar interface to) Werkzeug's SecureCookie, Flask's
SecureCookieSession and SecureCookieSessionInterface.

Install
=======
In addtion to Flask, Flask-EncryptedSession requires pyasn1, PyCrypto, and
python-keyczar.
::
    $ pip install http://keyczar.googlecode.com/files/python-keyczar-0.71b.tar.gz
    $ pip install Flask-EncryptedSession

Run tests
=========

::

    $ python setup.py test

Create keyczar keys
===================

::

    $ mkdir -p /tmp/keys
    $ keyczart create --location=/tmp/keys --purpose=crypt
    $ keyczart addkey --location=/tmp/keys --status=primary

Configure Flask app
===================

::

    from flask import Flask
    from flask_encryptedsession.encryptedsession import (
        EncryptedCookieSessionInterface)

    app = Flask(__name__)
    app.session_interface = EncryptedCookieSessionInterface("/tmp/keys")
