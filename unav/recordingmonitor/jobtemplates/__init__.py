# -*- coding: utf-8 -*-

import os
import shutil
import logging

from ..db import DB

from ..logger import SQLAlchemyHandler
from ..logger import ExtendExtraLogAdapter

log = logging.getLogger(__name__)
joblog = logging.getLogger('{0}.{1}'.format(__name__, 'job'))


def get_adapted_logger(job_info_id, job_template_name):
	la = ExtendExtraLogAdapter(joblog, {
		'job_info_id': job_info_id,
		'job_template_name': job_template_name,
		# 'command': None
	})

	h = SQLAlchemyHandler()
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

	def __call__(self, job_meta, tpl_params, job_params):

		job_id = job_meta['job_id']
		log.debug('Job [%s] preparing', job_id)

		# TODO: remove job_dir from meta
		job_dir = job_meta['job_dir']
		# TODO: remove connection_string from meta
		# IMPORTANT: it POPS connection string!
		connection_string = job_meta.pop('connection_string')

		self.db = DB
		self.db.init(connection_string)
		self.log = get_adapted_logger(job_id, self.template_name)

		log.debug('Job [%s] Dir: [%s]', job_id, job_dir)

		eff_job_params = self._extend_job_params_with_defaults(
			job_meta,
			tpl_params,
			job_params
		)

		os.makedirs(job_dir, exist_ok=True)

		self.log.debug('Job [%s] starting [%s]', job_id, type(self))
		res = self.run(tpl_params, eff_job_params)
		self.log.debug('Job [%s] ended [%s]', job_id, type(self))

		if job_meta.get('job_rmdir', True):
			shutil.rmtree(job_dir)

		log.debug('Job [%s] cleaned up', job_id)
		return res

	def _extend_job_params_with_defaults(self, job_meta, tpl_params, job_params):

		p = dict()
		p.update(job_meta)
		p.update(job_params)

		return p

	def run(self, job_meta, tpl_params, job_params):
		pass
