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
	date_trim = sa.Column(sa.DateTime)
	template_name = sa.Column(sa.String(4800))
	job_params = sa.Column(TypeJson)
	job_id = sa.Column(sa.String(96))

	channel_ID = sa.Column(TypeUuid, ForeignKey('channel.ID'), nullable=True)

	DURATION_SEC_MIN = 5
	DURATION_SEC_MAX = 8 * 60 * 60

	# def __init__(self):
	# 	super().__init__()

	def validate(self):
		now = arrow.get()
		if self.date_from < now and self.date_trim < now:
			raise ValidationError('Cannot add a Job in the past')

		duration_sec = (self.date_trim - self.date_from).total_seconds()

		if duration_sec < self.DURATION_SEC_MIN:
			raise ValidationError('Job is too short: {}sec < {}sec'.format(
				duration_sec,
				self.DURATION_SEC_MIN
			))

		if duration_sec > self.DURATION_SEC_MAX:
			raise ValidationError('Job is too long: {}sec > {}sec'.format(
				duration_sec,
				self.DURATION_SEC_MAX
			))
