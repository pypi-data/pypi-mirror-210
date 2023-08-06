import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


readme = read('README.rst')
changelog = read('CHANGELOG.rst')

setup(name='crsysapi',
      version='6.21.0.post1',
      description='Python interface to CryptoSys API',
      long_description=readme + '\n\n' + changelog,
      author='David Ireland',
      url='https://www.cryptosys.net/api.html',
      platforms=['Windows'],
      py_modules=['crsysapi'],
      license='See source code modules'
      )
