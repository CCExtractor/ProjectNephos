# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import signal
from logging import getLogger

# convenient way to use
from flask import json

from subprocess import Popen, TimeoutExpired
from subprocess import DEVNULL, PIPE

from ..errors import BaseError
from ..utils.string import decode_and_superstrip
from ..utils.string import format_with_emptydefault


log = getLogger(__name__)


class CommandError(BaseError):
	def __init__(
		self,
		command,
		stdin_way=None,
		# stdin - omitted!
		stdout_way=None,
		stdout=None,
		stderr=None,
		rc=None,
	):
		msg = (
			'pseudo-command: [{command}] failed with ret-code: [{rc}] '
			'stderr: [{stderr}]'
		).format(
			command=str(command),
			rc=rc,
			stdout_way=stdout_way,
			stderr=stderr,
		)

		super().__init__(msg)

		self.command = command
		self.stdin_way = stdin_way
		self.stdout_way = stdout_way
		self.stdout = stdout
		self.stderr = stderr
		self.rc = rc

	def __json__(self):
		dd = vars(self)
		dd['command'] = str(self.command)
		return dd


class CommandResult:
	def __init__(
		self,
		command,
		stdin_way=None,
		# stdin - omitted!
		stdout_way=None,
		stdout=None,
		stderr=None,
		rc=None,
	):
		self.command = command
		self.stdin_way = stdin_way
		self.stdout_way = stdout_way
		self.stdout = stdout
		self.stderr = stderr
		self.rc = rc

	def __json__(self):
		dd = vars(self)
		dd['command'] = str(self.command)
		return dd


def command_error2result(exc):
	return CommandResult(
		command    =exc.command,        # noqa: E221
		stdin_way  =exc.stdin_way,      # noqa: E221
		stdout_way =exc.stdout_way,     # noqa: E221
		stdout     =exc.stdout,         # noqa: E221
		stderr     =exc.stderr,         # noqa: E221
		rc         =exc.rc,             # noqa: E221
	)


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
			log.debug('StreamWrapper: open file [%s][%s]', self.mode, self.path)

		return self.fd

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.safe:
			log.debug('StreamWrapper: close file [%s]', self.path)
			self.fd.close()


################################################################################
# COMMAND FABRIC
################################################################################
class CommandFabric:
	def get_command(self):
		pass


################################################################################
# COMMANDS
################################################################################


class Command:
	def __init__(self, cmd, cwd='', inp=None, out=None, timeout_sec=None):

		self.command = cmd
		self.cwd = cwd
		self.timeout = timeout_sec

		self.out = StreamWrapper(out, cwd=self.cwd)
		self.inp = StreamWrapper(inp, cwd=self.cwd, mode='r')

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
		_tm = ''
		if self.timeout is not None:
			_tm = 'timeout {} '.format(self.timeout)

		res = '{tm}{cmd}{out}'.format(
			tm=_tm,
			cmd=self.command,
			out=str(self.out),
		)

		return res

	def run(self):

		log.debug('Command starting [%s]', self.command)

		if self.timeout is not None:
			log.info('Command timeout is %s sec', self.timeout)

		out = None
		err = None
		rc = None
		pid = None

		with self.out as outfd, self.inp as inpfd:

			with Popen(
				self.command,
				stdin=inpfd,
				stdout=outfd,
				stderr=PIPE,
				cwd=self.cwd,
				shell=True,
				start_new_session=True
			) as process:
				pid = process.pid
				try:
					(out, err) = process.communicate(timeout=self.timeout)
				except TimeoutExpired:  # as exc:
					os.killpg(pid, signal.SIGTERM)  # SIGINT)  # send signal to the process group
					(out, err) = process.communicate()
				rc = process.returncode

		out = decode_and_superstrip(out)
		err = decode_and_superstrip(err)
		if rc is not None:
			rc = int(rc)

		# exception will be thrown if there is something in stdout!
		if err:
			raise CommandError(
				command=self,
				stdin_way=self.inp.way,
				stdout_way=self.out.way,
				stdout=out,
				stderr=err,
				rc=rc,
			)

		return CommandResult(

			command=self,
			stdin_way=self.inp.way,
			# stdin - omitted!
			stdout_way=self.out.way,
			stdout=out,
			stderr=err,
			rc=rc,
		)


