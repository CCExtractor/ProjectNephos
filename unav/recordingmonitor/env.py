# -*- coding: utf-8 -*-

'''
DO NOT mv (move) THIS FILE ACROSS DIRECTORIES

MUST BE IN THE ROOT DIRECTORY
'''

import os


_pkgroot = os.path.dirname(os.path.abspath(__file__))


def cwd():
	'''
	Current working directory. Where the script was started from

	:returns: Path
	:rtype: str
	'''
	return os.getcwd()


def package_root():
	'''
	The root of the package. In most cases the
	`site-content/unav/recordingmonitor` folder

	:returns: Path
	:rtype: str
	'''
	return _pkgroot
