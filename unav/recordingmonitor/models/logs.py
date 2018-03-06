# -*- coding: utf-8 -*-

# logging to sqlalchemy
# https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/logging/sqlalchemy_logger.html

import arrow
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey

#from ..db import DB
from .base import Model
from ..db.mixins import MixinIdGuid
from ..db.types import TypeJson
from ..db.types import TypeUuid


# def _now():
# 	return arrow.utcnow().datetime


class TaskLogRecord(MixinIdGuid, Model):

	__tablename__ = 'task_log_record'

	logger = sa.Column(sa.String)
	level = sa.Column(sa.String)
	trace = sa.Column(sa.String)
	message = sa.Column(sa.String)

	job_info_ID = sa.Column(TypeUuid, ForeignKey('job_info.ID'))
	job_launch_ID = sa.Column(TypeUuid, ForeignKey('job_info.ID'))
	job_template_name = sa.Column(sa.String)
	data = sa.Column(TypeJson)

	ts = sa.Column(sa.TIMESTAMP, default=func.now())

	def __init__(
		self,
		logger=None,
		level=None,
		trace=None,
		message=None,
		ts=None,
		job_info_ID=None,
		job_launch_ID=None,
		job_template_name=None,
		data=None
	):
		self.logger = logger
		self.level = level
		self.trace = trace
		self.message = message
		self.ts = ts

		self.job_info_ID = job_info_ID
		self.job_launch_ID = job_launch_ID
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
