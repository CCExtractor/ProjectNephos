# -*- coding: utf-8 -*-

import logging
from flask import Blueprint
from flask import json

from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import marshal_with
from flask_restful import fields

import arrow

log = logging.getLogger(__name__)

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


# output
job_fields = {
	'id': fields.String,
	'name': fields.String,
	'date_from': fields.DateTime(dt_format='iso8601'),
	'date_trim': fields.DateTime(dt_format='iso8601'),
}


def to_datetime(string):
	if string is None:
		return string
	d = arrow.get(string)
	return d.datetime


def as_is(arg):
	return arg


class JobsListResource(Resource):

	# input
	parser = reqparse.RequestParser()
	parser.add_argument('name')
	parser.add_argument('date_from', type=to_datetime)
	parser.add_argument('date_trim', type=to_datetime)
	parser.add_argument('extra', type=as_is)
	parser.add_argument('template_name')

	@marshal_with(job_fields)
	def get(self):
		return [
			{'hello': 'world'}
		]

	# CREATE JOB
	@marshal_with(job_fields)
	def post(self):
		args = self.parser.parse_args()
		log.debug('job create, args: %s', args)


		return {
			'id': 100,
			'name': args.name,
			'date_from': args.date_from,
			'date_trim': args.date_trim,
			'template_name': args.template_name,
		}


api.add_resource(JobsListResource, '/jobs')


class JobsResource(Resource):

	@marshal_with(job_fields)
	def get(self, id):
		return {
			'id': id,
			'name': 'horse',
		}


api.add_resource(JobsResource, '/jobs/<int:id>')
