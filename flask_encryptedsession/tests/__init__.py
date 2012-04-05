import unittest

from flask_encryptedsession.tests import (
    test_encryptedcookie, test_encryptedsession)


suite1 = test_encryptedcookie.suite()
suite2 = test_encryptedsession.suite()
suite = unittest.TestSuite([suite1, suite2])
