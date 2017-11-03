# -*- coding: utf-8 -*-

import logging

from raven.contrib.flask import Sentry
from flask import Flask

from .api import api_blueprint
from ..env import cwd
from ..version import __release__

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

		_sentry_dsn = self.config.get('sentry.dsn')
		if _sentry_dsn:
			self.sentry = Sentry(
				self,
				dsn=_sentry_dsn,
				release=__release__,

				logging=True,
				level=logging.ERROR,
			)

		self.register_blueprint(api_blueprint, url_prefix='/api/v0')
