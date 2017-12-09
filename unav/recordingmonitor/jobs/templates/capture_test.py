# -*- coding: utf-8 -*-

# import pytest
import mock
from .capture import CaptureStreamJob


class TestCaptureStreamJob:

	def test_create_command_from_config(self):

		template_config = {
			'type': 'capture',
			'main': {
				'out': "{job_name_slug}.mpg",
			},
			'after': [
				{
					'cmd': 'proga --sl1={job_name_slug}.mpg --plain=123 --id={job_ID} --slug={job_name_slug}',
					'note': 'unknown',
				},
			]
		}

		job_params = {
			'job_ID': '123',
			'job_name': 'NAME capturing % Program',
			'job_main_duration_sec': 45,
			'job_root_dir': '/tmp/python-test',
			'connection_string': 'local',
			'channel_ID': '202a3a96-e640-4aae-ade4-261e0a1bd9d7',
		}

		with mock.patch('unav.recordingmonitor.jobs.templates._common.get_session') as patch_get_session:
			# self.session.query(Channel).get(channel_ID)
			mock_query_caller = mock.MagicMock()
			patch_get_session.return_value.query = mock_query_caller

			mock_channel = mock.MagicMock()
			mock_query_caller.return_value.get.return_value = mock_channel
			mock_channel.ip_string = '127.0.0.1:54321'

			with CaptureStreamJob(template_config, job_params) as tsc:
				tsc.config()

		assert tsc is not None
		assert isinstance(tsc.commands_list, (list, tuple))

		cmd_cap = tsc.commands_list[0]
		cmd_aft = tsc.commands_list[1]

		# test capture command
		assert cmd_cap is not None
		assert cmd_cap.command == 'multicat -d 1215000000 -u @127.0.0.1:54321 name-capturing-program.mpg'

		# test AFTER commands:
		assert cmd_aft is not None
		assert cmd_aft.command == 'proga --sl1=name-capturing-program.mpg --plain=123 --id=123 --slug=name-capturing-program'

		cmd_aft_str = str(cmd_aft)
		assert cmd_aft_str == 'proga --sl1=name-capturing-program.mpg --plain=123 --id=123 --slug=name-capturing-program > /dev/null'
