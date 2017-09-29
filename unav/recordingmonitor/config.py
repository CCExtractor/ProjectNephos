# -*- coding: utf-8 -*-

import os
import logging
import logging.config

import yaml
import pydash as _

from .env import cwd

log = logging.getLogger(__name__)


class Cfg:
	"""
	Configuration loading

	A private class, provides access to config of the application.

	### Configuration options priority

	Options could be loaded from many sources: env, config file, command line.
	Here is a list of used priorities (the first found value take precedence):
	1. environment variable
	2. configuration file
	3. default values
	"""

	def __init__(self, flask_config, config_path=None):

		self._version = None
		self._data = {}
		dd = self._data
		dd['FLASK'] = flask_config

		_.merge(dd, yaml.load(_get_default_yaml()))

		if config_path is None:
			config_path = os.path.join(cwd(), 'recordingmonitor.yml')
			log.info('Load configuration from DEFAULT path: %s', config_path)
		else:
			log.info('Load configuration from path: %s', config_path)

		self._config_path = config_path

		try:
			with open(config_path, 'r') as stream:
				file_conf = yaml.load(stream)
				_.merge(dd, file_conf)
		except FileNotFoundError:
			log.debug('There is NO config file, continue using defaults and env')
			print('There is NO config file, continue using defaults and env')

		eover = self._gather_from_environment()
		for stg, val in eover.items():
			_.set_(dd, stg, val)

		_.defaults_deep(dd, {'log': {'version': 1}})

		# CONFIGURE LOGGING:
		logging.config.dictConfig(dd['log'])

		log.info('TEST LOGGING')
		log.debug('debug')
		log.info('info')
		log.warn('warn')
		log.error('error')
		log.critical('critical')
		log.info('DONE, you should have one message per enabled severity')

	def get(self, key, default=None):
		return _.get(self, key, default=default)

	def __getitem__(self, key):
		try:
			return super().__getitem__(key)
		except KeyError:
			pass

		res = self.get(key, default=self.__KEY_NOT_EXISTS)

		if self.__KEY_NOT_EXISTS == res:
			raise KeyError(key)

		return res

	def _gather_from_environment(self):
		values = {}

		for name in os.environ:
			if name.startswith('RECORDINGMONITOR_'):
				path = name[len('RECORDINGMONITOR_'):]

				if path.startswith('FLASK_'):
					path = path.replace('FLASK_', 'FLASK.')
				else:
					path = path.replace('_', '.')

				values[path] = os.environ[name]

		return values


def _get_default_yaml():
	return '''---
FLASK:
  DEBUG: False
  JSON_AS_ASCII: False
  JSONIFY_PRETTYPRINT_REGULAR: False

log:
  disable_existing_loggers: True
  formatters:
    simple:
      format: "%(asctime)s [%(name)s] [%(levelname)-8s] %(message)s"
    colored:
      "()": coloredlogs.ColoredFormatter
      format: "%(asctime)s [%(name)s] [%(levelname)-8s] %(message)s"
  handlers:
    console:
      class: logging.StreamHandler
      formatter: colored
      stream: ext://sys.stdout
      level: INFO
    file:
      class: logging.FileHandler
      formatter: simple
      filename: recordingmonitor.log
      level: INFO
  root:
    level: NOTSET
    handlers:
    - console
    - file
  loggers:
    unav.recordingmonitor:
      level: NOTSET

    pony.orm.sql:
      level: WARNING
    pony.orm:
      level: WARNING
...
'''  # noqa: E101
