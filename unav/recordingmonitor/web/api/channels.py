# -*- coding: utf-8 -*-

import logging

from flask import current_app

from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal_with
from flask_restful import fields

from ...models.tv import Channel

from ._utils import marshal_nullable_with
from ._utils import DateTimeWithUtc


log = logging.getLogger(__name__)


# output
_channel_fields = {
	'ID': fields.String,
	'name': fields.String,
	'name_short': fields.String,
	'ip_string': fields.String,
	'channel_status': fields.String(attribute='channel_status.status'),

	'meta_teletext_page': fields.String,
	'meta_country_code': fields.String,
	'meta_language_code3': fields.String,
	'meta_timezone': fields.String,
	'meta_video_source': fields.String,
}

_channel_status_fields = {
	'channel_ID': fields.String,
	'status': fields.String,
	'error': fields.String,
	'ts': DateTimeWithUtc,
}

# input
_parser_channel = reqparse.RequestParser()
_parser_channel.add_argument('name')
_parser_channel.add_argument('name_short')
_parser_channel.add_argument('ip_string')
# channel meta
_parser_channel.add_argument('meta_teletext_page')
_parser_channel.add_argument('meta_country_code')
_parser_channel.add_argument('meta_language_code3')
_parser_channel.add_argument('meta_timezone')
_parser_channel.add_argument('meta_video_source')


class ChannelsListResource(Resource):

	@marshal_with(_channel_fields, envelope='data')
	def get(self):
		ch = Channel.query.all()
		return ch

	# CREATE CHANNEL
	@marshal_with(_channel_fields, envelope='data')
	def post(self):
		args = _parser_channel.parse_args()
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

		args = _parser_channel.parse_args()
		# ch.validate()

		db = current_app.db
		db.session.query(Channel).filter_by(ID=ID).update(args)
		db.session.commit()
		ch = Channel.query.get(ID)

		return ch

	@marshal_nullable_with({}, envelope='data')
	def delete(self, ID):

		db = current_app.db
		ch = Channel.query.get(ID)
		db.session.delete(ch)
		db.session.commit()

		return None


class ChannelsStatusResource(Resource):

	@marshal_nullable_with(_channel_status_fields, envelope='data')
	def get(self, ID):
		ch = Channel.query.get(ID)
		return ch.channel_status
