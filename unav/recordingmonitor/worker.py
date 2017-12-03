# -*- coding: utf-8 -*-

import os

import re
import logging
import arrow

import pydash
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.pool import ThreadPoolExecutor

from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# EVENTS
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.events import EVENT_JOB_ERROR

# EVENT_ALL_JOBS_REMOVED    All jobs were removed from either all job stores or one particular job store
# 							SchedulerEvent
# EVENT_JOB_ADDED	        A job was added to a job store	JobEvent
# EVENT_JOB_REMOVED         A job was removed from a job store	JobEvent
# EVENT_JOB_MODIFIED        A job was modified from outside the scheduler	JobEvent
# EVENT_JOB_SUBMITTED       A job was submitted to its executor to be run	JobSubmissionEvent
# EVENT_JOB_MAX_INSTANCES   A job being submitted to its executor was not accepted by the executor because
#                           the job has already reached its maximum concurrently executing instances
#                           JobSubmissionEvent
# EVENT_JOB_EXECUTED        A job was executed successfully	JobExecutionEvent
# EVENT_JOB_ERROR           A job raised an exception during execution	JobExecutionEvent
# EVENT_JOB_MISSED          A job’s execution was missed	JobExecutionEvent
# EVENT_ALL                 A catch-all mask that includes every event type

from .typeconv import str2bool
from .errors import ConfigureJobError

from .jobs.maintenance.free_space import FreeSpaceJobResultProcessor
from .jobs.maintenance.channel_on_air import ChannelOnAirJobResultProcessor
from .jobs.result_processor import BaseJobResultProcessor


log = logging.getLogger(__name__)


