# -*- coding: utf-8 -*-

import blinker
import logging

from raven import Client as SentryClient

from .config import Config
from .version import __title__
from .version import __release__

from .worker import ScheduledWorker
from .web import OurFlask
# from .db import DB
# from .db import WEBDB

log = logging.getLogger(__name__)

# DEBUG
from .jobs.templates.scripttpl import TemplatedScriptJob


from .db import FlaskSQLAlchemy
from .models.base import Model


class Application:

	def __init__(self, config_path=None):
		# logging will be configured in Cfg constructor
		self.config = Config(config_path)

		self.sentry = None
		_sentry_dsn = self.config.get('sentry.dsn')
		if _sentry_dsn:
			log.info('Sentry\'s raven error-grabber connected for app release=%s', __release__)
			self.sentry = SentryClient(
				dsn=_sentry_dsn,
				release=__release__,
			)

		try:
			log.info('Starting %s [%s]', __title__, __release__)

			self.web = OurFlask(self.config)
			self.web.app = self
			log.info('* WEB SERVER ready')

			db = FlaskSQLAlchemy(model_class=Model)
			self.db = db
			self.web.db = db

			db.init_app(self.web)        # connect Flask and Flask-SqlAlchemy
			db.create_all(app=self.web)  # create DB schema
			log.info('* DB ready')

			self.scheduler = ScheduledWorker(self.config)
			log.info('* SCHEDULER ready')

			blinker.signal('app.initialized').send(self)
			log.info('Entire application initialized')
		except:
			if self.sentry:
				self.sentry.captureException()
			raise

	def run(self):
		try:
			self.scheduler.run()
			self.web.run()
		except:
			if self.sentry:
				self.sentry.captureException()
			raise
