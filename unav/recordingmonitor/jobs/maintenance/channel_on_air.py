# -*- coding: utf-8 -*-

'''
Check that all channels are on air
'''

import os
import shutil
import logging

import arrow
import pydash
import uuid

from ...models.tv import Channel
from ...models.tv import ChannelStatus
from ...db import get_session
#from ...errors import MaintenanceError
from ...errors import BaseError

# from ...utils.string import format_with_emptydefault

from ..syscommand import Command
from ..syscommand import CaptureCommand
from ..syscommand import GetVideoInfoCommand


log = logging.getLogger(__name__)


class ChannelBaseError(BaseError):
	pass


class ChannelStreamEmptyError(ChannelBaseError):
	pass


class ChannelCorruptedError(ChannelBaseError):
	pass


class ChannelChecker:

	DEMO_CAPTURING_TIMEOUT_SEC = 6

	def __init__(self, app_config, channel_id):

		# BUG: move to ./worker.py
		self.path_var = app_config.get('capture.paths.base')
		self.__cleanup_dir = app_config.get('scheduler.maintenance.rmdir')

		# TODO: use class, not type()
		self.config = type('__internal_config', (), {})
		# TODO: remove connection_string from meta
		self.config.connection_string = app_config.connection_string
		self.config.capture_address = app_config.get('capture.address')

		self.channel_id = channel_id

		self.ID = str(uuid.uuid4())

		self.session = None
		self.cwd = None
		self.channel_status = None

	def __enter__(self):

		session = get_session(self.config.connection_string)
		self.session = session

		self.channel = session.query(Channel).get(self.channel_id)
		log.info('start checking status of [%s]', self.channel.name)

		cs = self.channel.channel_status

		# 1 init status in DB (if not exist yet)
		if cs is None:
			cs = ChannelStatus()
			cs.channel = self.channel
			session.add(cs)
			session.commit()
		self.channel_status = cs

		# 2 create temporary dir
		self.cwd = os.path.join(self.path_var, 'maintenance', 'channel_on_air', str(self.ID))
		os.makedirs(self.cwd)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		session = self.session

		# 1 save state to DB
		cs = self.channel_status

		if exc_type is None:
			cs.status = 'OK'
			cs.error = None
		else:
			if isinstance(exc_val, ChannelBaseError):
				log.info('Channel is down: %s', exc_val)
			else:
				log.error(
					'Channel stream check: unexpected error',
					exc_info=(exc_type, exc_val, exc_tb),
				)

			cs.status = pydash.get(exc_val, 'code', exc_type.__name__)
			# not sure about trace... str(exc_tb)
			cs.error = str(exc_val)

		cs.ts = arrow.get().datetime

		session.add(cs)
		session.commit()

		# 2 rm temporary dir
		if self.__cleanup_dir:
			log.debug('Cleanup dir [%s]', self.cwd)
			shutil.rmtree(self.cwd)

		log.info('status of [%s] checked', self.channel.name)
		return True

	def check(self):

		filename = 'chunk'

		# CHECK CHANNEL
		ts_file = os.path.join(self.cwd, '{}.ts'.format(filename))

		capture_cmd = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=self.config.capture_address,
			cwd=self.cwd,
			out=ts_file,
			timeout_sec=self.DEMO_CAPTURING_TIMEOUT_SEC,
		)
		capture_res = capture_cmd.run()
		capture_exc = capture_res.get('exc')

		if capture_exc:
			raise capture_exc

		# TEST 1.1: file size
		ts_file_size = os.path.getsize(ts_file)
		if ts_file_size < 10:
			raise ChannelStreamEmptyError(('Channel\'s stream is empty:'
				' captured {:d} bytes during {:d} seconds').format(
					ts_file_size,
					self.DEMO_CAPTURING_TIMEOUT_SEC,
			))

		# TEST 2: ffprobe
		vinfo_cmd = GetVideoInfoCommand(inp=ts_file, cwd=self.cwd, timeout_sec=10)
		vinfo_res = vinfo_cmd.run()

		vformat_name = pydash.get(vinfo_res, 'out.format.format_name')
		log.debug('Channel [%s] stream format: [%s]', self.channel.name, vformat_name)

		if vformat_name != 'mpegts':
			raise ChannelCorruptedError('Unexpected stream format: {}'.format(vformat_name))

		vinfo_exc = vinfo_res.get('exc')
		if vinfo_exc:
			raise vinfo_exc

		# ffprobe_cmd = Command('ffprobe -loglevel error {}.ts'.format(filename), cwd=self.cwd, out='PIPE')
		# ffprobe_res = ffprobe_cmd.run()
		# ffprobe_exc = ffprobe_res.get('exc')
		# ffprobe_out = ffprobe_res.get('out')
		# ffprobe_rc = ffprobe_res.get('rc')

		# # TODO: improve error handling (RC vs STDERR)
		# if ffprobe_exc:
		# 	raise ffprobe_exc

		# if ffprobe_rc:
		# 	raise ChannelCorruptedError(ffprobe_out)

		# TEST 3: ccexctractor
		ccexctractor_cmd = Command('ccextractor -xmltv -out=null {}.ts'.format(filename), cwd=self.cwd)
		ccexctractor_res = ccexctractor_cmd.run()
		ccexctractor_exc = ccexctractor_res.get('exc')

		if ccexctractor_exc:
			raise ccexctractor_exc

		# output-file created by ccextractor:
		epg_file = os.path.join(self.cwd, '{}_epg.xml'.format(filename))

		cmd = '/usr/bin/curl -s -u novik:184412 -F do=upload -F "file_data=@${epg_file}" http://epgtests.xirvik.com/fm/'.format(
			epg_file=epg_file,
		)
		curl_cmd = Command(cmd, cwd=self.cwd)
		curl_res = curl_cmd.run()
		curl_exc = curl_res.get('exc')

		if curl_exc:
			raise curl_exc


def start(app_config):

	# TODO: remove connection_string from meta
	# IMPORTANT: it POPS connection string!
	# connection_string = job_meta.pop('connection_string')
	connection_string = app_config.connection_string
	session = get_session(connection_string)
	ids = [channel.ID for channel in session.query(Channel)]

	for channel_id in ids:
		with ChannelChecker(app_config, channel_id) as checker:
			checker.check()