class ScheduledWorker:

	__re_clean = re.compile('[^-_\w\d]', flags=re.A | re.I)

	def __init__(self, app_config):

		# config:
		connection_string = app_config.connection_string
		tzname = str(app_config.get('scheduler.tz', 'utc'))
		jobs_limit = int(app_config.get('scheduler.jobsLimit', 10))
		jobs_root = str(app_config.get('capture.paths.jobsRoot'))

		# TODO: remove this option! use per-task options
		maintenance_enabled = str2bool(app_config.get('maintenance.enabled'))
		# TODO: remove this option, count enabled tasks
		maintenance_jobs_limit = int(app_config.get('maintenance.jobsLimit'))

		# create root directory for jobs temporary files
		os.makedirs(jobs_root, exist_ok=True)

		jobstores = {
			'default': SQLAlchemyJobStore(url=connection_string),
		}

		executors = {
			# we are going to decode-encode video streams. That is why ProcessPool utilized.
			'default': ProcessPoolExecutor(jobs_limit),
		}

		if maintenance_enabled:
			jobstores['maintenance'] = MemoryJobStore()
			executors['maintenance'] = ThreadPoolExecutor(maintenance_jobs_limit)

		job_defaults = {
			'coalesce': False,
			'max_instances': 1,
		}
		s = BackgroundScheduler()
		self._scheduler = s
		self._tz = timezone(tzname)
		self.jobs_root = jobs_root

		self._scheduler.configure(
			jobstores=jobstores,
			executors=executors,
			job_defaults=job_defaults,
			timezone=self._tz,
		)

		log.info('scheduler configured, timezone=[%s]', self._tz)

		# ----------------------------------------------------------------------
		# connect event listeners
		# ----------------------------------------------------------------------
		self._connect_listeners(app_config)

		# TODO: remove __app_config
		self.__app_config = app_config

		# ----------------------------------------------------------------------
		# add maitenance jobs
		# ----------------------------------------------------------------------
		if maintenance_enabled:
			self._add_maintenance_jobs(app_config)

	def _connect_listeners(self, app_config):
		s = self._scheduler

		executed_listener = JobExecutedEventHandler(app_config)
		s.add_listener(executed_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

		# s.add_listener(
		# 	event_broadcasting,
		# 	EVENT_JOB_ADDED | EVENT_JOB_SUBMITTED | EVENT_JOB_MODIFIED
		# )

	def _add_maintenance_jobs(self, app_config):

		jobs = app_config.get('maintenance.jobs')
		if not isinstance(jobs, dict):
			raise ValueError('Config: maintenance.jobs must be a dict')

		for name, config in jobs.items():
			job_type = config['type']
			interval_min = int(config.get('interval', '30'))

			trig = IntervalTrigger(
				minutes=interval_min,
				start_date=arrow.get().shift(seconds=5).datetime,
				timezone=self._tz,
			)

			# TODO: it is not a good idea to pass the entire app_config to the job. But it's the fastest way for implementation
			all_job_args = [app_config]

			fn = 'unav.recordingmonitor.jobs.maintenance.{}:start'.format(job_type)

			self._scheduler.add_job(
				fn,
				trigger=trig,
				args=all_job_args,
				id=job_type,
				name=job_type,
				coalesce=True,
				max_instances=1,
				jobstore='maintenance',
				executor='maintenance',
				replace_existing=True,
			)

			log.debug(
				'maintenance task [%s] of type [%s] added with interval [%s] minutes',
				name,
				job_type,
				interval_min
			)

	def run(self):
		self._scheduler.start()

	def shutdown(self, wait=True):
		self._scheduler.shutdown(wait)

	def job_list(self):
		'''
		List all known jobs

		Result contains:

		- id
		- name
		- next_run_time

		.. seealso::

			https://apscheduler.readthedocs.io/en/latest/modules/job.html#apscheduler.job.Job

		:returns: List of jobs
		:rtype: list<Job>
		'''
		return self._scheduler.get_jobs(jobstore='default')

	def job_add(self, job_info_model):
		'''
		Add a job to scheduler

		[description]
		:param job_info: Job information
		:type job_info: ~.models.jobs.JobInfo
		:returns: scheduler job
		:rtype: apscheduler.job.Job
		:raises: HandleJobError
		'''

		ji = job_info_model

		job_info_ID = ji.ID
		template_name = ji.template_name
		date_from = ji.date_from
		duration_sec = ji.duration_sec
		channel_ID = ji.channel_ID
		job_params = ji.job_params
		repeat = ji.repeat

		tpl_name = self.__re_clean.sub('', template_name)

		if tpl_name:
			tpl_path = 'jobs.templates.{}'.format(tpl_name)
			job_type_path = 'jobs.templates.{}.type'.format(tpl_name)

			log.debug('creating a job using a template [%s]', tpl_path)
			template_config = self.__app_config.get(tpl_path)
			job_type = self.__app_config.get(job_type_path)
		else:
			job_type = None

		if not job_type:
			log.error('Job with unknown template [%s] requested', tpl_name)
			raise ConfigureJobError(
				'Job with unknown template',
				template_name=tpl_name
			)

		fn_name = 'unav.recordingmonitor.jobs.templates.{}:start'.format(job_type)

		trig = _create_trigger_from_repeat(date_from, repeat, self._tz)
		log.debug('trigger for job [%s]', trig)

		missfire_sec = duration_sec

		eff_job_params = {}
		eff_job_params.update(job_params)

		# predefined system params:
		eff_job_params.update({
			'job_ID': job_info_ID,
			'job_main_duration_sec': duration_sec,
			'job_root_dir': self.jobs_root,
			'job_rmdir': self.__app_config.get('capture.rmdir', True),

			'channel_ID': channel_ID,

			'connection_string': self.__app_config.connection_string,

			# TODO: remove, bcz it is necessary only for "capturing" job:
			'capture_address': self.__app_config.get('capture.address'),
		})

		# IMPORTANT: must be serializable!
		all_job_args = [template_config, eff_job_params]

		# add_job(
		# 	func,
		# 	trigger=None,
		# 	args=None,
		# 	kwargs=None,
		# 	id=None,
		# 	name=None,
		# 	misfire_grace_time=undefined,
		# 	coalesce=undefined,
		# 	max_instances=undefined,
		# 	next_run_time=undefined,
		# 	jobstore='default',
		# 	executor='default',
		# 	replace_existing=False,
		# 	**trigger_args
		# )

		sj = self._scheduler.add_job(
			fn_name,
			trigger=trig,
			args=all_job_args,
			name=str(job_info_ID),
			misfire_grace_time=missfire_sec,
			coalesce=True,
			jobstore='default',
			replace_existing=True,
		)

		log.info(
			'job added: name [%s] template[%s] start at [%s], trigger [%s]',
			ji.name,
			ji.template_name,
			ji.date_from,
			trig,
		)

		return sj

	def job_remove(self, ID):

		self._scheduler.remove_job(ID)


def _create_trigger_from_repeat(date_from, repeat, tz):

	def _pop_date_trim(obj):
		_str = obj.pop('date_trim', None)
		if _str is None:
			return None

		return arrow.get(_str).datetime

	_dt = date_from.datetime
	# TODO: try to create PYTZ timezone from DT...
	#_tz = arrow2pytz(date_from.tzinfo) # or tz
	_tz = tz

	_cron = pydash.get(repeat, 'cron')
	_interval = pydash.get(repeat, 'interval')

	if _cron:
		_cron['start_date'] = _dt
		_cron['end_date'] = _pop_date_trim(_cron)
		_cron['timezone'] = _tz
		trig = CronTrigger(**_cron)
	elif _interval:
		_interval['start_date'] = _dt
		_interval['end_date'] = _pop_date_trim(_interval)
		_interval['timezone'] = _tz
		trig = IntervalTrigger(**_interval)
	else:
		trig = DateTrigger(
			run_date=_dt,
			timezone=_tz
		)

	return trig


class JobExecutedEventHandler:

	def __init__(self, app_config):
		self.base_job_result_processor = BaseJobResultProcessor(app_config)

		self.job_result_processors = {
			FreeSpaceJobResultProcessor.KIND: FreeSpaceJobResultProcessor(app_config),
			ChannelOnAirJobResultProcessor.KIND: ChannelOnAirJobResultProcessor(app_config),
		}

	def __call__(self, event):
		# event: apscheduler.events.JobExecutionEvent

		# code – the type code of this event
		# alias – alias of the job store or executor that was added or removed (if applicable)
		# job_id – identifier of the job in question
		# jobstore – alias of the job store containing the job in question
		# scheduled_run_time – the time when the job was scheduled to be run
		# retval – the return value of the successfully executed job
		# exception – the exception raised by the job
		# traceback

		log.debug('APScheduler Event: job executed [%s]', event.job_id)

		# TODO: don't use KIND as a type-detector, use JOB data to differentiate
		job_kind = pydash.get(event.retval, 'kind')

		proc = self.job_result_processors.get(job_kind)
		if not proc:
			proc = self.base_job_result_processor

		proc.handle_event(
			event.retval,
			event.exception,
			event.traceback
		)
