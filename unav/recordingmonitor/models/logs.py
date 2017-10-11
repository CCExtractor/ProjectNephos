# -*- coding: utf-8 -*-

# logging to sqlalchemy
# https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/logging/sqlalchemy_logger.html

import arrow
from sqlalchemy.sql import func

from ..db import DB
from ..db import MixinIdGuid2
from ..db.types import TypeJson
from ..db.types import TypeUuid


# def _now():
# 	return arrow.utcnow().datetime


class TaskLogRecord(MixinIdGuid2, DB.Model):
	__tablename__ = 'task_log_record'

	logger = DB.Column(DB.String)
	level = DB.Column(DB.String)
	trace = DB.Column(DB.String)
	message = DB.Column(DB.String)

	job_info_id = DB.Column(TypeUuid)
	job_template_name = DB.Column(DB.String)
	data = DB.Column(TypeJson)

	ts = DB.Column(DB.TIMESTAMP, default=func.now())

	def __init__(
		self,
		logger=None,
		level=None,
		trace=None,
		message=None,
		ts=None,
		job_info_id=None,
		job_template_name=None,
		data=None
	):
		self.logger = logger
		self.level = level
		self.trace = trace
		self.message = message
		self.ts = ts

		self.job_info_id = job_info_id
		self.job_template_name = job_template_name
		self.data = data

		if isinstance(self.ts, (int, float)):
			self.ts = arrow.get(self.ts).datetime

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return '<TaskLogRecord: {ts} - {msgCut}>'.format(
			ts=self.ts.isoformat(),
			msgCut=self.message[:50]
		)

	def save(self):
		s = DB.session
		s.add(self)
		s.commit()

	def find(self, filt):
		s = DB.session
		s.query(TaskLogRecord).all()
