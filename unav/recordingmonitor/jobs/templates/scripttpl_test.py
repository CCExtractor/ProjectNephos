# -*- coding: utf-8 -*-

# import pytest
from .scripttpl import TemplatedScriptJob


class TestTemplatedScriptJob:

	def test_create_command_from_config(self):

		template_config = {
			'type': 'scripttpl',
			'main': {
				'out': "{job_name_slug}.mpg",
			},
			'after': [
				{
					'cmd': 'ping-pong --substitute={job_name_slug}.mpg --plain=123 --slug={job_name_slug}',
					'note': 'unknown',
				},
			]
		}

		job_params = {
			'job_ID': '123',
			'job_name': 'My Own Name For Program',
			'job_main_duration_sec': 45,
			'job_root_dir': '/tmp/python-test',
			'connection_string': 'local',
		}

		tsc = TemplatedScriptJob(template_config, job_params)
		tsc.config()

		assert tsc is not None
		assert isinstance(tsc.commands_list, (list, tuple))

		cmd_cap = tsc.commands_list[0]
		cmd_aft = tsc.commands_list[1]

		assert cmd_cap is not None
		assert cmd_aft is not None

		assert cmd_aft.command == 'ping-pong --substitute=my-own-name-for-program.mpg --plain=123 --slug=my-own-name-for-program'
