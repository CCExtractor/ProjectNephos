# -*- coding: utf-8 -*-

import uuid
import arrow

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy import MetaData
# from sqlalchemy import Column
# from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from .types import TypeUuid
# from .dbtypes import TypeJson


convention = {
	'ix': 'ix_%(table_name)s_%(column_0_label)s',
	'uq': 'uq_%(table_name)s_%(column_0_name)s',
	'ck': 'ck_%(table_name)s_%(constraint_name)s',
	'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
	'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)

WEBDB = SQLAlchemy(metadata=metadata)


class MixinTimestamp:
	created = WEBDB.Column(
		WEBDB.DateTime, nullable=False, default=arrow.utcnow)
	updated = WEBDB.Column(WEBDB.DateTime, onupdate=arrow.utcnow)


class MixinIdInteger:
	ID = WEBDB.Column(WEBDB.Integer, primary_key=True)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)


class MixinIdGuid:
	ID = WEBDB.Column(TypeUuid, primary_key=True, default=uuid.uuid4)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)


class __NotAFlaskDB:

	from sqlalchemy import Column
	from sqlalchemy import Integer
	from sqlalchemy import String
	from sqlalchemy import DateTime
	from sqlalchemy.types import TIMESTAMP

	Model = declarative_base()

	def __init__(self):
		self._engine = None
		self._model = None
		self._Session = None

	def init(self, uri):
		self._engine = create_engine(uri)
		self._model = self.Model

		# create session generator
		Session = sessionmaker()
		Session.configure(bind=self._engine)

		self._Session = Session

	def create_all(self):
		self._model.metadata.create_all(bind=self._engine)
		# return self._meta.create_all()

	@property
	def session(self):
		session = self._Session()
		return session


DB = __NotAFlaskDB()


class MixinIdGuid2:
	ID = DB.Column(TypeUuid, primary_key=True, default=uuid.uuid4)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)
