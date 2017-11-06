# -*- coding: utf-8 -*-

import logging

from raven.contrib.flask import Sentry
from flask import Flask

try:
	from flask_cors import CORS
except ImportError:
	CORS = None

from ..env import cwd
from ..version import __release__

from .api import api_blueprint
from .ui import ui_blueprint

log = logging.getLogger(__name__)


class OurFlask(Flask):
	def __init__(self, config):

		# disable `static`-handler for the main application
		# we will use static in bluprints (where required)
		super().__init__(__name__, static_folder=None)

		root = cwd()
		self.root_path = root
		self.config.root_path = root

		log.debug('Flask root path: [%s]', self.config.root_path)

		config.apply_defaults('FLASK', self.config)
		self.config = config['FLASK']

		self.__host = str(config.get('web.host', '127.0.0.1'))
		self.__port = int(config.get('web.port', 5000))

		_sentry_dsn = self.config.get('sentry.dsn')
		if _sentry_dsn:
			self.sentry = Sentry(
				self,
				dsn=_sentry_dsn,
				release=__release__,

				logging=True,
				level=logging.ERROR,
			)

		if CORS and self.debug:
			CORS(api_blueprint)
			log.warn('(FLASK DEBUG MODE) CORS enabled for API')

		self.register_blueprint(api_blueprint, url_prefix='/api/v0')
		self.register_blueprint(ui_blueprint)
		log.debug('web-route handlers registered')

	def run(self):
		h = self.__host
		p = self.__port

		log.info('Starging web server on [%s:%s]', h, p)
		super().run(host=h, port=p)
