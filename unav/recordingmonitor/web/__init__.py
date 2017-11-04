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
		super().__init__(__name__, static_folder=None)

		root = cwd()
		self.root_path = root
		self.config.root_path = root

		log.debug('Flask root path: [%s]', self.config.root_path)

		config.apply_defaults('FLASK', self.config)
		self.config = config['FLASK']

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
