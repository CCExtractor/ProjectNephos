# -*- coding: utf-8 -*-

from ..db import DB
from ..db import IdGuidMixin
from ..db import TypeJson
# from ..db import TypeJson


class Job(IdGuidMixin, DB.Model):
	__tablename__ = 'job'
	name = DB.Column(DB.String(1200))
	date_from = DB.Column(DB.DateTime)
	date_trim = DB.Column(DB.DateTime)
	template_name = DB.Column(DB.String(4800))
	extra = DB.Column(TypeJson)
	scheduler_id = DB.Column(DB.String(96))

	def __init__(self):
		super().__init__()

	def get_app(self):
		return DB.get_app().a

	def save(self):

		if self.ID is None:
			DB.session.add(self)
		DB.session.commit()

		# create/recreate scheduler task:
		sc = self.get_app().scheduler

		sj = sc.job_add(
			jobname=self.ID,
			template_name=self.template_name,
			date_from=self.date_from,
			date_trim=self.date_trim,
		)

		self.scheduler_id = sj.id
		DB.session.commit()
