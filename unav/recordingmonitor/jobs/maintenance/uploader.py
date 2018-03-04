# -*- coding: utf-8 -*-

'''
Post-processing for ccaptured streams

'''

import os
import uuid
import datetime
import json

import arrow
import pydash

from ..commands import Command
from ..commands import VideoInfoCommand
from ..commands import ExtractCaptionsCommand
from ..result_processor import BaseJobResultProcessor

from ...db import get_session
from ...models.tv import Channel

from ...utils.string import word_count
from ...utils.string import format_with_emptydefault


class UploaderTask:

	def __init__(self, app_config):

		# BUG: move to ./worker.py
		self.jobs_root = app_config.get('capture.paths.jobsRoot')

		self.__cleanup_dir = app_config.get('capture.rmdir')

		# TODO: use class, not type()
		self.config = type('__internal_uploader_config', (), {})
		# TODO: remove connection_string from meta
		self.config.connection_string = app_config.connection_string

		self.ID = str(uuid.uuid4())

		self.session = None
		self.cwd = None
		self.res = None

	def __enter__(self):

		session = get_session(self.config.connection_string)
		self.session = session

		# 2 create temporary dir
		self.cwd = os.path.join(self.jobs_root, 'uploader')
		os.makedirs(self.cwd)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		session = self.session

		# 1 save state to DB
		if exc_type is None:
			pass
		else:
			self.log.error(
				'Uploader: error occured',
				exc_info=(exc_type, exc_val, exc_tb),
			)

		session.commit()

		# 3 save result:
		self.res = {}
		return True

	def _is_info_file(self, name):
		if name is None:
			return False
		return name.lower().endswith('.task.json')

	def process_all_files(self):

		for (dirpath, dirnames, filenames) in os.walk(self.cwd):
			files = [fn for fn in filenames if self._is_info_file(fn)]

			for fn in files:
				meta = None
				with open(os.path.join(self.cwd, fn)) as fp:
					meta = json.load(fp)

				self.process_one_file(meta)

	def process_one_file(self, meta):

		filename           = meta['filename']        # noqa: E221
		channel_ID         = meta['channel_ID']      # noqa: E221
		date_from          = meta['date_from']       # noqa: E221
		job_params         = meta['job_params']      # noqa: E221
		job_launch_ID      = meta['job_launch_ID']   # noqa: E221

		self.log.info('start uploading [%s]', filename)

		session = self.session
		channel = session.query(Channel).get(channel_ID)

		filename_out = filename + '.ts'
		filename_len = filename + '.len'
		filename_txt = filename + '.txt'

		# commands from check-cc-single
		# ======================================================================
		# STEP: get video info
		# ======================================================================
		res_capinfo = self._run_cmd(VideoInfoCommand(
			inp=filename_out,
			cwd=self.cwd
		))

		# 1a Duration
		_video_duration_seconds = float(pydash.get(res_capinfo.stdout, 'format.duration'))
		self.log.info('Video duration is %s', _video_duration_seconds)

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
		_meta_timezone =       job_params.get('timezone')            or channel.meta_timezone          # noqa: E272, E222
		_meta_teletext_page =  job_params.get('meta_teletext_page')  or channel.meta_teletext_page     # noqa: E272, E222
		# _meta_country_code =   job_params.get('meta_country_code')   or channel.meta_country_code      # noqa: E272, E222
		_meta_language_code3 = job_params.get('meta_language_code3') or channel.meta_language_code3    # noqa: E272, E222
		_meta_video_source =   job_params.get('meta_video_source')   or channel.meta_video_source      # noqa: E272, E222

		# ======================================================================
		# STEP: extract subtitles
		# ======================================================================
		subs = self._extract_subs_with_ccextractor(
			inp=filename_out,
			tp=_meta_teletext_page,
			date_from=date_from,
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
				'unav\t{CCWORDS}\t{CCWORDS2}\t{CCDIFF}\t{ScheDUR}\t{ffDURs}\t{TIMDIFF}\t{filename_out}'
			).format(
				CCWORDS=wc,
				CCWORDS2=0,
				CCDIFF=-wc,
				ScheDUR=_video_duration_seconds,
				ffDURs=_video_duration_seconds,
				TIMDIFF=0,
				filename_out=filename_out,
			)
			flen.write(_len_txt)

		# ======================================================================
		# STEP: save .txt meta file
		# ======================================================================

		with open(os.path.join(self.cwd, filename_txt), 'w') as ftxt:

			_LBT = arrow.get(date_from).to(_meta_timezone or 'local').format('YYYY-MM-DD HH:mm:ss')

			_txt_header = (
				'TOP|{date_from:%Y%m%d%H%M%S}|{filename_out}\n'     # TOP|20170811210000|2017-08-11_2100_ES_Antena-3_Noticias_Deportes_El_tiempo
				'COL|{description}\n'                               # COL|Communication Studies Archive, UCLA
				'UID|{uid}\n'                                       # UID|0339184e-7ee6-11e7-8fb0-005056b6e57b
				'DUR|{duration}\n'                                  # DUR|00:00:00
				'VID|{scaled_size}|{picture_size}\n'                # VID|640x352|1920x1080
				'SRC|{source}\n'                                    # SRC|Universidad de Navarra, Spain
				'CMT|{CMT}\n'                                       # CMT|     - what the FUCK IS THIS!!!!
				'LAN|{language_code3}\n'                            # LAN|SPA
				'LBT|{local_from_date}\n'                           # LBT|2017-08-11 23:00:00 CEST Europe/Madrid
				'END|{date_from:%Y%m%d%H%M%S}|{filename_out}\n'     # END --- SAME AS TOP
			).format(
				date_from=date_from,
				filename_out=filename_out,
				description='Communication Studies Archive, UCLA',
				uid=job_launch_ID,
				duration=datetime.timedelta(seconds=_video_duration_seconds),
				scaled_size=_scaled_size,
				picture_size=_picture_size,
				source=_meta_video_source,
				CMT='',
				language_code3=_meta_language_code3,
				local_from_date='{} {}'.format(_LBT, _meta_timezone),  # because ARROW can't handle ZZZ correctly
			)

			ftxt.write(_txt_header)
			ftxt.write(subs)

		# # ----------------------------------------------------------------------
		# # UPLOAD
		# # ----------------------------------------------------------------------

		# note: create remote dir
		cmd1 = format_with_emptydefault(
			'ssh ca mkdir -p ES/{job_launch_date_from:%Y}/{job_launch_date_from:%Y%m}/{job_launch_date_from:%Y%m%d}',
			job_params
		)
		self._run_cmd(Command(cmd=cmd1, cwd=self.cwd))

		# note: sync remote dir
		cmd2 = format_with_emptydefault(
			'rsync -v --progress {out_filename_noext}.ts {out_filename_noext}.txt {out_filename_noext}.len ca:ES/{job_launch_date_from:%Y}/{job_launch_date_from:%Y%m}/{job_launch_date_from:%Y%m%d}',
			job_params
		)
		self._run_cmd(Command(cmd=cmd2, cwd=self.cwd))

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

	def _extract_subs_with_ccextractor(self, inp, tp, date_from):

		utc_ts = arrow.get(date_from).timestamp
		cc_params1 = '-datets -unixts {0}'.format(utc_ts)

		ccextractor_prms = [
			['ccextractor',          tp,   cc_params1],
			['ccextractor',          None, cc_params1],
			['ccextractor-0.69-a02', tp,   '-delay 0 -ts'],
			['ccextractor-0.69-a02', None, '-delay 0 -ts'],
		]

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


def start(app_config):

	ret = None

	with UploaderTask(app_config) as handler:
		ret = handler.process_all_files()

	return {
		'kind': UploaderJobResultProcessor.KIND,

		'data': ret
	}


class UploaderJobResultProcessor(BaseJobResultProcessor):

	# TODO: use package name
	KIND = 'unav.recordingmonitor.jobs.maintenance.uploader'

	def __init__(self, app_config):
		super().__init__(app_config)

	def handle_data(self, data):
		# self.notify_signal.send(
		# 	self.KIND,
		# 	notification_code='low_space',
		# 	data={
		# 	},
		# )

		pass

	def handle_error(cls, exc, tb_str):
		pass
