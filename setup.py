# -*- coding: utf-8 -*-
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='kat',
      version='0.0.0',
      description='A commandline access to kickass torrent',
      long_description=readme(),
      url='https://github.com/BenoitZugmeyer/kat/',
      author='Benoît Zugmeyer',
      author_email='bzugmeyer@gmail.com',
      license='Expat',
      packages=['kat'],
      install_requires=[
          'pyquery>=1.2.4',
          'requests>=2.2.1',
      ],
      entry_points={
          'console_scripts': ['kat=kat.__init__:cli'],
      },
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=True)
