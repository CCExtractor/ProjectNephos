# -*- coding: utf-8 -*-

import arrow
import sqlalchemy as sa
from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship

from .base import Model
from ..db.mixins import MixinIdGuid
from ..db.types import TypeJson
from ..db.types import TypeUuid

from ..errors import ValidationError


class JobInfo(MixinIdGuid, Model):

	__tablename__ = 'job_info'

	name = sa.Column(sa.String(1200))
	date_from = sa.Column(sa.DateTime)
	duration_sec = sa.Column(sa.Integer)
	template_name = sa.Column(sa.String(4800))
	job_params = sa.Column(TypeJson)
	job_id = sa.Column(sa.String(96))
	repeat = sa.Column(TypeJson)

	channel_ID = sa.Column(TypeUuid, ForeignKey('channel.ID'), nullable=True)

	DURATION_SEC_MIN = 5
	DURATION_SEC_MAX = 8 * 60 * 60

	# def __init__(self):
	# 	super().__init__()

	def validate(self):
		now = arrow.get()
		if self.date_from < now:
			raise ValidationError('Cannot add a Job in the past')

		if self.duration_sec < self.DURATION_SEC_MIN:
			raise ValidationError('Job is too short: {}sec < {}sec'.format(
				self.duration_sec,
				self.DURATION_SEC_MIN
			))

		if self.duration_sec > self.DURATION_SEC_MAX:
			raise ValidationError('Job is too long: {}sec > {}sec'.format(
				self.duration_sec,
				self.DURATION_SEC_MAX
			))
