#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import olympiad

setup(
        name='django-olympiad',
        version=olympiad.__version__,
        description='A reusable Django app for scraping, storing and aggregating Olympic medal counts.',
        author=olympiad.__author__,
        author_email=['bowersj@washpost.com', 'dan.hill@washpost.com'],
        url='https://github.com/wpmedia/django-olympiad',
        packages=[
            'olympiad'
        ],
        install_requires=[
            'beautifulsoup4',
            'requests',
            'Django>=1.4',
            'django-tastypie',
            'south'
        ],
        license=olympiad.__license__,
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'
        ],
)
