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


log = logging.getLogger(__name__)


# output
_job_fields = {
	'ID': fields.String,
	'name': fields.String,
	'date_from': fields.DateTime(dt_format='iso8601'),
	'date_trim': fields.DateTime(dt_format='iso8601'),
}


class JobsListResource(Resource):

	# input
	parser = reqparse.RequestParser()
	parser.add_argument('name')
	parser.add_argument('date_from', type=to_datetime)
	parser.add_argument('date_trim', type=to_datetime)
	parser.add_argument('template_name')
	parser.add_argument('job_params', type=to_dict)

	@marshal_with(_job_fields, envelope='data')
	def get(self):
		jjs = JobInfo.query.all()

		return jjs

	# CREATE JOB
	@marshal_with(_job_fields, envelope='data')
	def post(self):
		args = self.parser.parse_args()
		log.debug('job create, args: %s', args)

		ji = JobInfo()
		ji.name = args.name
		ji.date_from = args.date_from
		ji.date_trim = args.date_trim

		# DEBUG
		print('!' * 40)
		print('!' * 40)
		print('DEBUG')
		print('!' * 40)
		print('!' * 40)
		ji.date_from = arrow.now().shift(seconds=3).datetime
		ji.date_trim = arrow.now().shift(seconds=13).datetime

		ji.template_name = args.template_name
		ji.job_params = args.job_params

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
