# -*- coding: utf-8 -*-

from __future__ import absolute_import

from logging import getLogger

from ._common import StarterFabric
from ._common import BaseJob
from ..syscommand import Command
from ...utils.string import format_with_emptydefault


log = getLogger(__name__)


class TemplatedScriptJob(BaseJob):

	def create_command_from_config(self, command_config, job_params, timeout_sec=None):

		_cmd_params = command_config
		if isinstance(command_config, str):
			_cmd_params = {
				'cmd': command_config
			}

		cmd = _cmd_params.get('cmd')
		cwd = job_params.get('job_dir')
		out = _cmd_params.get('out')

		cmd = format_with_emptydefault(cmd, job_params)

		# cc = Command(main_cmd_params, job_params_dict, logger=self.log, timeout_sec=duration_sec)
		cc = Command(cmd, cwd=cwd, out=out, timeout_sec=timeout_sec)
		return cc

	def __init__(self, template_config, job_params):
		super().__init__(template_config, job_params)

		self._commands_to_run = []

	def config(self, template_config, job_params):
		# print('R' * 80)
		# print(tpl_params, job_params)
		# print('-' * 50)
		# print(job_params)
		# print('R' * 80)

		main_cmd_config = template_config.get('main')
		if main_cmd_config:
			command = self.create_command_from_config(main_cmd_config, self.job_params, self.duration_sec)
			self._commands_to_run.append(command)

		after_cmd_config_list = template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self._commands_to_run.append(command)

	def __str__(self):
		return '\n\n'.join([
			str(cmd) for cmd in self._commands_to_run
		])

	def run(self):
		for cmd in self._commands_to_run:
			self.log.debug('Command starting', extra={'command': str(cmd)})

			ret = cmd.run()

			err = ret['err']

			if err:
				self.log.error(
					'Command failed',
					extra={'command': str(cmd), 'result': ret}
				)
			else:
				self.log.info(
					'Command done',
					extra={'command': str(cmd), 'result': ret}
				)

		self.log.info('Script succeeded', extra={
			'command': str(self),
		})


start = StarterFabric(TemplatedScriptJob)
