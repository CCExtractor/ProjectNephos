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

	def handle_data(self, data):

		# TODO: take from config
		free_bottom_level = 100 * 1024 * 1024  # 100 Mb
		free_percent_bottom_level = 10

		path = data.get('path')
		used = data.get('used')
		free = data.get('free')
		total = data.get('total')

		free_percent = float(free) / total * 100.0

		if (
			free < free_bottom_level or
			free_percent < free_percent_bottom_level
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
					'free_bottom_level': free_bottom_level,
					'free_percent_bottom_level': free_percent_bottom_level,
				},
			)

	# def handle_error(cls, exc, tb):
	# 	pass
