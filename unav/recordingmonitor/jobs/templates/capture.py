# -*- coding: utf-8 -*-

import os
import json

from logging import getLogger

from ._common import StarterFabric
from .scripttpl import TemplatedScriptJob
from ..commands import CaptureCommand

from ...utils.string import format_with_emptydefault

from ...models.tv import Channel

from ..result_processor import BaseJobResultProcessor

log = getLogger(__name__)


class CaptureStreamJob(TemplatedScriptJob):

	def config(self):

		# TODO: remove this;)
		# captured_out = pydash.get(self.template_config, 'main.out', 'stream.ts')
		# captured_out = format_with_emptydefault(captured_out, self.job_params)

		channel_ID = self.job_params['channel_ID']

		self.job_params['out_filename_noext'] = format_with_emptydefault(
			'{job_launch_date_from:%Y-%m-%d}_{job_launch_date_from:%H%M}_{job_name_slug}',
			self.job_params
		)

		self.channel = self.session.query(Channel).get(channel_ID)
		# TODO: check that channel is not NONE

		after_cmd_config_list = self.template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)

	def run(self):

		# TODO: remove these lines
		capture_address = self.job_params.get('capture_address')
		filename = self.job_params['out_filename_noext']

		filename_out = filename + '.ts'
		filename_meta = filename + '.task.json'

		# ======================================================================
		# MAIN: capture
		# ======================================================================
		# res_capture = self._run_cmd(self.commands__capture)
		self._run_cmd(CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=capture_address,
			cwd=self.cwd,
			out=filename_out,
			timeout_sec=self.duration_sec,
		))

		fullfilename_out = os.path.join(self.cwd, filename_out)
		fullfilename_out_new = os.path.join(self.jobs_root, 'uploader', filename_out)
		os.rename(fullfilename_out, fullfilename_out_new)

		fullmetaname = os.path.join(self.jobs_root, 'uploader', filename_meta)
		with open(fullmetaname, 'w') as fp:
			meta = {
				'filename'             : filename,               # noqa: E203
				'channel_ID'           : self.channel.ID,        # noqa: E203
				'date_from'            : self.date_from,         # noqa: E203
				'job_params'           : self.job_params,        # noqa: E203
				'job_launch_ID'        : self.job_launch.ID,     # noqa: E203
			}
			json.dump(meta, fp)

		return {
			'kind': CaptureJobResultProcessor.KIND,

			'data': {
				'job_ended': str(self.job_ID),
			}
		}

	def _run_cmd(self, cmd):
		self.log.debug('Command starting', extra={'command': str(cmd)})
		ret = cmd.run()
		self.log.info(
			'Command done', extra={
				'command': str(cmd),
				'result': ret.__json__()
			}
		)
		return ret


class CaptureJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.templates.capture'

	def __init__(self, app_config):
		super().__init__(app_config)

	# def handle_data(self, data):
	# 	pass


start = StarterFabric(CaptureStreamJob)
