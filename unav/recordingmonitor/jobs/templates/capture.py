# -*- coding: utf-8 -*-

import os
import datetime

import arrow
import pydash
from logging import getLogger

from ._common import StarterFabric
from .scripttpl import TemplatedScriptJob
from ..commands import CaptureCommand
from ..commands import VideoInfoCommand
from ..commands import ExtractCaptionsCommand

from ...utils.string import format_with_emptydefault
from ...utils.string import word_count

from ...models.tv import Channel

from ..result_processor import BaseJobResultProcessor

log = getLogger(__name__)


class CaptureStreamJob(TemplatedScriptJob):

	def config(self):

		# TODO: remove this;)
		# captured_out = pydash.get(self.template_config, 'main.out', 'stream.ts')
		# captured_out = format_with_emptydefault(captured_out, self.job_params)

		channel_ID = self.job_params['channel_ID']

		self.channel = self.session.query(Channel).get(channel_ID)
		# TODO: check that channel is not NONE

		after_cmd_config_list = self.template_config.get('after')
		if after_cmd_config_list:
			for after_cmd_config in after_cmd_config_list:
				command = self.create_command_from_config(after_cmd_config, self.job_params)
				self.commands_list.append(command)

	def run(self):

		# TODO: remove these lines
		capture_address = self.job_params.get('capture_address')
		filename = format_with_emptydefault(
			'{job_launch_date_from:%Y-%m-%d}_{job_launch_date_from:%H%M}_{job_name_slug}',
			self.job_params
		)
		filename_out = filename + '.ts'
		filename_len = filename + '.len'
		filename_txt = filename + '.txt'

		# ======================================================================
		# MAIN: capture
		# ======================================================================
		# res_capture = self._run_cmd(self.commands__capture)
		self._run_cmd(CaptureCommand(
			channel_ip=self.channel.ip_string,
			ifaddr=capture_address,
			cwd=self.cwd,
			out=filename_out,
			timeout_sec=self.duration_sec,
		))

		# commands from check-cc-single
		# ======================================================================
		# STEP: get video info
		# ======================================================================
		res_capinfo = self._run_cmd(VideoInfoCommand(
			inp=filename_out,
			cwd=self.cwd
		))

		# 1a Duration (in hours)
		_video_duration_hours = float(pydash.get(res_capinfo.stdout, 'format.duration'))
		self.log.info('Video duration is %s', _video_duration_hours)

		# 1a Size
		_picture_size = None
		_picture_width = None
		_picture_height = None
		for _stream in pydash.get(res_capinfo.stdout, 'streams', []):
			if not isinstance(_stream, dict):
				continue

			if 'video' == _stream.get('codec_type', '').lower():
				try:
					_picture_width = int(_stream['width'])
					_picture_height = int(_stream['height'])
					_picture_size = '{0}x{1}'.format(_picture_width, _picture_height)
				except TypeError:
					_picture_size = None

				break

		_scaled_size = self._get_scaled_picture_size(
			_picture_width,
			_picture_height,
			_picture_size
		)

		self.log.info('Video size: %s, scaled size: %s', _picture_size, _scaled_size)

		# video meta, taken from the channel-meta. It is default values
		_meta_teletext_page =  self.job_params.get('meta_teletext_page',   self.channel.meta_teletext_page)     # noqa: E222
		#_meta_country_code =   self.job_params.get('meta_country_code',    self.channel.meta_country_code)      # noqa: E222
		_meta_language_code3 = self.job_params.get('meta_language_code3',  self.channel.meta_language_code3)    # noqa: E222
		_meta_timezone =       self.job_params.get('meta_timezone',        self.channel.meta_timezone)          # noqa: E222
		_meta_video_source =   self.job_params.get('meta_video_source',    self.channel.meta_video_source)      # noqa: E222

		# ======================================================================
		# STEP: extract subtitles
		# ======================================================================
		subs = self._extract_subs_with_ccextractor(
			inp=filename_out,
			tp=_meta_teletext_page,
		)

		# ======================================================================
		# STEP: Word count
		# ======================================================================
		wc = self._word_count(subs)

		# ======================================================================
		# STEP: save .len meta file
		# ======================================================================

		with open(os.path.join(self.cwd, filename_len), 'w') as flen:
			# echo -e "unav \t$CCWORDS \t$CCWORDS2 \t$CCDIFF \t$ScheDUR \t$ffDURs \t$TIMDIFF \t$FIL.$EXT" > $FIL.len
			_len_txt = (
				'unav\t{CCWORDS}\t{CCWORDS2}\t{CCDIFF}\t{ScheDUR}\t{ffDURs}\t{TIMDIFF}\t{filename}'
			).format(
				CCWORDS=wc,
				CCWORDS2=0,
				CCDIFF=-wc,
				ScheDUR=_video_duration_hours,
				ffDURs=_video_duration_hours,
				TIMDIFF=0,
				filename=filename,
			)
			flen.write(_len_txt)

		# ======================================================================
		# STEP: save .txt meta file
		# ======================================================================

		with open(os.path.join(self.cwd, filename_txt), 'w') as ftxt:

			_LBT = arrow.get(self.date_from).at(_meta_timezone or 'local').format('YYYY-MM-DD HH:mm:ss')

			_txt_header = (
				'TOP|{%Y%m%d%H%M%S:from_date}|{filename}\n'         # TOP|20170811210000|2017-08-11_2100_ES_Antena-3_Noticias_Deportes_El_tiempo
				'COL|{description}\n'                               # COL|Communication Studies Archive, UCLA
				'UID|{uid}\n'                                       # UID|0339184e-7ee6-11e7-8fb0-005056b6e57b
				'DUR|{duration}\n'                                  # DUR|00:00:00
				'VID|{scaled_size}|{picture_size}\n'                # VID|640x352|1920x1080
				'SRC|{source}\n'                                    # SRC|Universidad de Navarra, Spain
				'CMT|{CMT}\n'                                       # CMT|     - what the FUCK IS THIS!!!!
				'LAN|{language_code3}\n'                            # LAN|SPA
				'LBT|{local_from_date}\n'                           # LBT|2017-08-11 23:00:00 CEST Europe/Madrid
				'END|{%Y%m%d%H%M%S:from_date}|{filename}\n'         # END --- SAME AS TOP
			).format(
				from_date=self.from_date,
				filename=filename,
				description='Communication Studies Archive, UCLA',
				uid=self.job_launch.ID,
				duration=datetime.timedelta(hours=_video_duration_hours),
				scaled_size=_scaled_size,
				picture_size=_picture_size,
				source=_meta_video_source,
				CMT='',
				language_code3=_meta_language_code3,
				local_from_date='{} {}'.format(_LBT, _meta_timezone),  # vecause ARROW can't handle ZZZ correctly
			)

			ftxt.write(_txt_header)
			ftxt.write(subs)

		for cmd in self.commands_list:
			# res = self._run_cmd(cmd)
			self._run_cmd(cmd)

		# return ret.__json__()
		return {
			'kind': CaptureJobResultProcessor.KIND,

			'data': {
				'job_ended': str(self.job_ID),
			}
		}

	def _run_cmd(self, cmd):
		self.log.debug('Command starting', extra={'command': str(cmd)})
		ret = cmd.run()
		self.log.info(
			'Command done', extra={
				'command': str(cmd),
				'result': ret.__json__()
			}
		)
		return ret

	@staticmethod
	def _get_scaled_picture_size(w, h, s):
		_SIZES = {
			'1920x1088': '640x352',  # noqa: E203
			'1920x1080': '640x352',  # noqa: E203
			'1280x720' : '640x352',  # noqa: E203
			'720x576'  : '640x512',  # noqa: E203
			'720x480'  : '640x426',  # noqa: E203
		}

		if s in _SIZES:
			return _SIZES[s]

		return s

	def _extract_subs_with_ccextractor(self, inp, tp):
		ccextractor_prms = tuple(
			('ccextractor',          tp,   '-datets -unixts $BTIM',),
			('ccextractor',          None, '-datets -unixts $BTIM',),
			('ccextractor-0.69-a02', tp,   '-delay 0 -ts',),
			('ccextractor-0.69-a02', None, '-delay 0 -ts',),
		)

		subs = None
		for _cc_app, _cc_tp, _cc_prm in ccextractor_prms:

			res = self._run_cmd(ExtractCaptionsCommand(
				inp=inp,
				cwd=self.cwd,
				app=_cc_app,
				tpage=_cc_tp,
				extra_params=_cc_prm,
			))

			if res.length > 100:
				subs = res.subs
				break

		return subs

	def _word_count(self, subs):
		wc = word_count(subs)
		return wc


class CaptureJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.templates.capture'

	def __init__(self, app_config):
		super().__init__(app_config)

	# def handle_data(self, data):
	# 	pass


start = StarterFabric(CaptureStreamJob)
