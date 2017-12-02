# -*- coding: utf-8 -*-

import os
import shutil
import logging

import arrow

from ...db import get_session
from ...models.jobs import JobLaunch

from ...logger import SQLAlchemyHandler
from ...logger import ExtendExtraLogAdapter


log = logging.getLogger(__name__)


def get_adapted_logger(job, db_session):
	joblog = logging.getLogger(job.full_classname)
	joblog.setLevel(logging.NOTSET)

	la = ExtendExtraLogAdapter(joblog, {
		'job_info_ID': job.job_ID,
		'job_launch_ID': job.job_launch.ID,
		'job_template_name': job.classname,
		# 'command': None
	})

	h = SQLAlchemyHandler(db_session)
	joblog.addHandler(h)
	return la


class BaseJob:
	'''
	Base class for all available jobs

	Works in a separate process.
	'''
	@property
	def classname(self):
		return type(self).__name__

	@property
	def full_classname(self):
		t = type(self)
		return t.__module__ + '.' + t.__name__

	def __init__(self, template_config, job_params):

		_start_at = arrow.get()

		# TODO: is it necessary??
		job_params = dict(job_params)

		# ----------------------------------------------------------------------
		# list of accessible fields of the base job class
		# ----------------------------------------------------------------------
		self.log = None
		self.session = None
		self.template_config = template_config
		self.job_params = job_params
		self.jobs_root = None
		self.cwd = None
		self.job_launch = None
		self.job_ID = job_params['job_ID']

		self.duration_sec = job_params['job_main_duration_sec']
		self.date_from = _start_at
		self.date_trim = _start_at.shift(seconds=self.duration_sec)

		log.debug('Job [%s] init runtime job instance', self.job_ID)

		# TODO: remove this params from job_params at all. Or make something...
		self.jobs_root = job_params.pop('job_root_dir')
		self.__connection_string = job_params.pop('connection_string')
		self.__cleanup_dir = job_params.pop('job_rmdir', True)

		log.debug('Job [%s] configured', self.job_ID)

	def _gen_job_launch_dir_name(self):
		_subfld = self.date_from.format('YYYY-MM-DDTHHmmss.SSS')
		_dn = os.path.join(self.jobs_root, 'jobs', str(self.job_ID), _subfld)
		return _dn

	def __enter__(self):

		log.debug('Create DB session for job [%s]', self.job_ID)
		self.session = get_session(self.__connection_string)

		# 1 create job-launch
		log.info('Create JobLaunch in DB for job [%s]', self.job_ID)

		jl = JobLaunch()
		jl.job_info_ID = self.job_ID
		jl.date_from = self.date_from
		self.session.add(jl)
		self.session.commit()
		self.job_launch = jl

		# 2 configure DB-logger
		self.log = get_adapted_logger(self, self.session)

		# 3 create temporary dir
		self.cwd = self._gen_job_launch_dir_name()

		log.debug('Create dir for job [%s] [%s]', self.job_ID, self.cwd)
		os.makedirs(self.cwd, exist_ok=True)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):

		if self.__cleanup_dir:
			log.debug('Cleanup dir for job [%s] [%s]', self.job_ID, self.cwd)
			shutil.rmtree(self.cwd)

		if exc_val:
			self.log.error(
				'Job FAILED',
				extra={
					'command': str(self),
					'error': {
						'type': str(exc_type),
						'value': str(exc_val),
					},
				},
				exc_info=(exc_type, exc_val, exc_tb),
			)

		else:
			self.log.info('Job SUCCESS',
				extra={
					'command': str(self)
				}
			)

	def run(self):
		pass


class StarterFabric:

	def __init__(self, job_class):
		self._job_class = job_class

	def __call__(self, template_config, job_params):
		'''
		This will be called by apscheduler on it's own timetable
		'''
		rc = None

		with self._job_class(template_config, job_params) as job:
			job.config(template_config, job_params)
			log.debug('Job [%s] starting [%s]', job.job_ID, type(job))
			rc = job.run()
			log.debug('Job [%s] ended [%s]', job.job_ID, type(job))

		return rc
