# -*- coding: utf-8 -*-

import uuid
# just a convenient way to import simplejson with fallback to python.json
from flask import json

from sqlalchemy.types import TypeDecorator, CHAR, VARCHAR, JSON
from sqlalchemy.dialects.postgresql import UUID as postgreUUID
from sqlalchemy.dialects.postgresql import JSON as postgreJSON


class TypeUuid(TypeDecorator):
	"""
	Platform-independent UUID type.

	Uses Postgresql's UUID type, otherwise uses
	CHAR(32), storing as stringified hex values.

	"""
	impl = CHAR

	def load_dialect_impl(self, dialect):
		if dialect.name == 'postgresql':
			return dialect.type_descriptor(postgreUUID())
		else:
			return dialect.type_descriptor(CHAR(32))

	def process_bind_param(self, value, dialect):
		if value is None:
			return value
		elif dialect.name == 'postgresql':
			return str(value)
		else:
			if not isinstance(value, uuid.UUID):
				return "%.32x" % uuid.UUID(value).int
			else:
				# hexstring
				return "%.32x" % value.int

	def process_result_value(self, value, dialect):
		if value is None:
			return value
		else:
			return uuid.UUID(value)


class TypeJson(TypeDecorator):
	"""
	Represents an immutable structure as a json-encoded string.

	Usage::

		JSON(255)

	"""

	impl = VARCHAR

	_supports_json = ['postgresql', 'mysql']

	def load_dialect_impl(self, dialect):
		if dialect.name == 'postgresql':
			return dialect.type_descriptor(JSON())  # postgreJSON())
		elif dialect.name == 'mysql':
			return dialect.type_descriptor(JSON())
		else:
			return dialect.type_descriptor(VARCHAR())

	def process_bind_param(self, value, dialect):
		if dialect.name not in self._supports_json:
			if value is not None:
				value = json.dumps(value)

		return value

	def process_result_value(self, value, dialect):
		if dialect.name not in self._supports_json:
			if value is not None:
				value = json.loads(value)
		return value
