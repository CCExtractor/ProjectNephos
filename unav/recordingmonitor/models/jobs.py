# -*- coding: utf-8 -*-

import arrow
import sqlalchemy as sa

from .base import Model
from ..db.mixins import MixinIdGuid
from ..db.types import TypeJson
# from ..db import TypeJson

from ..errors import ValidationError


class JobInfo(MixinIdGuid, Model):

	__tablename__ = 'job_info'

	name = sa.Column(sa.String(1200))
	date_from = sa.Column(sa.DateTime)
	date_trim = sa.Column(sa.DateTime)
	template_name = sa.Column(sa.String(4800))
	job_params = sa.Column(TypeJson)
	job_id = sa.Column(sa.String(96))

	DURATION_SEC_MAX = 8 * 60 * 60

	def __init__(self):
		super().__init__()

	def validate(self):
		now = arrow.get()
		if self.date_from < now and self.date_trim < now:
			raise ValidationError('Cannot add a Job in the past')

		duration_sec = (self.date_trim - self.date_from).total_seconds()

		if duration_sec < 2:
			raise ValidationError('Job is too short')

		if duration_sec > self.DURATION_SEC_MAX:
			raise ValidationError('Job is too long: {}sec > {}sec'.format(
				duration_sec,
				self.DURATION_SEC_MAX
			))
