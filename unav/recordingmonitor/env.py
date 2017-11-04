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
	print('^' * 80)
	print('^' * 80)
	print('DEBUG')
	print('package root', _pkgroot)
	print('^' * 80)
	print('^' * 80)

	return _pkgroot
