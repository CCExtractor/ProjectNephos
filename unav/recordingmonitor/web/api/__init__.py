# -*- coding: utf-8 -*-

from flask import jsonify

from flask import Blueprint
from logging import getLogger
# from flask import json

from flask_restful import Api

from .jobs import JobsResource
from .jobs import JobsListResource
from .channels import ChannelsResource
from .channels import ChannelsListResource
from .channels import ChannelsStatusResource

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)

api.add_resource(JobsListResource,       '/jobs')
api.add_resource(JobsResource,           '/jobs/<string:ID>')
api.add_resource(ChannelsListResource,   '/channels')
api.add_resource(ChannelsResource,       '/channels/<string:ID>')
api.add_resource(ChannelsStatusResource, '/channels/<string:ID>/status')


log = getLogger(__name__)


@api_blueprint.errorhandler(Exception)
def error_handler(exc):

	log.warn(exc)

	data = {'error': str(exc)}
	raw_res = {'data': data}

	# BUG: improve this handler!!!

	return jsonify(raw_res)
