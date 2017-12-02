# -*- coding: utf-8 -*-

import logging
import arrow

from flask import current_app

from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal_with
from flask_restful import fields

from ...models.jobs import JobInfo
from ._utils import marshal_nullable_with
from ._utils import to_datetime
from ._utils import to_dict
from ._utils import DateTimeWithUtc


log = logging.getLogger(__name__)


# output
_repeat_cron_fields = {
	'year':        fields.String,
	'month':       fields.String,
	'day':         fields.String,
	'week':        fields.String,
	'day_of_week': fields.String,
	'hour':        fields.String,
	'minute':      fields.String,
	'second':      fields.String,
	'date_trim':   DateTimeWithUtc,
}

_repeat_interval_fields = {
	'weeks':       fields.String,
	'days':        fields.String,
	'hours':       fields.String,
	'minutes':     fields.String,
	'seconds':     fields.String,
	'start_date':  fields.String,
	'date_trim':   DateTimeWithUtc,
}

_repeat_fields = {
	'cron': fields.Nested(_repeat_cron_fields, allow_null=True),
	'interval': fields.Nested(_repeat_interval_fields, allow_null=True),
}

_job_fields = {
	'ID': fields.String,
	'channel_ID': fields.String,
	'name': fields.String,
	'date_from': DateTimeWithUtc,
	'duration_sec': fields.Integer,
	'repeat': fields.Nested(_repeat_fields, allow_null=True)
}

# input
_parser = reqparse.RequestParser()
_parser.add_argument('name')
_parser.add_argument('date_from', type=to_datetime)
_parser.add_argument('duration_sec', type=int)
_parser.add_argument('template_name')
_parser.add_argument('job_params', type=to_dict)
_parser.add_argument('channel_ID')
_parser.add_argument('repeat', type=to_dict)


class JobsListResource(Resource):

	@marshal_nullable_with(_job_fields, envelope='data')
	def get(self):

		# TODO: handle URLs like these:
		#   * ?sort=&page=1&per_page=10
		#   * ?sort=&page=1&per_page=10&filter=asdf

		jjs = JobInfo.query.all()

		return jjs

	# CREATE JOB
	@marshal_nullable_with(_job_fields, envelope='data')
	def post(self):
		args = _parser.parse_args()
		log.debug('job create, args: %s', args)

		ji = JobInfo(**args)

		# DBG
		print('!' * 40)
		print('!' * 40)
		print('DBG')
		print('!' * 40)
		print('!' * 40)
		ji.date_from = arrow.now().shift(seconds=3).datetime
		ji.duration_sec = 10

		ji.validate()

		db = current_app.db
		sched = current_app.app.scheduler

		db.session.add(ji)
		# REQUIRED! only after commit ji will have a real ID
		db.session.commit()

		sj = sched.job_add(ji)

		ji.job_id = sj.id
		db.session.commit()

		return ji


class JobsResource(Resource):

	@marshal_nullable_with(_job_fields, envelope='data')
	def get(self, ID):
		# jj = JobInfo.query.filter_by(ID=ID).first()
		jj = JobInfo.query.get(ID)

		return jj
