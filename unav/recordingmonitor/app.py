# -*- coding: utf-8 -*-

import blinker
import logging

from .config import Config
from .version import __title__
from .version import __release__

from .worker import ScheduledWorker
from .web import OurFlask
from .db import DB

log = logging.getLogger(__name__)


class Application:

	def __init__(self, config_path=None):

		# logging will be configured in Cfg constructor
		self.config = Config(config_path)

		log.info('Starting %s [%s]', __title__, __release__)

		self.web = OurFlask(self.config)
		self.web.a = self
		log.info('* WEB SERVER ready')

		DB.init_app(self.web)
		self.db = DB

		# create all tables
		DB.create_all(app=self.web)
		log.info('* DB ready')

		self.scheduler = ScheduledWorker(self.config)
		log.info('* SCHEDULER ready')

		blinker.signal('app.initialized').send(self)
		log.info('Entire application initialized')

	def run(self):
		self.scheduler.run()
		self.web.run()
