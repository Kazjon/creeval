#!/usr/bin/env python

from distutils.core import setup

setup(
    name='CreEval',
    version='0.1dev',
    description='CreativityEvaluation',
    packages=['creeval',],
    package_dir={'creeval': 'src/creeval'},
    author='Kazjon',
    author_email='kazjon@me.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)