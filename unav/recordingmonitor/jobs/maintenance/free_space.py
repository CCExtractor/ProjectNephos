# -*- coding: utf-8 -*-

'''
Check the free space on disk

..seealso::

	https://docs.python.org/3/library/shutil.html#shutil.disk_usage

'''

import shutil

from ..result_processor import BaseJobResultProcessor


def start(app_config):
	config = {
		'path': app_config.get('capture.paths.jobsRoot')
	}

	total, used, free = shutil.disk_usage(config['path'])

	return {
		'kind': FreeSpaceJobResultProcessor.KIND,

		'data': {
			'path': config['path'],
			'used': used,
			'free': free,
			'total': total,
		}
	}


class FreeSpaceJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.maintenance.free_space'

	def __init__(self, app_config):
		super().__init__(app_config)

		self._min_bytes = app_config.get('maintenance.jobs.freeSpace.minBytes')
		self._min_percent = app_config.get('maintenance.jobs.freeSpace.minPercent')

	def handle_data(self, data):

		path = data.get('path')
		used = data.get('used')
		free = data.get('free')
		total = data.get('total')

		free_percent = free * 100.0 / total

		if (
			free < self._min_bytes or
			free_percent < self._min_percent
		):
			# it is a problem, notify
			self.notify_signal.send(
				self.KIND,
				notification_code='low_space',
				data={
					'path': path,
					'used': used,
					'free': free,
					'total': total,
					'free_percent': free_percent,
					'free_min': self._min_bytes,
					'free_min_percent': self._min_percent,
				},
			)

	# def handle_error(cls, exc, tb):
	# 	pass