class CaptureCommand(Command):
	'''
	Command for capturing the stream

	..seealso::

		* https://github.com/CCExtractor/ProjectNephos/wiki/Editing-Record-with-multicat-(this-is-just-%22call-a-program%22)
		* https://github.com/mmalecki/multicat/blob/master/trunk/README

	'''
	def __init__(self, channel_ip, ifaddr, cwd='', out=None, timeout_sec=None):

		if not isinstance(out, str):
			raise ValueError('parameter `out` of CaptureCommand MUST be a string')

		_timeout_str = ''

		if timeout_sec is not None:
			_delay_27kHz = int(timeout_sec * 27000000)
			_timeout_str = '-d {:d}'.format(_delay_27kHz)

		_options = ''
		if ifaddr is not None:
			_options = '/ifaddr={}'.format(ifaddr)

		cmd = format_with_emptydefault('multicat {timeout} -u @{channel_ip}{options} {out_file}', {
			'channel_ip': channel_ip,
			'ifaddr':     ifaddr,
			'out_file':   out,
			'timeout':    _timeout_str,
			'options':    _options,
		})

		super().__init__(
			cmd=cmd,
			cwd=cwd,

			out=None,
			timeout_sec=None,
		)

	def run(self):

		try:
			res = super().run()
		except CommandError as exc:
			# multicat sends DEBUG messages to stderr
			# this leads to EXPECTED exception
			if exc.rc == 0:
				res = command_error2result(exc)
			else:
				raise

		return res


class VideoInfoCommand(Command):
	'''
	Wrapper for ffprobe

	..seealso::

		* https://gist.github.com/fabianmoronzirfas/4682731

	Example of response:

	..codeblock::

	{
		"format": {
			"filename": "/home/tmp/maintenance/channel_on_air/8256cf0f-29d7-4dfd-b61b-7b020a8f4c67/chunk.ts",
			"nb_streams": 5,
			"nb_programs": 1,
			"format_name": "mpegts",
			"format_long_name": "MPEG-TS (MPEG-2 Transport Stream)",
			"start_time": "396.903411",
			"duration": "1.161545",
			"size": "48692",
			"bit_rate": "335360",
			"probe_score": 100
		}
	}


	'''
	def __init__(self, inp, cwd='', timeout_sec=10):

		# TODO: find a better way to validate input:
		ifst = StreamWrapper(inp, cwd=cwd, mode='r')
		if not ifst.path:
			raise ValueError('parameter `inp` of VideoInfoCommand MUST be a file-path')

		cmd = 'ffprobe -loglevel error -print_format json -show_streams -show_format {inp}'.format(
			inp=inp,
		)

		super().__init__(
			cmd=cmd,
			cwd=cwd,

			out='PIPE',
			timeout_sec=timeout_sec,
		)

	def run(self):

		try:
			res = super().run()
		except CommandError as exc:
			# ffprobe sends a lot of info to the stderr
			# this leads to EXPECTED exception, but we will check the stream error
			# using return-code
			if exc.rc == 0:
				res = command_error2result(exc)
			else:
				raise

		raw = res.stdout
		js = json.loads(raw)
		# TODO: think about strict typing for output (see ffprobe documentation)
		res.stdout = js

		return res


