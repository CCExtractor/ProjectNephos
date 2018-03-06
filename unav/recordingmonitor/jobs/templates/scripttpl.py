# -*- coding: utf-8 -*-

from logging import getLogger

from ._common import StarterFabric
from ._common import BaseJob
from ..commands import Command
from ...utils.string import format_with_emptydefault

from ..result_processor import BaseJobResultProcessor


log = getLogger(__name__)


class TemplatedScriptJob(BaseJob):
	'''
	Job type, which allows to run an array/list of commands. Commands can
	contain formatting primitives

	* job_ID
	* job_name
	* job_name_slug
	* job_main_duration_sec
	* channel_ID
	* job_launch_date_from
	* job_launch_date_trim
	* job_dir

	'''

	def create_command_from_config(self, command_config, job_params, timeout_sec=None):

		_cmd_params = command_config
		if isinstance(command_config, str):
			_cmd_params = {
				'cmd': command_config,
			}

		cwd = self.cwd
		cmd = _cmd_params.get('cmd')
		out = _cmd_params.get('out')

		cmd = format_with_emptydefault(cmd, job_params)
		out = format_with_emptydefault(out, job_params)

		# cc = Command(main_cmd_params, job_params_dict, logger=self.log, timeout_sec=duration_sec)
		cc = Command(cmd, cwd=cwd, out=out, timeout_sec=timeout_sec)
		return cc

	def __init__(self, template_config, job_params):
		super().__init__(template_config, job_params)

		self.commands_list = []

	def config(self):

		main_cmd_config = self.template_config.get('main')
		if main_cmd_config:
			command = self.create_command_from_config(main_cmd_config, self.job_params, self.duration_sec)
			self.commands_list.append(command)

		after_cmd_config_list = self.template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)

	def __str__(self):
		return '\n'.join([
			str(cmd) for cmd in self.commands_list
		])

	def run(self):
		for cmd in self.commands_list:
			self.log.debug('Command starting', extra={'command': str(cmd)})

			ret = cmd.run()

			self.log.info(
				'Command done', extra={'command': str(cmd), 'result': ret.__json__()}
			)

		# return ret.__json__()
		return {
			'kind': ScriptTplJobResultProcessor.KIND,

			'data': {
				'job_ended': str(self.job_ID),
			}
		}


class ScriptTplJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.templates.scripttpl'

	def __init__(self, app_config):
		super().__init__(app_config)

	# def handle_data(self, data):
	# 	pass


start = StarterFabric(TemplatedScriptJob)
