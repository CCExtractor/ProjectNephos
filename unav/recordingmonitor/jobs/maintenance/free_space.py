# -*- coding: utf-8 -*-

'''
Check the free space on disk

..seealso::

	https://docs.python.org/3/library/shutil.html#shutil.disk_usage

'''

import shutil
import blinker


def start(job_meta, job_params):
	# print(job_meta)
	# print('*' * 50)
	# res = os.statvfs('/')
	# print(res)

	print('*' * 50)
	total, used, free = shutil.disk_usage('/')

	print(total, used, free)
	print('*' * 50)
	blinker.signal('jobs.maintenance').send('free_space', )
