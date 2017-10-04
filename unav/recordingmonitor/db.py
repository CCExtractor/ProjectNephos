# -*- coding: utf-8 -*-

from flask import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from sqlalchemy.types import TypeDecorator, CHAR, VARCHAR, JSON
from sqlalchemy.dialects.postgresql import UUID as postgreUUID
from sqlalchemy.dialects.postgresql import JSON as postgreJSON


import uuid

convention = {
	'ix': 'ix_%(table_name)s_%(column_0_label)s',
	'uq': 'uq_%(table_name)s_%(column_0_name)s',
	'ck': 'ck_%(table_name)s_%(constraint_name)s',
	'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
	'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)

DB = SQLAlchemy(metadata=metadata)


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


# class TimestampMixin(object):
# 	created = db.Column(
# 		db.DateTime, nullable=False, default=datetime.utcnow)
# 	updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class IdIntegerMixin:
	ID = DB.Column(DB.Integer, primary_key=True)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)


class IdGuidMixin:
	ID = DB.Column(TypeUuid, primary_key=True, default=uuid.uuid4)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)
