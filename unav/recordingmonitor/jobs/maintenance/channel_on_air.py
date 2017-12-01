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

from ..result_processor import BaseJobResultProcessor

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


class ChannelStreamIsEmptyError(ChannelBaseError):
	pass


class ChannelCorruptedError(ChannelBaseError):
	pass


class ChannelChecker:

	DEMO_CAPTURING_TIMEOUT_SEC = 6

	def __init__(self, app_config, channel_ID):

		# BUG: move to ./worker.py
		self.path_var = app_config.get('capture.paths.jobsRoot')

		self.__cleanup_dir = app_config.get('maintenance.rmdir')

		# TODO: use class, not type()
		self.config = type('__internal_config', (), {})
		# TODO: remove connection_string from meta
		self.config.connection_string = app_config.connection_string
		self.config.capture_address = app_config.get('capture.address')

		self.channel_ID = channel_ID

		self.ID = str(uuid.uuid4())

		self.session = None
		self.cwd = None
		self.channel_status = None
		self.res = None

	def __enter__(self):

		session = get_session(self.config.connection_string)
		self.session = session

		self.channel = session.query(Channel).get(self.channel_ID)
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

		old_status = cs.status
		old_error = cs.error

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

		# 3 save result:
		self.res = {
			'channel_ID': self.channel_ID,
			'ts': cs.ts,
			'old': {
				'status': old_status,
				'error': old_error,
			},
			'new': {
				'status': cs.status,
				'error': cs.error,
			}
		}

		return True

	def check(self):

		filename = 'chunk'
		ts_file = os.path.join(self.cwd, '{}.ts'.format(filename))
		epg_file = os.path.join(self.cwd, '{}_epg.xml'.format(filename))

		# CHECK CHANNEL
		capture_cmd = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=self.config.capture_address,
			cwd=self.cwd,
			out=ts_file,
			timeout_sec=self.DEMO_CAPTURING_TIMEOUT_SEC,
		)
		capture_cmd.run()

		# TEST 1.1: file size
		ts_file_size = os.path.getsize(ts_file)
		if ts_file_size < 10:
			raise ChannelStreamIsEmptyError(('Channel\'s stream is empty:'
				' captured {:d} bytes during {:d} seconds').format(
					ts_file_size,
					self.DEMO_CAPTURING_TIMEOUT_SEC,
			))

		# TEST 2: ffprobe
		vinfo_cmd = GetVideoInfoCommand(inp=ts_file, cwd=self.cwd, timeout_sec=10)
		vinfo_res = vinfo_cmd.run()

		vformat_name = pydash.get(vinfo_res.stdout, 'format.format_name')
		log.debug('Channel [%s] stream format: [%s]', self.channel.name, vformat_name)

		if vformat_name != 'mpegts':
			raise ChannelCorruptedError('Unexpected stream format: {}'.format(vformat_name))

		# TEST 3: ccexctractor
		ccexctractor_cmd = Command('ccextractor -xmltv -out=null {}'.format(ts_file), cwd=self.cwd)
		ccexctractor_cmd.run()

		# output-file created by ccextractor:
		cmd = '/usr/bin/curl -s -u novik:184412 -F do=upload -F "file_data=@${epg_file}" http://epgtests.xirvik.com/fm/'.format(
			epg_file=epg_file,
		)

		curl_cmd = Command(cmd, cwd=self.cwd)
		curl_cmd.run()


def start(app_config):

	# TODO: remove connection_string from meta
	# IMPORTANT: it POPS connection string!
	# connection_string = job_meta.pop('connection_string')
	connection_string = app_config.connection_string
	session = get_session(connection_string)
	ids = [str(channel.ID) for channel in session.query(Channel)]

	_channels_result = {}

	for channel_id in ids:
		with ChannelChecker(app_config, channel_id) as checker:
			checker.check()

		_channels_result[channel_id] = checker.res

	# {
	#   kind: 'channel_on_air',
	#   data: {
	#     channel_uuid: {
	#       ts: datetime,
	#       channel_ID: str(uuid),
	#       old: {
	#         status: 'OK',
	#         error: null,
	#       },
	#       new: {
	#         status: 'OK',
	#         error: null,
	#       }
	#     },
	#     ...
	#   }
	# }
	return {
		'kind': ChannelOnAirJobResultProcessor.KIND,

		'data': _channels_result,
	}


class ChannelOnAirJobResultProcessor(BaseJobResultProcessor):
	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.maintenance.channel_on_air'

	def handle_data(self, data):

		channels_went_down = []
		channels_stay_down = []
		channels_went_up = []

		def _ok(st):
			return st == 'OK'

		ts = None

		for channel_ID_str, channel_info in data.items():
			old_st = pydash.get(channel_info, 'old.status')
			new_st = pydash.get(channel_info, 'new.status')

			old_ok = _ok(old_st)
			new_ok = _ok(new_st)

			ts = pydash.get(channel_info, 'ts')

			if old_ok and not new_ok:
				channels_went_down.append({
					'name': 'TODO: fill channel name',
					'channel_ID': channel_ID_str,
					'channel_status': new_st,
				})
			elif not old_ok and not new_ok:
				channels_stay_down.append({
					'name': 'TODO: fill channel name',
					'channel_ID': channel_ID_str,
					'channel_status': new_st,
				})
			elif not old_ok and new_ok:
				channels_went_up.append({
					'name': 'TODO: fill channel name',
					'channel_ID': channel_ID_str,
					'channel_status': new_st,
				})

		something_changed = len(channels_went_down) + len(channels_went_up)
		down_counter = len(channels_stay_down)

		if something_changed > 0:
			# notify about changes
			self.notify_signal.send(
				self.KIND,
				notification_code='channels_statuses_changed',
				data={
					'ts': ts,
					'channels_went_down': channels_went_down,
					'channels_stay_down': channels_stay_down,
					'channels_went_up': channels_went_up,
				},
			)
		elif down_counter > 0:
			self.notify_signal.send(
				self.KIND,
				notification_code='channels_statuses_are_down',
				data={
					'ts': ts,
					'channels_went_down': channels_went_down,
					'channels_stay_down': channels_stay_down,
					'channels_went_up': channels_went_up,
				},
			)
		else:
			log.debug('ChannelOnAirJobResultProcessor: no changes in channels statuses')

	# def handle_error(cls, exc, tb_str):
	# 	pass
