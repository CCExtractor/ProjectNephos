# -*- coding: utf-8 -*-

'''
Check that all channels are on air
'''

import os
import shutil
import logging
import datetime

import uuid

from ...env import cwd as get_cwd
from ...models.tv import Channel
from ...models.tv import ChannelStatus
from ...db import get_session
#from ...errors import MaintenanceError

from ...utils.string import format_with_emptydefault

from ..syscommand import Command


log = logging.getLogger(__name__)


# IP_IPTV="159.237.36.240"


class ChannelChecker:
	def __init__(self, job_meta, job_params, channel, session):
		self.meta = job_meta
		self.pm = job_params
		self.channel = channel
		self.session = session

		self.id = str(uuid.uuid4())

		self.cd = None
		self._channel_status = None

	def __enter__(self):
		log.info('start checking status of [%s]', self.channel.name)
		session = self.session

		# 1 init status in DB (if not exist yet)
		cs = self.channel.channel_status
		if cs is None:
			cs = ChannelStatus()
			cs.channel = self.channel
			session.add(cs)
			session.commit()
		self._channel_status = cs

		# 2 create temporary dir
		self.cd = os.path.join(get_cwd(), 'var', 'maintenance', 'channel_on_air', str(self.id))
		os.makedirs(self.cd)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		session = self.session
		print('*' * 40)
		print('*' * 40)
		print('DEBUG')
		print('*' * 40)
		print('*' * 40)
		# shutil.rmtree(self.cd)

		cs = self._channel_status

		if exc_type is None:
			cs.status = 'OK'
			cs.error = None
		else:
			cs.status = exc_type.__name__
			cs.error = str(exc_val)  # + str(exc_tb)

		cs.ts = datetime.datetime.now()

		session.add(cs)
		session.commit()

		log.info('status of [%s] checked', self.channel.name)
		return True

	def check(self):

		filename = 'chunk'

		# CHECK CHANNEL
		ts_file = os.path.join(self.cd, '{}.ts'.format(filename))

		# TEST 1: multicat
		cmd = format_with_emptydefault('multicat -u @{channel_ip}/ifaddr={iface} {ts_file}', {
			'channel_ip': self.channel.ip_string,
			'iface': 'eth0', # iface,
			'ts_file': ts_file,
		})

		print('*' * 40)
		print('*' * 40)
		print('DEBUG')
		print('*' * 40)
		print('*' * 40)
		cmd = format_with_emptydefault('ping {channel_ip} # {ts_file}', {
			'channel_ip': self.channel.ip_string,
			'ts_file': ts_file,
		})

		multicat_cmd = Command(cmd=cmd, cwd=self.cd, out=ts_file, timeout_sec=10, logger=log)
		multicat_res = multicat_cmd.run()
		multicat_exc = multicat_res.get('exc')

		if multicat_exc:
			raise multicat_exc

		# TEST 2: ffprobe
		ffprobe_cmd = Command('ffprobe {}.ts'.format(filename), cwd=self.cd, out='PIPE', logger=log)
		ffprobe_res = ffprobe_cmd.run()
		ffprobe_exc = ffprobe_res.get('exc')
		ffprobe_out = ffprobe_res.get('out')

		if ffprobe_exc:
			raise ffprobe_exc

		if not ffprobe_out.startswith('Input #0, mpegts'):
			raise Exception('ffprobe: stream corrupted')

		# TEST 3: ccexctractor
		ccexctractor_cmd = Command('ccextractor -xmltv -out=null {}.ts'.format(filename), cwd=self.cd, logger=log)
		ccexctractor_res = ccexctractor_cmd.run()
		ccexctractor_exc = ccexctractor_res.get('exc')

		if ccexctractor_exc:
			raise ccexctractor_exc

		# output from ccextractor
		epg_file = os.path.join(self.cd, '{}_epg.xml'.format(filename))

		# TODO: upload:
		#
		cmd = '/usr/bin/curl -s -u novik:184412 -F do=upload -F "file_data=@${epg_file}" http://epgtests.xirvik.com/fm/'.format(
			epg_file=epg_file,
		)
		curl_cmd = Command(cmd, cwd=self.cd, logger=log)
		curl_res = curl_cmd.run()
		curl_exc = curl_res.get('exc')

		if curl_exc:
			raise curl_exc

		return None


def start(job_meta, job_params):

	# TODO: remove connection_string from meta
	# IMPORTANT: it POPS connection string!
	# connection_string = job_meta.pop('connection_string')
	connection_string = job_meta['connection_string']

	print('connection_string', connection_string)
	session = get_session(connection_string)

	for ch in session.query(Channel):
		with ChannelChecker(job_meta, job_params, ch, session) as checker:
			checker.check()
