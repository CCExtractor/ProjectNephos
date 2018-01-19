# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pydash
from logging import getLogger

from ._common import StarterFabric
from .scripttpl import TemplatedScriptJob
from ..syscommand import CaptureCommand
from ..syscommand import VideoInfoCommand

from ...utils.string import format_with_emptydefault

from ...models.tv import Channel

from ..result_processor import BaseJobResultProcessor

log = getLogger(__name__)


class CaptureStreamJob(TemplatedScriptJob):

	def config(self):

		captured_out = pydash.get(self.template_config, 'main.out', 'stream.ts')
		captured_out = format_with_emptydefault(captured_out, self.job_params)

		channel_ID = self.job_params['channel_ID']
		capture_address = self.job_params.get('capture_address')

		self.channel = self.session.query(Channel).get(channel_ID)
		# TODO: check that channel is not NONE

		self.commands__capture = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=capture_address,
			cwd=self.cwd,
			out=captured_out,
			timeout_sec=self.duration_sec,
		)

		self.commands__videoinfo = VideoInfoCommand(inp=captured_out, cwd=self.cwd)

		after_cmd_config_list = self.template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)

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

	@staticmethod
	def _get_scaled_picture_size(w, h, s):
		_SIZES = {
			'1920x1088': '640x352',
			'1920x1080': '640x352',
			'1280x720' : '640x352',
			'720x576'  : '640x512',
			'720x480'  : '640x426',
		}

		if s in _SIZES:
			return _SIZES[s]

		return s

	def run(self):

		# MAIN: capture
		# res_capture = self._run_cmd(self.commands__capture)
		self._run_cmd(self.commands__capture)

		# commands from check-cc-single
		# 1 get video info
		res_capinfo = self._run_cmd(self.commands__videoinfo)

		# 1a Duration
		_video_duration = float(pydash.get(res_capinfo.stdout, 'format.duration'))
		self.log.info('Video duration is %s', _video_duration)

		# 1a Size
		_picture_size = None
		_picture_width = None
		_picture_height = None
		for _stream in pydash.get(res_capinfo.stdout, 'streams', []):
			if not isinstance(_stream, dict):
				continue

			if 'video' == _stream.get('codec_type', '').lower():
				try:
					_picture_width = int(_stream['width'])
					_picture_height = int(_stream['height'])
					_picture_size = '{0}x{1}'.format(_picture_width, _picture_height)
				except TypeError:
					_picture_size = None

				break

		_scaled_size = self._get_scaled_picture_size(
			_picture_width,
			_picture_height,
			_picture_size
		)

		self.log.info('Video size: %s, scaled size: %s', _picture_size, _scaled_size)

		# 2 Add the collection name, an identifier, and the video duration
		# (insert after the first line, TOP)
		# "COL|Communication Studies Archive, UCLA\nUID|$(uuid -v1)\nDUR|"$DUR"\nVID|"$VID"|"$PIC""`" $DDIR/$FIL.txt

		for cmd in self.commands_list:
			# res = self._run_cmd(cmd)
			self._run_cmd(cmd)

		# return ret.__json__()
		return {
			'kind': CaptureJobResultProcessor.KIND,

			'data': {
				'job_ended': str(self.job_ID),
			}
		}


class CaptureJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.templates.capture'

	def __init__(self, app_config):
		super().__init__(app_config)

	# def handle_data(self, data):
	# 	pass


start = StarterFabric(CaptureStreamJob)
