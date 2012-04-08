Flask-EncryptedSession is a replacement for the default Flask session. In
addition to signing, it encrypts the cookie using the keyczar_ library. It is
based on (and provides a similar interface to) Werkzeug's SecureCookie_ and
Flask's `SecureCookieSession and SecureCookieSessionInterface`_.

.. _keyczar: http://code.google.com/p/keyczar/
.. _SecureCookie: https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/contrib/securecookie.py
.. _SecureCookieSession and SecureCookieSessionInterface: https://github.com/mitsuhiko/flask/blob/master/flask/sessions.py

Install
=======
In addtion to Flask, Flask-EncryptedSession requires pyasn1, PyCrypto, and
python-keyczar.

::

    $ pip install http://keyczar.googlecode.com/files/python-keyczar-0.71b.tar.gz 
    $ pip install https://github.com/saltycrane/flask-encryptedsession/tarball/master 

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

Complete example
================

::

    from datetime import datetime

    from flask import Flask, session
    from flask_encryptedsession.encryptedsession import (
        EncryptedCookieSessionInterface)


    app = Flask(__name__)
    app.debug = True
    app.session_interface = EncryptedCookieSessionInterface("/tmp/keys")


    @app.route("/")
    def hello_world():
        now = str(datetime.now())
        last_visit = session.get('last_visit', 'Never')
        page = "Today's date: %s<br> Last visit: %s" % (now, last_visit)
        session['last_visit'] = now
        return page


    if __name__ == '__main__':
        app.run()

Run tests
=========

::

    $ git clone git@github.com:saltycrane/flask-encryptedsession.git 
    $ cd flask-encryptedsession 
    $ pip install http://keyczar.googlecode.com/files/python-keyczar-0.71b.tar.gz 
    $ pip install -e ./ 
    $ python setup.py test 
