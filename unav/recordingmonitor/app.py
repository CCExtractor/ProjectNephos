# -*- coding: utf-8 -*-

import blinker
import logging

from .config import Config
from .version import __title__
from .version import __release__

from .worker import ScheduledWorker
from .web import WebServer
from .models.db import DB

log = logging.getLogger(__name__)


class Application:

	def __init__(self, config_path=None):

		# logging will be configured in Cfg constructor
		self.config = Config(config_path)

		log.info('Starting %s [%s]', __title__, __release__)

		#log.info('Connecting to DB..')
		#self.db = DB.init(CONFIG['db'])

		self.tasks = ScheduledWorker(self.config)
		self.web = WebServer(self.config)

		DB.init_app(self.web)
		self.db = DB

		blinker.signal('app.initialized').send(self)
		log.info('Application initialized')

	def run(self):
		self.tasks.run()
		self.web.run()
