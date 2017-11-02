# -*- coding: utf-8 -*-

from __future__ import absolute_import

from logging import getLogger

from . import BaseJob
from ..syscommand import Command
from ...utils.string import format_with_emptydefault


log = getLogger(__name__)


class TemplatedScriptJob(BaseJob):

	def _create_command(self, cmd_params, job_params, timeout_sec=None):

		_cmd_params = cmd_params
		if isinstance(cmd_params, str):
			_cmd_params = {
				'cmd': cmd_params
			}

		cmd = _cmd_params.get('cmd')
		cwd = job_params.get('job_dir')
		out = _cmd_params.get('out')

		cmd = format_with_emptydefault(cmd, job_params)

		# cc = Command(main_cmd_params, job_params_dict, logger=self.log, timeout_sec=duration_sec)
		cc = Command(cmd, cwd=cwd, out=out, timeout_sec=timeout_sec, logger=self.log)
		return cc

	def _config(self, template_config, job_params):
		# print('R' * 80)
		# print(tpl_params, job_params)
		# print('-' * 50)
		# print(job_params)
		# print('R' * 80)

		self._commands_to_run = []

		job_params_dict = dict(job_params)

		date_from = job_params.get('job_date_from')
		date_trim = job_params.get('job_date_trim')
		duration_sec = (date_trim - date_from).total_seconds()

		main_cmd_params = template_config.get('main')
		if main_cmd_params:
			command = self._create_command(main_cmd_params, job_params_dict, duration_sec)
			self._commands_to_run.append(command)

		after_cmd_list = template_config.get('after')
		if after_cmd_list:
			for after_cmd_params in after_cmd_list:
				command = self._create_command(after_cmd_params, job_params_dict)
				self._commands_to_run.append(command)

		self.log.info('Script for job is done', extra={
			'command': str(self),
		})

	def _run(self):
		for c in self._commands_to_run:
			c.run()

	def __str__(self):
		return '\n\n'.join([
			str(cmd) for cmd in self._commands_to_run
		])

	def run(self, template_config, job_params):
		self._config(template_config, job_params)
		self._run()


# TODO: probably, this should be written as a function, creating a class.
start = TemplatedScriptJob()
