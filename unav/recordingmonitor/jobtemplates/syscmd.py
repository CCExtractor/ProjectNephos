# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
from subprocess import Popen, PIPE

from ..logger import get_job_logger


class RunningProgram:
	def __init__(self):
		self.err = None
		self.out = None
		self.pid = None
		self.rc = None

	def __str__(self):
		return '<RunningProg, \n\terr={err}\n\tout={out}\n\tpid={pid}\n\trc={rc}\n'.format(
			err=self.err,
			out=self.out,
			pid=self.pid,
			rc=self.rc,
		)


def runping(job_info_id, job_params):
	log = get_job_logger(job_info_id, 'runping')

	print('ARGUMENT')
	print('-' * 50)
	print(job_params)
	print('-' * 50)

	cmd = ['ping', '127.0.0.1', '-c', '3']
	cmd = [str(i) for i in cmd]

	log.info('hello %s', 1, extra={'command': ' '.join(cmd)})

	prg = RunningProgram()
	pr = None

	try:
		pr = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
		(prg.out, prg.err) = pr.communicate()

		prg.out = prg.out.decode()
		prg.err = prg.err.decode()

		prg.ret = pr.returncode
		prg.pid = pr.pid
	except OSError as e:
		if e.errno == os.errno.ENOENT:
			# probably, executable not found..
			raise Exception('This executable was not found: [{0}]'.format(cmd[0]))
		else:
			# Something else went wrong while trying to run the command..
			raise

	if prg.err:
		prg.err = prg.err.strip()

	log.info('task stopped %s', prg)

	return prg
