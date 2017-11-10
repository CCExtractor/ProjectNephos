# -*- coding: utf-8 -*-

import os
import shutil
import logging

from ...db import get_session

from ...logger import SQLAlchemyHandler
from ...logger import ExtendExtraLogAdapter


log = logging.getLogger(__name__)


def get_adapted_logger(job, db_session):
	joblog = logging.getLogger(job.full_classname)
	joblog.setLevel(logging.NOTSET)

	la = ExtendExtraLogAdapter(joblog, {
		'job_info_id': job.job_ID,
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

		# TODO: is it necessary??
		job_params = dict(job_params)

		# ----------------------------------------------------------------------
		# list of accessible fields of the base job class
		# ----------------------------------------------------------------------
		self.log = None
		self.session = None
		self.template_config = template_config
		self.job_params = job_params
		self.cwd = None
		self.job_ID = job_params['job_ID']

		self.date_from = job_params['job_date_from']
		self.date_trim = job_params['job_date_trim']
		self.duration_sec = (self.date_trim - self.date_from).total_seconds()

		log.debug('Job [%s] init runtime job instance', self.job_ID)

		# TODO: remove this params from job_params at all. Or make something...
		self.cwd = job_params.pop('job_dir')
		self.__connection_string = job_params.pop('connection_string')
		self.__cleanup_dir = job_params.pop('job_rmdir', True)

		log.debug('Job [%s] configured', self.job_ID)

	def __enter__(self):
		self.session = get_session(self.__connection_string)
		self.log = get_adapted_logger(self, self.session)

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

		return True

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
