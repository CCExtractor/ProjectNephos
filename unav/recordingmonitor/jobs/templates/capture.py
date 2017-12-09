# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pydash
from logging import getLogger

from ._common import StarterFabric
from .scripttpl import TemplatedScriptJob
from ..syscommand import CaptureCommand
from ...utils.string import format_with_emptydefault

from ...models.tv import Channel

from ..result_processor import BaseJobResultProcessor

log = getLogger(__name__)


class CaptureStreamJob(TemplatedScriptJob):

	def config(self):

		out = pydash.get(self.template_config, 'main.out', 'stream.ts')
		out = format_with_emptydefault(out, self.job_params)

		channel_ID = self.job_params['channel_ID']
		capture_address = self.job_params.get('capture_address')

		self.channel = self.session.query(Channel).get(channel_ID)
		# TODO: check that channel is not NONE

		capture_command = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=capture_address,
			cwd=self.cwd,
			out=out,
			timeout_sec=self.duration_sec,
		)
		self.commands_list.append(capture_command)

		after_cmd_config_list = self.template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)

	# TODO: override RUN method and replace KIND in the result value


class CaptureJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.templates.capture'

	def __init__(self, app_config):
		super().__init__(app_config)

	# def handle_data(self, data):
	# 	pass


start = StarterFabric(CaptureStreamJob)
