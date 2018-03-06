# -*- coding: utf-8 -*-

import uuid
import arrow

import sqlalchemy as sa

from .types import TypeUuid
# from .dbtypes import TypeJson


class MixinTimestamp:
	created = sa.Column(
		sa.DateTime, nullable=False, default=arrow.utcnow)
	updated = sa.Column(sa.DateTime, onupdate=arrow.utcnow)


class MixinIdInteger:
	ID = sa.Column(sa.Integer, primary_key=True)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)


class MixinIdGuid:
	ID = sa.Column(TypeUuid, primary_key=True, default=uuid.uuid4)

	def __repr__(self):
		return '<{cls} {ID}>'.format(
			cls=type(self).__name__,
			ID=self.ID,
		)
