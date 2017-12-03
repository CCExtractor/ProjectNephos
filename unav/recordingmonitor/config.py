# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.config

import yaml
import pydash as _
from sqlalchemy.engine.url import URL

from .env import cwd

log = logging.getLogger(__name__)


class Config:
	'''
	Configuration loading

	A private class, provides access to config of the application.

	Configuration options priority
	------------------------------

	Options could be loaded from many sources: env, config file, command line.
	Here is a list of used priorities (the first found value take precedence):

	1. environment variable
	2. configuration file
	3. default values

	'''

	__KEY_NOT_EXISTS = {'__KEY_NOT_EXISTS': -1231211}

	def __init__(self, config_path=None):

		self._version = None
		self._data = {}
		dd = self._data
		dd['FLASK'] = {}

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

		# LOAD ENVIRONMENT:
		eover = self._gather_from_environment()
		for stg, val in eover.items():
			_.set_(dd, stg, val)

		# set default values for settings which could not be
		# initalized declaratively:
		self.apply_defaults('log.version', 1)
		self.apply_defaults('capture.paths.jobsRoot', os.path.join(cwd(), 'tmp'))

		# list of debugging options
		self.apply_defaults('maintenance.rmdir', True)
		self.apply_defaults('capture.rmdir', True)

		# ----------------------------------------------------------------------
		# CONFIGURE LOGGING:
		# ----------------------------------------------------------------------
		logging.config.dictConfig(dd['log'])

		self._reset_frozendebug()

		if self.get('FLASK.DEBUG'):
			self._test_logging()

		# move connection string to expected place
		dbconfig = self.get('db.connection')
		if dbconfig is not None:
			self.connection_string = dbconfig

		log.debug('main database: %s', self.connection_string)

	def get(self, key, default=None):
		return _.get(self._data, key, default=default)

	def __getitem__(self, key):
		try:
			return self._data[key]
		except KeyError:
			pass

		res = self.get(key, default=self.__KEY_NOT_EXISTS)

		if self.__KEY_NOT_EXISTS == res:
			raise KeyError(key)

		return res

	def apply_defaults(self, path, val):
		if path is None:
			path = ''

		try:
			subcfg = self[path]
		except KeyError:
			# key not found, create a new branch in config:
			subcfg = None

		if subcfg is None:
			_.set_(self._data, path, val)
		else:
			_.defaults_deep(subcfg, val)

	def _gather_from_environment(self):
		values = {}

		for name in os.environ:
			if name.startswith('RECORDINGMONITOR_'):
				path = name[len('RECORDINGMONITOR_'):]

				if path.startswith('FLASK_'):
					path = path.replace('FLASK_', 'FLASK.')
				else:
					# TODO: this works errorprone.. Example: log.disable_existing_loggers
					path = path.replace('_', '.')

				values[path] = os.environ[name]

		return values

	def _test_logging(self):
		log.info('TEST LOGGING')
		log.debug('debug')
		log.info('info')
		log.warn('warn')
		log.error('error')
		log.critical('critical')
		log.info('DONE, you should have one message per enabled severity')

	def _reset_frozendebug(self):
		'''
		disable FLASK DEBUG when the app is running in PyInstaller bundle.

		When the app is running inside the PyInstaller environment it doesn't
		make sense to reload app on changes in code (default Flask's behavior
		in DEBUG mode).
		'''
		if getattr(sys, 'frozen', False):
			# running in a bundle
			if _.get(self._data, 'FLASK.DEBUG', False):
				self._data['FLASK']['DEBUG'] = False
				log.warn('FLASK.DEBUG was disabled for frozen environment')

	# helpers
	@property
	def connection_string(self):
		cs = self.get('FLASK.SQLALCHEMY_DATABASE_URI')
		return cs

	@connection_string.setter
	def connection_string(self, value):
		if isinstance(value, dict):
			dburl = str(URL(**value))
		else:
			dburl = str(value)

		_.set_(self._data, 'FLASK.SQLALCHEMY_DATABASE_URI', dburl)


def _get_default_yaml():
	return '''---
capture:
  # IP TV address
  address: 127.0.0.1

  paths:
    # "./tmp" folder in current working directory is used
    # if explicit value is not set
    jobsRoot: null  # '/tmp'

web:
  host: 0.0.0.0
  port: 5000

maintenance:
  enabled: True
  jobsLimit: 10

  jobs:
    freeSpace:
      type: free_space
      interval: 30  # minutes
      minBytes: 104857600  # 100 Mb
      minPercent: 10

    channelOnAir:
      type: channel_on_air
      interval: 60  # minutes

FLASK:
  DEBUG: False
  JSON_AS_ASCII: False
  JSONIFY_PRETTYPRINT_REGULAR: False

  SQLALCHEMY_TRACK_MODIFICATIONS: False

scheduler:
  tz: utc
  jobsLimit: 20

notifications:
  emails:
    smtp:
      host: localhost
      port: null  # 465
      ssl: False  # True
      tls: False

      username: null
      password: null

    subject: 'Recording Monitor'
    from: recordingmonitor@unav.es
    to:
      - support@xirvik.com

jobs:
  templates:
    # Template for a 'demo' job:
    demo:
      type: scripttpl

      after:
        - echo "{message}"
        - cmd: date +%s
          out: PIPE

    capture:
      type: capture

      parameters:
        channel_ID:
          type: TypeChannelSelect
        ftp_host:
          type: str
          default: ftp.com
        ftp_user:
          type: str
          default: user
        ftp_password:
          type: str
          default: password

      main:
        out: stream.ts

      after:
        # - echo "{message}"
        # - cmd: cp stream2.ts /tmp/mon/{job_ID}.ts

        # send with FTP:
        - cmd: curl --silent --fail --show-error -T stream.ts ftp://{ftp_host} --user {ftp_user}:{ftp_password}

db:
  connection:
    drivername:  'sqlite'
    database:    'recordingmonitor.sqlite'

    # drivername:  'postgres'
    # host:        'db.sqlite'
    # port:        5432
    # database:    'recordingmonitor'
    # username:    'recordingmonitor'
    # password:    'recordingmonitor'

sentry:
  dsn: null

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
      level: NOTSET
    file:
      class: unav.recordingmonitor.logger.EnsureFolderFileHandler
      formatter: simple
      filename: log/recordingmonitor.log
      level: NOTSET
  root:
    level: NOTSET
    handlers:
    - console
    - file
  loggers:
    unav.recordingmonitor:
      level: NOTSET

    sqlalchemy:
      level: ERROR # INFO  # NOTSET
    werkzeug:
      level: NOTSET # ERROR
    flask:
      level: NOTSET # ERROR
...
'''  # noqa: E101
