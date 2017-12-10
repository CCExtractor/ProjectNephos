# -*- coding: utf-8 -*-

import os
from setuptools import setup
from setuptools import find_packages

VERSION = (0, 2, 0)
VERSION_SUFFIX = 'dev.1'
VERSION_SUFFIX = ''

VERSION_STRING = '.'.join([str(x) for x in VERSION[0:3]])
RELEASE_STRING = VERSION_STRING + VERSION_SUFFIX

__title__ = 'unav-recordingmonitor'
__description__ = 'RecordingMonitor - Recording monitor'
__copyright__ = '2016-2017 © Xirvik Python Team'
__author__ = 'Xirvik Python Team'
__license__ = 'private'
__version__ = VERSION_STRING
__release__ = RELEASE_STRING
# __build__ = os.env['TRAVIS_COMMIT']
# __commit__ = os.env['TRAVIS_BUILD_NUMBER']

cwd = os.path.dirname(__file__)


def read_all(file_name):
	fullname = os.path.join(cwd, file_name)
	with open(fullname, encoding='utf-8') as f:
		return f.read()


def rewrite_version():
	txt = '''# -*- coding: utf-8 -*-

# =====================================
# THIS FILE WAS GENERATED AUTOMATICALLY
# =====================================
#
# Probably, most of your changes in this file will be lost

__title__ = '{title}'
__description__ = '{description}'
__copyright__ = '{copyright}'
__author__ = '{author}'
__license__ = '{license}'
__version__ = '{version}'
__release__ = '{release}'
'''.format(
		title=__title__,
		description=__description__,
		copyright=__copyright__,
		author=__author__,
		license=__license__,
		version=__version__,
		release=__release__,
	)
	outname = os.path.join('unav', 'recordingmonitor', 'version.py')

	with open(outname, 'w', encoding='utf-8') as out:
		out.write(txt)


def gather_client_ui():
	files = []
	# taken from
	# https://github.com/stub42/pytz/blob/master/src/setup.py#L16
	# TODO: gh #8 - handle paths!
	for dirpath, dirnames, filenames in os.walk(os.path.join('client', 'dist')):
		# remove the 'pytz' part of the path
		# basepath = dirpath.split(os.path.sep, 1)[1]
		basepath = dirpath  # dirpath.split(os.path.sep, 1)[1]
		files.extend([
			os.path.join(basepath, filename) for filename in filenames
		])
	return files


rewrite_version()

# still no success with packaging this shit. Really annoying python setuptools..
# TODO: gh #7
package_data = {
	# TODO: gh #8 - handle paths!
	'unav.recordingmonitor.web.ui': gather_client_ui(),
}

# print('J' * 50)
# print('J' * 50)
# import json
# print(json.dumps(package_data, indent=4))
# print('J' * 50)
# print('J' * 50)

setup(
	name=__title__,
	version=__release__,
	url='https://github.com/XirvikMadrid/RecordingMonitor',
	# bugtrack_url='https://github.com/XirvikMadrid/RecordingMonitor/issues',
	license=__license__,
	# copyright=__copyright__,
	author=__author__,
	author_email='carlos@ccextractor.org',
	description=__description__,
	long_description=read_all('README.md'),
	keywords='network',
	packages=find_packages(
		include=['unav', 'unav.recordingmonitor', 'unav.recordingmonitor.*'],
		exclude=['*_test*'],
	),
	package_data=package_data,
	include_package_data=True,
	zip_safe=True,

	platforms='any',
	classifiers=[
		# 'Development Status :: 1 - Planning',
		# 'Development Status :: 2 - Pre-Alpha',
		# 'Development Status :: 3 - Alpha',
		# 'Development Status :: 4 - Beta',
		# 'Development Status :: 5 - Production/Stable',
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Environment :: Other Environment',
		# 'License :: OSI Approved :: ISC License (ISCL)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: Implementation',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],
	test_suite='pytest',

	install_requires=[
		'PyYAML           == 3.12',
		'python-dotenv    == 0.7.1',
		'coloredlogs      == 7.3',
		'pydash           == 4.2.1',
		'arrow            >= 0.10.0,   < 0.10.99',

		'raven[flask]     >=6.3.0',
		'blinker          >= 1.4,      < 1.4.99',
		'APScheduler      == 3.4.0',
		'SQLAlchemy       >= 1.2.0b2,  < 1.2.99',
		'SQLAlchemy-Utils >= 0.32.21,  < 0.32.99',

		'flask            == 0.12.2',
		'Flask-SQLAlchemy >= 2.3.0,    < 2.3.99',
		'Jinja2           >= 2.10,     < 2.99',
		'flask-restful    >= 0.3.6,    < 0.3.99',
		#'flask-restplus   >= 0.10.1,   < 0.10.99',
		'flask-socketio   >= 2.7.0',

		'python-slugify   >= 1.2.4,    < 1.2.99',

		# 'simplejson       == 3.11.1',

		# 'httplib2         ==0.9.1',
		# 'requests        ==2.18.4',
		# 'enum34          ==1.1.6',
	],

	entry_points='''
[console_scripts]
	RecordingMonitor=unav.recordingmonitor:main
	'''
)
