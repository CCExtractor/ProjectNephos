# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import signal
from logging import getLogger

log = getLogger(__name__)

from subprocess import Popen, TimeoutExpired
from subprocess import DEVNULL, PIPE

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


class StreamWrapper:
	def __init__(self, cwd, name, mode='w'):
		self.safe = False
		self.mode = mode
		self.fd = None
		self.path = None
		self.way = 'UNKNOWN'

		name = str(name)
		code = name.upper()

		if code == 'NONE':
			self.fd = DEVNULL
			self.way = 'DEVNULL'
			self._way_h = ' > /dev/null'

		elif code == 'PIPE':
			self.fd = PIPE
			self.way = 'PIPE'
			self._way_h = ' | cat'

		else:
			self.path = os.path.join(cwd, name)
			self.safe = True
			self.way = 'FILE<{}>'.format(name)
			self._way_h = ' > {}'.format(name)

	def human_str(self):
		return self._way_h

	def __enter__(self):
		if self.safe:
			self.fd = open(self.path, self.mode)
			log.debug('StreamWrapper: open file [%s][%s] = [%s]', self.mode, self.path, self.fd)

		return self.fd

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.safe:
			log.debug('StreamWrapper: close file [%s]', self.path)
			self.fd.close()


class OneCommand:
	def __init__(self, cmd_params, job_params, timeout_sec=None, log=None):
		self.log = log

		prm = cmd_params
		if isinstance(cmd_params, str):
			prm = {
				'cmd': cmd_params
			}

		cmd = prm.get('cmd')
		self.command = format_def(cmd, job_params)
		self.job_dir = job_params.get('job_dir')
		self.timeout = timeout_sec

		self.out = StreamWrapper(self.job_dir, prm.get('out'))

	def human_str(self):
		tm = ''
		if self.timeout is not None:
			tm = '# with timeout {} sec run:\n'.format(self.timeout)

		res = '{tm}{cmd}{out}'.format(
			tm=tm,
			cmd=self.command,
			out=self.out.human_str(),
		)

		return res

	def run(self):

		self.log.info('Command starting', extra={'command': self.command})

		# try:
		# 	# pr = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
		# 	# (prg.out, prg.err) = pr.communicate()

		# 	# prg.out = prg.out.decode()
		# 	# prg.err = prg.err.decode()

		# 	# prg.ret = pr.returncode
		# 	# prg.pid = pr.pid
		# 	# run(cmd, stdout=PIPE, stderr=PIPE, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None)
		# 	pass
		# except OSError as e:
		# 	print('E' * 80)
		# 	print(e)
		# 	print('E' * 80)

		# 	cpp = type('BUG', (), {'stderr': None, 'stdout': None, 'returncode': None})
		# 	if e.errno == os.errno.ENOENT:
		# 		self.log.critical('Executable was not found: [{0}]'.format(self.command))
		# 	else:
		# 		# Something else went wrong while trying to run the command..
		# 		self.log.error(e)
		# 		raise e

		if self.timeout is not None:
			self.log.info('Command timeout is %s sec', self.timeout, extra={
				'command': self.command,
				'timeout': self.timeout
			})

		out = None
		err = None
		rc = None
		pid = None

		with self.out as outfd:
			# cpp = run(self.command, stdout=outfd, stderr=PIPE, cwd=self.job_dir, shell=True, timeout=self.timeout)

			# preexec_fn=os.setsid
			with Popen(self.command, stdout=outfd, stderr=PIPE, cwd=self.job_dir, shell=True, start_new_session=True) as process:
				pid = process.pid
				try:
					(out, err) = process.communicate(timeout=self.timeout)
				except TimeoutExpired as exc:
					os.killpg(pid, signal.SIGINT)  # send signal to the process group
					(out, err) = process.communicate()
				rc = process.returncode

		out = decode_and_superstrip(out)
		err = decode_and_superstrip(err)
		if rc is not None:
			rc = int(rc)

		prg = {
			'out_way': self.out.way,
			'out': out,
			'err': err,
			'rc': rc
		}

		if err:
			self.log.error(
				'Command failed',
				extra={'command': self.command, 'result': prg}
			)
		else:
			self.log.info(
				'Command done',
				extra={'command': self.command, 'result': prg}
			)


class TemplatedScriptJob(BaseJob):

	def _config(self, tpl_params, job_params):
		# print('R' * 80)
		# print(tpl_params, job_params)
		# print('-' * 50)
		# print(job_params)
		# print('R' * 80)

		self._commands_to_run = []

		job_params_dict = dict(job_params)

		date_from = job_params.get('job_date_from')
		date_trim = job_params.get('job_date_trim')
		duration_sec = (date_trim - date_from).total_seconds()

		main_cmd_params = tpl_params.get('main')
		if main_cmd_params:
			cc = OneCommand(main_cmd_params, job_params_dict, log=self.log, timeout_sec=duration_sec)
			self._commands_to_run.append(cc)

		after_cmd_list = tpl_params.get('after')
		if after_cmd_list:
			for after_cmd_params in after_cmd_list:
				cc = OneCommand(after_cmd_params, job_params_dict, log=self.log)
				self._commands_to_run.append(cc)

		self.log.info('Script for job is done', extra={
			'command': self.human_str(),
		})

	def _run(self):
		for c in self._commands_to_run:
			c.run()

	def human_str(self):
		return '\n\n'.join([
			cmd.human_str() for cmd in self._commands_to_run
		])

	def run(self, tpl_params, job_params):
		self._config(tpl_params, job_params)
		self._run()


start = TemplatedScriptJob()
