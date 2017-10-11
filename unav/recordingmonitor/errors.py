# -*- coding: utf-8 -*-


def getFullTypeName(obj):
	return '.'.join((obj.__module__, type(obj).__name__))


class BaseError(Exception):

	def __json__(self):
		return {
			"type": getFullTypeName(self),
			"message": str(self),
		}


class ValidationError(BaseError):
	def __init__(self, msg):
		super().__init__(msg)


class HandleJobError(BaseError):
	def __init__(self, msg, template_name):
		super().__init__(msg)

		self.template_name = template_name
