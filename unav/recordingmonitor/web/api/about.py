# -*- coding: utf-8 -*-

import os
import logging

from flask_restful import Resource
from flask_restful import marshal_with
from flask_restful import fields


log = logging.getLogger(__name__)


# output
_pid_fields = {
	'pid':        fields.Integer,
}


class PingResource(Resource):

	@marshal_with({}, envelope='data')
	def get(self):
		return True


class GetPidResource(Resource):

	@marshal_with(_pid_fields, envelope='data')
	def get(self):
		pid = os.getpid()
		return {
			'pid': pid,
		}
