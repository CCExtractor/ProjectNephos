# -*- coding: utf-8 -*-

from logging import getLogger

import blinker
import pydash

log = getLogger(__name__)


class BaseJobResultProcessor:

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.common'

	notify_signal = blinker.signal('notifications')

	def __init__(self, app_config):
		pass

	def handle_event(self, res, exc, tb_str):

		if exc:
			self.handle_error(exc, tb_str)
		else:
			data = pydash.get(res, 'data')
			self.handle_data(data)

	def handle_data(self, data):
		'''
		This method MUST be overriden in the inherited classes

		The main purpose: analyze data (there are job's results) and
		provide appropriate information for notification system

		:param data: Job result
		:type data: *
		'''
		log.info(
			(
				'Default JobResultProcessor is used for '
				'job kind [%s] with data [%s]'
			),
			self.KIND,
			data,
			extra={
				'data': data
			}
		)

		# self.notify_signal.send(
		# 	self.KIND,
		# 	notification_code='unknown_event',
		# 	data={
		# 		'message': 'Unknown event fired',
		# 	},
		# )

	def handle_error(self, exc, tb_str):
		'''
		This method will remains un-overridden in inherited classes.

		Main purpose: to forward the exception info (from job) to notification
		system

		:param exc: Job exception
		:type exc: Exception
		:param tb: Job exception traceback
		:type tb: Traceback
		'''
		log.info(
			'Job of kind [%s] ended and raised an exception [%s]',
			self.KIND,
			exc,
			exc_info=(type(exc), exc, exc.__traceback__),
			extra={
				'error': exc
			}
		)

		self.notify_signal.send(
			self.KIND,
			notification_code='job_error',
			data={
				'error': exc,
			}
		)
