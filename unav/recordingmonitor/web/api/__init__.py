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
from .about import PingResource

log = getLogger(__name__)


api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


# BUG: IT DOES NOT WORK!!!!
# BUG: IT DOES NOT WORK!!!!
# BUG: IT DOES NOT WORK!!!!
# BUG: IT DOES NOT WORK!!!!
# BUG: IT DOES NOT WORK!!!!
# BUG: IT DOES NOT WORK!!!!
#@api_blueprint.errorhandler(Exception)
@api_blueprint.errorhandler(401)
# @api_blueprint.app_errorhandler(500)
def error_handler(exc):

	log.warn(exc)

	print('DBG')
	print('H' * 70)
	print('H' * 70)
	print('H' * 70)
	print('H' * 70)
	print('H' * 70)

	data = {'error': str(exc)}
	raw_res = {'data': data}

	# BUG: improve this handler!!!

	return jsonify(raw_res)


api.add_resource(JobsListResource,       '/jobs')
api.add_resource(JobsResource,           '/jobs/<string:ID>')
api.add_resource(ChannelsListResource,   '/channels')
api.add_resource(ChannelsResource,       '/channels/<string:ID>')
api.add_resource(ChannelsStatusResource, '/channels/<string:ID>/status')
api.add_resource(PingResource,           '/about/ping')
