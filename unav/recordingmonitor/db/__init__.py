# -*- coding: utf-8 -*-

import logging

from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemyOriginal
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.base import set_query_property

# import sqlalchemy as sa
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)

convention = {
	'ix': 'ix_%(table_name)s_%(column_0_label)s',
	'uq': 'uq_%(table_name)s_%(column_0_name)s',
	'ck': 'ck_%(table_name)s_%(constraint_name)s',
	'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
	'pk': 'pk_%(table_name)s',
}

metadata = MetaData(naming_convention=convention)


class FlaskSQLAlchemy(FlaskSQLAlchemyOriginal):
	"""
	Flask extension that integrates alchy with Flask-SQLAlchemy.
	"""
	def __init__(
		self,
		app=None,
		use_native_unicode=True,
		session_options=None,
		model_class=None,
	):
		self.Model = model_class

		super().__init__(
			app=app,
			use_native_unicode=use_native_unicode,
			session_options=session_options,
			metadata=metadata,
		)

	def make_declarative_base(self, model_class, metadata):
		"""Creates or extends the declarative base."""
		if self.Model is None:
			self.Model = super().make_declarative_base(self.Model, metadata)
		else:
			set_query_property(self.Model, self.session)
		return self.Model


def get_session(connection_string):
	connect_args = None
	if connection_string.startswith('sqlite'):
		connect_args = {'check_same_thread': False}

	engine = create_engine(
		connection_string,
		connect_args=connect_args
	)
	# model = self.Model

	# create session generator
	SessionClass = sessionmaker()
	SessionClass.configure(bind=engine)

	session = SessionClass()
	return session
