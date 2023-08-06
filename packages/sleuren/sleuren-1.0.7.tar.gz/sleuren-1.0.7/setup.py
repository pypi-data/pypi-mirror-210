#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.md')).read()
if sys.version.startswith('3.'):
    install_requires = ['psutil', 'netifaces', 'configparser', 'future', 'distro']
elif sys.version.startswith('2.7'):
    install_requires = ['psutil==5.6.7', 'netifaces', 'configparser==3.5.0', 'future']
else:
    install_requires = ['psutil', 'netifaces', 'configparser', 'future']


setuptools.setup(
    name='sleuren',
    version='1.0.7',
    description='Server monitoring agent',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/sleuren/agent',
    author='sleuren',
    author_email='hello@sleuren.com',
    maintainer='sleuren',
    maintainer_email='hello@sleuren.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
    ],
    keywords='sleuren monitoring agent',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'sleuren=sleuren.sleuren:main',
            'hello=sleuren.sleuren:hello',
        ],
    },
    data_files=[('share/doc/sleuren', [
        'sleuren.ini',
        'LICENSE',
        'README.md',
    ])],
)