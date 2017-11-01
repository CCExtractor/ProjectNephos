# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import signal
from logging import getLogger

from subprocess import Popen, TimeoutExpired
from subprocess import DEVNULL, PIPE

from ..errors import CommandError
from ..utils.string import decode_and_superstrip


log = getLogger(__name__)


class StreamWrapper:
	def __init__(self, name, cwd=None, mode='w'):
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
			_cwd = cwd or ''
			self.path = os.path.join(_cwd, name)
			self.safe = True
			self.way = 'FILE<{}>'.format(name)
			self._way_h = ' > {}'.format(name)

	def __str__(self):
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


class Command:
	def __init__(self, cmd, cwd='', out=None, timeout_sec=None, logger=None):
		self.log = logger or log
		self.command = cmd
		self.cwd = cwd
		self.timeout = timeout_sec

		self.out = StreamWrapper(out, cwd=self.cwd)

	# def __init__(self, cmd_params, job_params, timeout_sec=None, logger=None):
	# 	self.log = logger or log

	# 	prm = cmd_params
	# 	if isinstance(cmd_params, str):
	# 		prm = {
	# 			'cmd': cmd_params
	# 		}

	# 	cmd = prm.get('cmd')
	# 	self.command = format_with_emptydefault(cmd, job_params)
	# 	self.job_dir = job_params.get('job_dir')
	# 	self.timeout = timeout_sec

	# 	self.out = StreamWrapper(prm.get('out'), cwd=self.job_dir)

	def __str__(self):
		tm = ''
		if self.timeout is not None:
			tm = '# with timeout {} sec run:\n'.format(self.timeout)

		res = '{tm}{cmd}{out}'.format(
			tm=tm,
			cmd=self.command,
			out=str(self.out),
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
			# cpp = run(self.command, stdout=outfd, stderr=PIPE, cwd=self.cwd, shell=True, timeout=self.timeout)

			# preexec_fn=os.setsid
			with Popen(self.command, stdout=outfd, stderr=PIPE, cwd=self.cwd, shell=True, start_new_session=True) as process:
				pid = process.pid
				try:
					(out, err) = process.communicate(timeout=self.timeout)
				except TimeoutExpired:  # as exc:
					os.killpg(pid, signal.SIGINT)  # send signal to the process group
					(out, err) = process.communicate()
				rc = process.returncode

		exc = None
		out = decode_and_superstrip(out)
		err = decode_and_superstrip(err)
		if rc is not None:
			rc = int(rc)

		if err:
			exc = CommandError(err)

		prg = {
			'out_way': self.out.way,
			'out': out,
			'err': err,
			'rc': rc,
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

		prg['exc'] = exc
		return prg
