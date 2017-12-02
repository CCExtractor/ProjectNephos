# -*- coding: utf-8 -*-

import blinker
import logging

from raven import Client as SentryClient

from .config import Config
from .version import __title__
from .version import __release__

from .worker import ScheduledWorker
from .web import OurFlask

# DBG
# from .jobs.templates.scripttpl import TemplatedScriptJob
# from .jobs.templates.capture import CaptureStreamJob


from .db import FlaskSQLAlchemy
from .models.base import Model

from .notifications.emails import EmailsNotifier

log = logging.getLogger(__name__)


class Application:

	def __init__(self, config_path=None):

		self._needcleanup = True

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

			self._connect_notifiers(self.config)

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
		except:  # noqa: E722
			if self.sentry:
				self.sentry.captureException()

			# MUST BE RE-THROWN!
			# if you don't want to re-raise the exception - don't use
			# bare EXCEPT instruction!

			raise

	def _connect_notifiers(self, app_config):

		notify_signal = blinker.signal('notifications')

		port = app_config.get('notifications.emails.smtp.port')
		if port:
			port = int(port)

		en = EmailsNotifier(
			smtp_host=app_config.get('notifications.emails.smtp.host'),
			smtp_port=port,
			smtp_ssl=app_config.get('notifications.emails.smtp.ssl'),
			smtp_tls=app_config.get('notifications.emails.smtp.tls'),

			username=app_config.get('notifications.emails.smtp.username'),
			password=app_config.get('notifications.emails.smtp.password'),

			email_subject=app_config.get('notifications.emails.subject'),
			email_from=app_config.get('notifications.emails.from'),
			email_to=app_config.get('notifications.emails.to'),
		)

		# filter senders: sender='unav.recordingmonitor.jobs.maintenance.free_space'
		#
		# notify_signal.connect(asdfasdf, sender='unav.recordingmonitor.jobs.maintenance.free_space', weak=False)
		notify_signal.connect(en.notify, weak=False)

	def run(self):
		try:
			self.scheduler.run()
			self.web.run()
		# except (KeyboardInterrupt, SystemExit):
		# 	# TODO: check, that this works!
		# 	log.info('Shutdown application')
		# 	self.scheduler.shutdown()
		# 	sys.exit()
		except:  # noqa: E722
			if self.sentry:
				self.sentry.captureException()

			# MUST BE RE-THROWN!
			# if you don't want to re-raise the exception - don't use
			# bare EXCEPT instruction!

			raise

		finally:
			log.info('Shutdown application')
			self.cleanup()

	def cleanup(self):
		if self._needcleanup:
			self.scheduler.shutdown()
			self._needcleanup = False
