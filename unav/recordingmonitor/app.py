# -*- coding: utf-8 -*-

from flask import Flask
import logging

from .config import Cfg
from .version import __title__
from .version import __release__

log = logging.getLogger(__name__)


class Application(Flask):

	def __init__(self, config_path=None):

		super().__init__(__name__)

		self._config_path = config_path

		# logging will be configured in Cfg constructor
		self.cfg = Cfg(self.config, self._config_path)

		log.info('preload')

		# logLoadConfigDict(CONFIG['log'])
		log.info('%s [%s] ready', __title__, __release__)

		log.info('Connecting to DB..')
		# DB.init(CONFIG['db'])
