# -*- coding: utf-8 -*-

import logging

from flask import Flask
from .api import api_blueprint
from ..env import cwd

log = logging.getLogger(__name__)


class OurFlask(Flask):
	def __init__(self, config):
		super().__init__(__name__)

		root = cwd()
		self.root_path = root
		self.config.root_path = root

		log.debug('Flask root path: [%s]', self.config.root_path)

		config.apply_defaults('FLASK', self.config)
		self.config = config['FLASK']

		self.register_blueprint(api_blueprint, url_prefix='/api/v0')
