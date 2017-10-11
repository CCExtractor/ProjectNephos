# -*- coding: utf-8 -*-

import logging

from ..logger import get_job_logger

log = logging.getLogger(__name__)


class BaseJob:
	# def __init__(self, job_info_id, tpl_params, job_params):

	template_name = 'unknown'

	def __init__(self):
		self.log = None
		log.debug('Instance of Job: creating [%s]', type(self))

	def __call__(self, job_info_id, tpl_params, job_params):
		self.log = get_job_logger(job_info_id, self.template_name)

		log.debug('Instance of Job: starting [%s]', type(self))
		res = self.run(tpl_params, job_params)
		log.debug('Instance of Job: stopped [%s]', type(self))
		return res

	def run(self, job_info_id, tpl_params, job_params):
		pass