class ExtractCaptionsCommand(Command):
	'''
	Wrapper for ccextractor
	'''
	def __init__(self, inp, cwd='', timeout_sec=None, app='ccextractor', tpage=None, extra_params=None):

		# TODO: find a better way to validate input:
		ifst = StreamWrapper(inp, cwd=cwd, mode='r')
		if not ifst.path:
			raise ValueError('parameter `inp` of ExtractCaptionsCommand MUST be a file-path')

		if not app:
			app = 'ccextractor'

		# Call CCExtractor
		# -ts                                  - input is a MPEG TS file
		# -datets                              - write time as YYYYMMDDHHMMss.ms
		# -autoprogram                         - automatically select the first good program ID
		# -pn $PN                              - select a known program number
		# -tpage $TP                           - teletext page
		# -1 or -2 or -12                      - primary transcript, secondary transcript, or both (not for teletext?)
		# -UCLA                                - adds TLT|$TP
		# -noru                                - do not repeat lines to simulate roll-up
		# -out=ttxt                            - plain text output format
		# -utf8                                - character set
		# -unixts $BTIM                        - unix reference time (number of seconds since epoch)
		# -delay                               - seconds adjustment
		# -o $FIL.ccx.out                      - named output
		# $FIL.$EXT                            - input MPEG file

		# ccextractor          -ttxt -autoprogram -UCLA -noru -utf8 --nofontcolor -parsepat -parsepmt -datets -unixts $BTIM -tpage $TP -o $FIL.ccx.out $FIL.$EXT > $FIL.ccx.stout 2> $FIL.ccx.stderr
		# ccextractor          -ttxt -autoprogram -UCLA -noru -utf8 --nofontcolor -parsepat -parsepmt -datets -unixts $BTIM            -o $FIL.ccx.out $FIL.$EXT > $FIL.ccx.stout 2> $FIL.ccx.stderr
		# ccextractor-0.69-a02 -ttxt -autoprogram -UCLA -noru -utf8 --nofontcolor -parsepat -parsepmt -delay 0 -ts          -tpage $TP -o $FIL.ccx.out $FIL.$EXT > $FIL.ccx.stout 2> $FIL.ccx.stderr
		# ccextractor-0.69-a02 -ttxt -autoprogram -UCLA -noru -utf8 --nofontcolor -parsepat -parsepmt -delay 0 -ts                     -o $FIL.ccx.out $FIL.$EXT > $FIL.ccx.stout 2> $FIL.ccx.stderr

		if tpage:
			tpage_str = '-tpage {}'.format(tpage)
		else:
			tpage_str = ''

		cargs = '-ttxt -autoprogram -UCLA -noru -utf8 --nofontcolor -parsepat -parsepmt -stdout'

		cmd = '{app} {cargs} {tpage_str} {extra_params} {inp}'.format(
			app=app,
			inp=inp,
			cargs=cargs,
			tpage_str=tpage_str,
			extra_params=extra_params,
		)

		super().__init__(
			cmd=cmd,
			cwd=cwd,

			out='PIPE',
			timeout_sec=timeout_sec,
		)

	def run(self):

		try:
			res = super().run()
		except CommandError as exc:
			# ffprobe sends a lot of info to the stderr
			# this leads to EXPECTED exception, but we will check the stream error
			# using return-code
			if exc.rc == 0:
				res = command_error2result(exc)
			else:
				raise

		subs = res.stdout

		# # Remove the byte order mark (BOM)
		# $SED -i '1 s/^\xef\xbb\xbf//' $FIL.ccx.out

		# # Remove any 7F DEL character
		# $SED -i -e 's/\x7F//g' $FIL.ccx.out

		# # Get the teletext page number used by ccextractor
		# TPX="$( grep -m1 '^2' $FIL.ccx.out | $SED -r 's/.*([0-9]{3})\|?TLT.*/\1/' )"

		# # Remove the teletext page number and TLT from the body
		# $SED -r -i "s/$TPX\|?TLT\|/CC1|/" $FIL.ccx.out

		##########################
		# dos2unix
		# Convert from DOS format (may not be needed)
		# dos2unix -q -k -o $FIL.txt

		res.subs = subs
		res.length = 0 if subs is None else len(subs)

		return res
