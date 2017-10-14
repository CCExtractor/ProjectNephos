# -*- coding: utf-8 -*-

import arrow

from ..db import WEBDB
from ..db import MixinIdGuid
from ..db.types import TypeJson
# from ..db import TypeJson

from ..errors import ValidationError


class JobInfo(MixinIdGuid, WEBDB.Model):

	name = WEBDB.Column(WEBDB.String(1200))
	date_from = WEBDB.Column(WEBDB.DateTime)
	date_trim = WEBDB.Column(WEBDB.DateTime)
	template_name = WEBDB.Column(WEBDB.String(4800))
	job_params = WEBDB.Column(TypeJson)
	job_id = WEBDB.Column(WEBDB.String(96))

	DURATION_SEC_MAX = 8 * 60 * 60

	def __init__(self):
		super().__init__()

	def get_app(self):
		return WEBDB.get_app().a

	def _validate(self):
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

	def save(self):

		self._validate()

		if self.ID is None:
			WEBDB.session.add(self)
		WEBDB.session.commit()

		# create/recreate scheduler task:
		sc = self.get_app().scheduler

		sj = sc.job_add(
			job_info_id=self.ID,
			template_name=self.template_name,
			date_from=self.date_from,
			date_trim=self.date_trim,
			job_params=self.job_params,
		)

		self.job_id = sj.id
		WEBDB.session.commit()
