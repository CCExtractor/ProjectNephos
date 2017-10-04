# -*- coding: utf-8 -*-

from functools import wraps

from flask_restful import marshal
from flask_restful.utils import unpack


class marshal_nullable_with:
	"""
	TODO: provide a PULL REQUEST
	A decorator that apply marshalling to the return values of your methods.

	It is a copy of decorator from flask_restful
	https://github.com/flask-restful/flask-restful/blob/master/flask_restful/__init__.py#L650
	"""
	def __init__(self, fields, envelope=None):
		self.fields = fields
		self.envelope = envelope

	def _get_none(self):
		if self.envelope:
			return {self.envelope: None}

		return None

	def __call__(self, f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			resp = f(*args, **kwargs)
			if isinstance(resp, tuple):
				data, code, headers = unpack(resp)
				if data is None:
					return self._get_none(), code, headers

				return marshal(data, self.fields, self.envelope), code, headers
			else:
				if resp is None:
					return self._get_none()

				return marshal(resp, self.fields, self.envelope)
		return wrapper
