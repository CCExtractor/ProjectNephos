# -*- coding: utf-8 -*-


class _DictFormatEmpty(dict):
	def __missing__(self, key):
		# return '{' + key + '}'
		return ''


def format_with_emptydefault(string, data):
	'''
	Works exactly like str.format, but in addition ignores params, that
	doesn't exist in the provided `data` (default implementation will warn)

	:param string: String template
	:type string: str
	:param data: Template data
	:type data: dict
	:returns: Formatted string
	:rtype: str
	'''
	return string.format_map(_DictFormatEmpty(data))


def decode_and_superstrip(xx):
	'''
	Call xx.decode(), strip() result, and convert empty to None

	:param xx: Some value
	:type xx: *
	:returns: Decoded string or None
	:rtype: str or None
	'''
	if xx is None:
		return None

	s = xx.decode()
	if s:
		s = s.strip()
	if not s:
		s = None

	return s
