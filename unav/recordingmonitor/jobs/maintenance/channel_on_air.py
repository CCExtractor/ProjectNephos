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

from ...env import cwd as get_cwd
from ...models.tv import Channel
from ...models.tv import ChannelStatus
from ...db import get_session
#from ...errors import MaintenanceError
from ...errors import BaseError

# from ...utils.string import format_with_emptydefault

from ..syscommand import Command
from ..syscommand import CaptureCommand


log = logging.getLogger(__name__)


class StreamCorruptedError(BaseError):
	pass


class ChannelChecker:
	def __init__(self, app_config, channel_id):

		# BUG: move to ./worker.py
		self.path_var = app_config.get('capture.paths.base')

		# TODO: use class, not type()
		self.config = type('__internal_config', (), {})
		# TODO: remove connection_string from meta
		self.config.connection_string = app_config.connection_string
		self.config.capture_address = app_config.get('capture.address')

		self.channel_id = channel_id

		self.ID = str(uuid.uuid4())

		self.session = None
		self.cd = None
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
		self.cd = os.path.join(self.path_var, 'maintenance', 'channel_on_air', str(self.ID))
		os.makedirs(self.cd)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		session = self.session

		# 1 save state to DB
		cs = self.channel_status

		if exc_type is None:
			cs.status = 'OK'
			cs.error = None
		else:
			cs.status = pydash.get(exc_val, 'code', exc_type.__name__)
			# not sure about trace... str(exc_tb)
			cs.error = str(exc_val)

		cs.ts = arrow.get().datetime

		session.add(cs)
		session.commit()

		# 2 rm temporary dir
		shutil.rmtree(self.cd)

		log.info('status of [%s] checked', self.channel.name)
		return True

	def check(self):

		filename = 'chunk'

		# CHECK CHANNEL
		ts_file = os.path.join(self.cd, '{}.ts'.format(filename))

		capture_cmd = CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=self.config.capture_address,
			cwd=self.cd,
			out=ts_file,
			timeout_sec=10,
			logger=log,
		)
		capture_res = capture_cmd.run()
		capture_exc = capture_res.get('exc')

		if capture_exc:
			raise capture_exc

		# TEST 2: ffprobe
		ffprobe_cmd = Command('ffprobe -loglevel error {}.ts'.format(filename), cwd=self.cd, out='PIPE', logger=log)
		ffprobe_res = ffprobe_cmd.run()
		ffprobe_exc = ffprobe_res.get('exc')
		ffprobe_out = ffprobe_res.get('out')
		ffprobe_rc = ffprobe_res.get('rc')

		if ffprobe_exc:
			raise ffprobe_exc

		if ffprobe_rc:
			raise StreamCorruptedError(ffprobe_out)

		# TEST 3: ccexctractor
		ccexctractor_cmd = Command('ccextractor -xmltv -out=null {}.ts'.format(filename), cwd=self.cd, logger=log)
		ccexctractor_res = ccexctractor_cmd.run()
		ccexctractor_exc = ccexctractor_res.get('exc')

		if ccexctractor_exc:
			raise ccexctractor_exc

		# output-file created by ccextractor:
		epg_file = os.path.join(self.cd, '{}_epg.xml'.format(filename))

		cmd = '/usr/bin/curl -s -u novik:184412 -F do=upload -F "file_data=@${epg_file}" http://epgtests.xirvik.com/fm/'.format(
			epg_file=epg_file,
		)
		curl_cmd = Command(cmd, cwd=self.cd, logger=log)
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
