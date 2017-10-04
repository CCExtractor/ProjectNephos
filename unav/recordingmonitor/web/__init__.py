# -*- coding: utf-8 -*-

import logging

from flask import Flask
from .api import api_blueprint

log = logging.getLogger(__name__)


class WebServer(Flask):
	def __init__(self, config):
		super().__init__(__name__)

		config.apply_defaults('FLASK', self.config)
		self.config = config['FLASK']

		self.register_blueprint(api_blueprint, url_prefix='/api/v0')
