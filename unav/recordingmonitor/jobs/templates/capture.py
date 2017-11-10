# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pydash
from logging import getLogger

from ._common import StarterFabric
from .scripttpl import TemplatedScriptJob
from ..syscommand import CaptureCommand

from ...models.tv import Channel

log = getLogger(__name__)


class CaptureStreamJob(TemplatedScriptJob):

	def config(self, template_config, job_params):

		out = pydash.get(template_config, 'main.out', 'stream.ts')

		channel_ID = job_params['channel_ID']
		capture_address = job_params.get('capture_address')

		self.channel = self.session.query(Channel).get(channel_ID)

		capture_command = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=capture_address,
			cwd=self.cwd,
			out=out,
			timeout_sec=self.duration_sec,
		)
		self.commands_list.append(capture_command)

		after_cmd_config_list = template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)


start = StarterFabric(CaptureStreamJob)
