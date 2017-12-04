# -*- coding: utf-8 -*-

import logging

from flask_restful import Resource
from flask_restful import marshal_with


log = logging.getLogger(__name__)


class PingResource(Resource):

	@marshal_with({}, envelope='data')
	def get(self):
		return True
