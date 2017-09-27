# -*- coding: utf-8 -*-


def getFullTypeName(obj):
	return '.'.join((obj.__module__, type(obj).__name__))


class BaseError(Exception):

	def __json__(self):
		return {
			"type": getFullTypeName(self),
			"message": str(self),
		}
