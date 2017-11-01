# -*- coding: utf-8 -*-

import blinker
import logging

from .config import Config
from .version import __title__
from .version import __release__

from .worker import ScheduledWorker
from .web import OurFlask
# from .db import DB
# from .db import WEBDB

log = logging.getLogger(__name__)

#DEBUG
from .jobs.templates.scripttpl import TemplatedScriptJob


from .db import FlaskSQLAlchemy
from .models.base import Model


class Application:

	def __init__(self, config_path=None):
		# logging will be configured in Cfg constructor
		self.config = Config(config_path)

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

		# WEBDB.init_app(self.web)
		# self.webdb = WEBDB

		# # create all tables
		# WEBDB.create_all(app=self.web)
		# log.info('* WEBDB ready')

		self.scheduler = ScheduledWorker(self.config)
		log.info('* SCHEDULER ready')

		blinker.signal('app.initialized').send(self)
		log.info('Entire application initialized')

	def run(self):
		self.scheduler.run()
		self.web.run()
