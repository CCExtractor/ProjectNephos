# -*- coding: utf-8 -*-

'''
Check the free space on disk

..seealso::

	https://docs.python.org/3/library/shutil.html#shutil.disk_usage

'''

import shutil
import blinker


def start(app_config):
	config = {
		'path': app_config.get('capture.paths.base')
	}

	total, used, free = shutil.disk_usage(config['path'])

	blinker.signal('jobs.maintenance').send('free_space',
		path=config['path'],
		total=total,
		used=used,
		free=free,
	)
