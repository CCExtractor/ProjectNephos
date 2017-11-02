# -*- coding: utf-8 -*-

'''
jobtemplates

This folder contains template-handlers for jobs.

.. warning::

	JOB will be run in separated processes!

'''

import os
import shutil
import logging

from ...db import get_session

from ...logger import SQLAlchemyHandler
from ...logger import ExtendExtraLogAdapter

log = logging.getLogger(__name__)
joblog = logging.getLogger('{0}.{1}'.format(__name__, 'job'))


def get_adapted_logger(db_session, job_info_id, job_template_name):
	la = ExtendExtraLogAdapter(joblog, {
		'job_info_id': job_info_id,
		'job_template_name': job_template_name,
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
	def template_name(self):
		return type(self).__name__

	def __init__(self):
		self.log = None
		self.session = None

	def __call__(self, template_config, job_params):

		job_id = job_params['job_id']
		log.debug('Job [%s] preparing', job_id)

		# TODO: remove job_dir from meta
		job_dir = job_params['job_dir']
		job_rmdir = job_params.get('job_rmdir', True)

		# TODO: remove connection_string from meta
		# IMPORTANT: it POPS connection string!
		connection_string = job_params.pop('connection_string')

		self.session = get_session(connection_string)
		self.log = get_adapted_logger(self.session, job_id, self.template_name)

		log.debug('Job [%s] Dir: [%s]', job_id, job_dir)
		os.makedirs(job_dir, exist_ok=True)

		self.log.debug('Job [%s] starting [%s]', job_id, type(self))
		res = self.run(template_config, job_params)
		self.log.debug('Job [%s] ended [%s]', job_id, type(self))

		if job_rmdir:
			shutil.rmtree(job_dir)

		log.debug('Job [%s] cleaned up', job_id)
		return res

	def run(self, template_config, job_params):
		pass
