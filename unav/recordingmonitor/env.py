# -*- coding: utf-8 -*-

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
	The root of the package. In most cases - `site-content` folder

	:returns: Path
	:rtype: str
	'''
	return _pkgroot
