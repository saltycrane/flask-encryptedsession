
from setuptools import setup, find_packages


setup(
    name='Flask-EncryptedSession',
    version='0.2.0',
    url='http://github.com/saltycrane/flask-encryptedsession/',
    license='BSD',
    author='Eliot',
    author_email='saltycrane@gmail.com',
    description='Flask encrypted cookie session',
    packages=find_packages(),
    package_data={'flask_encryptedsession.tests': ['testkeys/*']},
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'pyasn1>=0.1.2',
        'PyCrypto>=2.5',
        'python-keyczar>=0.71b',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='flask_encryptedsession.tests.suite'
)
