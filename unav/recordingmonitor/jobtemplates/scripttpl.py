# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
from logging import getLogger

log = getLogger(__name__)

from subprocess import Popen, PIPE, run

from . import BaseJob


def decode_and_superstrip(xx):
	if xx is None:
		return None

	s = xx.decode()
	if s:
		s = s.strip()
	if not s:
		s = None

	return s


class DictFormatEmpty(dict):
	def __missing__(self, key):
		# return '{' + key + '}'
		return ''


def format_def(tpl, data):
	return tpl.format_map(DictFormatEmpty(data))


class TemplatedScriptJob(BaseJob):

	template_name = 'TemplatedScriptJob'

	def script_run_item(self, config, script, job_params, timeout_sec=None):

		cmd = format_def(str(script), job_params)
		job_dir = job_params.get('job_dir')

		self.log.info('Command starting', extra={'command': cmd})

		try:
			# pr = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
			# (prg.out, prg.err) = pr.communicate()

			# prg.out = prg.out.decode()
			# prg.err = prg.err.decode()

			# prg.ret = pr.returncode
			# prg.pid = pr.pid
			# run(cmd, stdout=PIPE, stderr=PIPE, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None)
			log.debug('timeout is %d', timeout_sec)
			cpp = run(cmd, stdout=PIPE, stderr=PIPE, cwd=job_dir, shell=True, timeout=timeout_sec)
			log.debug('hohooop')

		except OSError as e:
			print('E' * 80)
			print(e)
			print('E' * 80)

			cpp = type('BUG', (), {'stderr': None, 'stdout': None, 'returncode': None})
			if e.errno == os.errno.ENOENT:
				self.log.critical('Executable was not found: [{0}]'.format(cmd))
			else:
				# Something else went wrong while trying to run the command..
				self.log.error(e)
				raise e

		out = decode_and_superstrip(cpp.stdout)
		err = decode_and_superstrip(cpp.stderr)

		rc = cpp.returncode
		if rc is not None:
			rc = int(rc)

		prg = {
			'out': out,
			'err': err,
			'rc': rc
		}

		if err:
			self.log.error(
				'Command failed',
				extra={'command': cmd, 'result': prg}
			)
		else:
			self.log.info(
				'Command done',
				extra={'command': cmd, 'result': prg}
			)

	def run(self, tpl_params, job_params):
		# print('R' * 80)
		# print(tpl_params, job_params)
		# print('-' * 50)
		# print(job_params)
		# print('R' * 80)

		job_params_dict = dict(job_params)

		main_cmd = tpl_params.get('main')
		if main_cmd:
			self.script_run_item(tpl_params, main_cmd, job_params_dict, timeout_sec=5)

		script_cmds = tpl_params.get('script', tpl_params.get('after_main'))

		if script_cmds:
			for script_cmd in script_cmds:
				self.script_run_item(tpl_params, script_cmd, job_params_dict)


start = TemplatedScriptJob()
