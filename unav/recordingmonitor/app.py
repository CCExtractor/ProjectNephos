# -*- coding: utf-8 -*-

import logging

from .config import Config
from .version import __title__
from .version import __release__

from .tasks import TaskRunner
from .web import WebServer
#from .db import DB

log = logging.getLogger(__name__)


class Application:

	def __init__(self, config_path=None):

		# logging will be configured in Cfg constructor
		self.config = Config(config_path)

		log.info('Starting %s [%s]', __title__, __release__)

		#log.info('Connecting to DB..')
		#self.db = DB.init(CONFIG['db'])

		self.tasks = TaskRunner(self.config)
		self.web = WebServer(self.config)

	def run(self):

		self.tasks.add_job()

		self.tasks.run()
		self.web.run()


