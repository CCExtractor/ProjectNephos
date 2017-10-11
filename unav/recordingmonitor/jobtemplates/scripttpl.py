# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
from subprocess import Popen, PIPE, run

from . import BaseJob


def decode_and_superstrip(xx):
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


class Job(BaseJob):

	template_name = 'scripttpl'

	def script_run_item(self, config, script, job_params):

		cmd = format_def(str(script), job_params)

		self.log.info('cmd starting', extra={'command': cmd})

		try:
			# pr = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
			# (prg.out, prg.err) = pr.communicate()

			# prg.out = prg.out.decode()
			# prg.err = prg.err.decode()

			# prg.ret = pr.returncode
			# prg.pid = pr.pid
			# run(cmd, stdout=PIPE, stderr=PIPE, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None)
			cpp = run(cmd, stdout=PIPE, stderr=PIPE, shell=True)

		except OSError as e:
			if e.errno == os.errno.ENOENT:
				# probably, executable not found..
				raise Exception('This executable was not found: [{0}]'.format(cmd[0]))
			else:
				# Something else went wrong while trying to run the command..
				raise

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

		self.log.info('cmd stopped', extra={'command': cmd, 'result': prg})

	def run(self, tpl_params, job_params):
		# print('R' * 80)
		# print(tpl_params, job_params)
		# print('-' * 50)
		# print(job_params)
		# print('R' * 80)

		job_params_dict = dict(job_params)

		for script_cmd in tpl_params['script']:
			self.script_run_item(tpl_params, script_cmd, job_params_dict)

		self.log.debug('task ended')


start = Job()
