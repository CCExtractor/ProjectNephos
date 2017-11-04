# -*- coding: utf-8 -*-

import logging

from flask import current_app

from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal_with
from flask_restful import fields

from ...models.tv import Channel

from ._utils import marshal_nullable_with
# from ._utils import to_datetime
# from ._utils import to_dict


log = logging.getLogger(__name__)


# output
_null_fields = {
}

_channel_fields = {
	'ID': fields.String,
	'name': fields.String,
	'name_short': fields.String,
	'ip_string': fields.String,
	'channel_status': fields.String(attribute='channel_status.status'),
}

# input
_parser = reqparse.RequestParser()
_parser.add_argument('name')
_parser.add_argument('name_short')
_parser.add_argument('ip_string')


class ChannelsListResource(Resource):

	@marshal_with(_channel_fields, envelope='data')
	def get(self):
		ch = Channel.query.all()
		return ch

	# CREATE CHANNEL
	@marshal_with(_channel_fields, envelope='data')
	def post(self):
		args = _parser.parse_args()
		log.debug('channel create, args: %s', args)

		entity = Channel(**args)

		# ji.validate()

		db = current_app.db
		db.session.add(entity)
		db.session.commit()

		return entity


class ChannelsResource(Resource):

	@marshal_nullable_with(_channel_fields, envelope='data')
	def get(self, ID):
		ch = Channel.query.get(ID)

		return ch

	@marshal_with(_channel_fields, envelope='data')
	def put(self, ID):
		# ch = Channel.query.get(ID)

		args = _parser.parse_args()
		# ch.validate()

		db = current_app.db
		db.session.query(Channel).filter_by(ID=ID).update(args)
		db.session.commit()
		ch = Channel.query.get(ID)

		return ch

	@marshal_nullable_with(_null_fields, envelope='data')
	def delete(self, ID):

		db = current_app.db
		ch = Channel.query.get(ID)
		db.session.delete(ch)
		db.session.commit()

		return None
