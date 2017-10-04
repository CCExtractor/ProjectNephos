# -*- coding: utf-8 -*-

import datetime
import logging

import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

from apscheduler.triggers.date import DateTrigger

# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.executors.pool import ProcessPoolExecutor

log = logging.getLogger(__name__)


class ScheduledWorker:
	def __init__(self, app_config):

		jobstores = {
			'default': SQLAlchemyJobStore(url=app_config.connection_string)
		}
		executors = {
			'default': ProcessPoolExecutor(5),
		}
		job_defaults = {
			'coalesce': False,
			'max_instances': 3
		}
		self._scheduler = BackgroundScheduler()

		self._scheduler.configure(
			jobstores=jobstores,
			executors=executors,
			job_defaults=job_defaults,
			timezone=pytz.utc,
		)

		# .. do something else here, maybe add jobs etc.

	def run(self):

		self._scheduler.start()

	def list_job(self):
		'''
		List all known jobs

		Result contains:

		- id
		- name
		- next_run_time

		.. seealso::

			https://apscheduler.readthedocs.io/en/latest/modules/job.html#apscheduler.job.Job

		:returns: List of jobs
		:rtype: list<Job>
		'''
		return self._scheduler.get_jobs()

	def add_job(self):
		# add_job(
		# 	func,
		# 	trigger=None,
		# 	args=None,
		# 	kwargs=None,
		# 	id=None,
		# 	name=None,
		# 	misfire_grace_time=undefined,
		# 	coalesce=undefined,
		# 	max_instances=undefined,
		# 	next_run_time=undefined,
		# 	jobstore='default',
		# 	executor='default',
		# 	replace_existing=False,
		# 	**trigger_args
		# )

		dt = datetime.datetime.now() + datetime.timedelta(seconds=7)

		trig = DateTrigger(run_date=dt)

		self._scheduler.add_job(
			tastss,
			trigger=trig,
			name='asdf',
			coalesce=True,
			replace_existing=True,
		)
		return 0


import os
from subprocess import Popen, PIPE


def tastss():
	t = TaskStep()
	return t.run()


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


class TaskStep:
	def __init__(self):
		pass

	def run(self):
		cmd = ['ping', '127.0.0.1', '-c', '3']

		cmd = [str(i) for i in cmd]

		log.debug('run task %s', cmd)

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
