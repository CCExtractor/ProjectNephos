# -*- coding: utf-8 -*-

import logging

from flask import current_app

from flask_restful import Resource
from flask_restful import reqparse
# from flask_restful import marshal_with
from flask_restful import fields

from ...models.jobs import JobInfo
from ...models.tv import Channel

from ._utils import marshal_nullable_with
from ._utils import to_arrow_datetime
from ._utils import to_dict
from ._utils import DateTimeWithUtc


log = logging.getLogger(__name__)


# output
_repeat_cron_fields = {
	'year':         fields.String,
	'month':        fields.String,
	'day':          fields.String,
	'week':         fields.String,
	'day_of_week':  fields.String,
	'hour':         fields.String,
	'minute':       fields.String,
	'second':       fields.String,
	'date_trim':    DateTimeWithUtc,
}

_repeat_interval_fields = {
	'weeks':        fields.String,
	'days':         fields.String,
	'hours':        fields.String,
	'minutes':      fields.String,
	'seconds':      fields.String,
	'date_trim':    DateTimeWithUtc,
}

_repeat_fields = {
	'cron': fields.Nested(_repeat_cron_fields, allow_null=True),
	'interval': fields.Nested(_repeat_interval_fields, allow_null=True),
}

_job_fields = {
	'ID':           fields.String,
	'name':         fields.String,
	'date_from':    DateTimeWithUtc,
	'duration_sec': fields.Integer,
	'timezone':     fields.String,
	'is_removed':   fields.Boolean,
	'repeat':       fields.Nested(_repeat_fields, allow_null=True),

	'channel_ID':   fields.String,
	'meta_teletext_page': fields.String,
	'meta_country_code': fields.String,
	'meta_language_code3': fields.String,
	'meta_timezone': fields.String,
	'meta_video_source': fields.String,
}

# input
_parser = reqparse.RequestParser()
_parser.add_argument('name')
_parser.add_argument('date_from', type=to_arrow_datetime)
_parser.add_argument('duration_sec', type=int)
_parser.add_argument('timezone')
_parser.add_argument('template_name')
_parser.add_argument('job_params', type=to_dict)
_parser.add_argument('repeat', type=to_dict)

_parser.add_argument('channel_ID')
_parser.add_argument('channel_name')
_parser.add_argument('meta_teletext_page')
_parser.add_argument('meta_country_code')
_parser.add_argument('meta_language_code3')
_parser.add_argument('meta_timezone')
_parser.add_argument('meta_video_source')


# BUG: refactor
# BUG: refactor
# BUG: refactor
# BUG: refactor
# BUG: refactor
from werkzeug.exceptions import HTTPException


class JobAlreadyDisabled(HTTPException):
	code = 409


class NotFoundError(HTTPException):
	code = 404


class _WithSchedulerAndDb:
	@property
	def app_scheduler(self):
		return current_app.app.scheduler

	@property
	def db(self):
		return current_app.db


class JobsListResource(_WithSchedulerAndDb, Resource):

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

		channel_name = args.pop('channel_name', None)
		channel_ID = args.get('channel_ID', None)
		if channel_ID is None:
			channel = Channel.query.filter_by(name=channel_name).first()
			if channel:
				channel_ID = channel.ID
				args['channel_ID'] = channel.ID
				log.debug('channel [%s] found by name [%s]', channel_ID, channel_name)
			else:
				log.warn('channel not found by name [%s]', channel_name)

		ji = JobInfo(**args)

		# DBG
		# print('!' * 40)
		# print('!' * 40)
		# print('DBG')
		# print('!' * 40)
		# print('!' * 40)
		# ji.date_from = arrow.now().shift(seconds=3)

		ji.validate()

		self.db.session.add(ji)
		# REQUIRED! only after commit ji will have a real ID
		self.db.session.commit()

		sj = self.app_scheduler.job_add(ji)

		ji.job_ID = sj.id
		self.db.session.commit()

		return ji


class JobsResource(_WithSchedulerAndDb, Resource):

	@marshal_nullable_with(_job_fields, envelope='data')
	def get(self, ID):
		# jj = JobInfo.query.filter_by(ID=ID).first()
		jj = JobInfo.query.get(ID)

		return jj

	@marshal_nullable_with({}, envelope='data')
	def delete(self, ID):

		ji = JobInfo.query.get(ID)
		if not ji:
			raise NotFoundError('Job not found')

		if ji.is_removed:
			raise JobAlreadyDisabled('Job already disabled')

		self.app_scheduler.job_remove(ji.job_ID)

		ji.job_ID = None
		ji.is_removed = True

		self.db.session.commit()

		return None
