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

	def handle_event(self, res, exc, tb):

		if exc:
			self.handle_error(exc, tb)
		else:
			data = pydash.get(res, 'data')
			self.handle_data(data)

		# notify_signal = blinker.signal('notifications')
		# notify_signal.send(
		# 	cls,
		# 	x=1,
		# )

	def handle_data(self, data):
		'''
		This method MUST be overriden in the inherited classes

		The main purpose: analyze data (there are job's results) and
		provide appropriate information for notification system

		:param data: Job result
		:type data: *
		'''
		log.error(
			(
				'JobResultProcessor called for unknown '
				'job kind [%s] with data [%s]'
			),
			self.KIND,
			self.data,
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

	def handle_error(self, exc, tb):
		'''
		This method will remains un-overridden in inherited classes.

		Main purpose: to forward the exception info (from job) to notification
		system

		[description]
		:param exc: Job exception
		:type exc: Exception
		:param tb: Job exception traceback
		:type tb: Traceback
		'''
		log.info(
			'Job of kind [%s] ended with an exception [%s]',
			self.KIND,
			exc,
			exc_info=(type(exc), exc, tb),
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
