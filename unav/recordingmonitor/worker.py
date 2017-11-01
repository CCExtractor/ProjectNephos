# -*- coding: utf-8 -*-

import os

import re
import logging
import datetime

from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.executors.pool import ThreadPoolExecutor

from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# EVENTS
from apscheduler.events import EVENT_JOB_ADDED
from apscheduler.events import EVENT_JOB_SUBMITTED
from apscheduler.events import EVENT_JOB_MODIFIED
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.events import EVENT_JOB_ERROR

# EVENT_ALL_JOBS_REMOVED	All jobs were removed from either all job stores or one particular job store	SchedulerEvent
# EVENT_JOB_ADDED	A job was added to a job store	JobEvent
# EVENT_JOB_REMOVED	A job was removed from a job store	JobEvent
# EVENT_JOB_MODIFIED	A job was modified from outside the scheduler	JobEvent
# EVENT_JOB_SUBMITTED	A job was submitted to its executor to be run	JobSubmissionEvent
# EVENT_JOB_MAX_INSTANCES	A job being submitted to its executor was not accepted by the executor because the job has already reached its maximum concurrently executing instances	JobSubmissionEvent
# EVENT_JOB_EXECUTED	A job was executed successfully	JobExecutionEvent
# EVENT_JOB_ERROR	A job raised an exception during execution	JobExecutionEvent
# EVENT_JOB_MISSED	A job’s execution was missed	JobExecutionEvent
# EVENT_ALL	A catch-all mask that includes every event type

from .env import cwd
from .errors import ConfigureJobError

log = logging.getLogger(__name__)


def event_broadcasting(event):
	log.warn('SCHEDULER EVENT: %s // %s', event.code, event.job_id)
	print(event)

	try:
		print('scheduled_run_times', event.scheduled_run_times)
	except:
		pass

	try:
		print('scheduled_run_time', event.scheduled_run_time)
	except:
		pass

	try:
		print('retval', event.retval)
	except:
		pass

	try:
		print('exception', event.exception)
	except:
		pass

	try:
		print('traceback', event.traceback)
	except:
		pass

	# code – the type code of this event
	# job_id – identifier of the job in question
	# jobstore – alias of the job store containing the job in question


class ScheduledWorker:

	__re_clean = re.compile('[^-_\w\d]', flags=re.A | re.I)

	def __init__(self, app_config):

		# config:
		connection_string = app_config.connection_string
		tz = app_config.get('scheduler.tz', 'utc')
		jobs_limit = int(app_config.get('scheduler.jobsLimit', 10))
		maintenance_jobs_limit = int(app_config.get('scheduler.maintenance.jobsLimit', 10))
		maintenance_interval_min = int(app_config.get('scheduler.maintenance.interval', 30))

		jobstores = {
			'default': SQLAlchemyJobStore(url=connection_string),
			'maintenance': MemoryJobStore(),
		}

		executors = {
			# we are going to decode-encode video streams. That is why ProcessPool utilized.
			'default': ProcessPoolExecutor(jobs_limit),
			'maintenance': ThreadPoolExecutor(maintenance_jobs_limit)
		}
		job_defaults = {
			'coalesce': False,
			'max_instances': 1,
		}
		s = BackgroundScheduler()
		self._scheduler = s
		self.tz = timezone(tz)

		s.add_listener(
			event_broadcasting,
			EVENT_JOB_ADDED | EVENT_JOB_SUBMITTED | EVENT_JOB_MODIFIED | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
		)

		self._scheduler.configure(
			jobstores=jobstores,
			executors=executors,
			job_defaults=job_defaults,
			timezone=self.tz,
		)

		# TODO: remove __app_config
		self.__app_config = app_config

		self._add_system_jobs(maintenance_interval_min)

	def _add_system_jobs(self, interval_min):

		job_types = [
			'free_space',
			'channel_on_air',
		]

		trig = IntervalTrigger(minutes=interval_min)

		print('!' * 40)
		print('!' * 40)
		print('DEBUG')
		print('!' * 40)
		print('!' * 40)
		trig = IntervalTrigger(
			seconds=30,
			start_date=datetime.datetime.now() + datetime.timedelta(seconds=2)
		)

		job_meta = {
			'connection_string': self.__app_config.connection_string,
		}
		job_params = None

		all_job_args = [job_meta, job_params]

		for job_type in job_types:

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

	def run(self):
		self._scheduler.start()

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

		job_info_id = ji.ID
		template_name = ji.template_name
		date_from = ji.date_from
		date_trim = ji.date_trim
		job_params = ji.job_params

		tpl_name = self.__re_clean.sub('', template_name)

		if tpl_name:
			tpl_path = 'jobs.templates.{}'.format(tpl_name)
			job_type_path = 'jobs.templates.{}.type'.format(tpl_name)

			log.debug('creating a job using a template [%s]', tpl_path)
			tpl_params = self.__app_config.get(tpl_path)
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

		trig = DateTrigger(run_date=date_from)
		missfire_sec = int((date_trim - date_from).total_seconds())

		job_dir = os.path.join(cwd(), 'var', 'jobs', str(job_info_id))

		job_meta = {
			'job_id': job_info_id,
			'job_date_from': date_from,
			'job_date_trim': date_trim,
			'job_dir': job_dir,
			'job_rmdir': True,

			'connection_string': self.__app_config.connection_string,
		}

		# IMPORTANT: must be serializable!
		all_job_args = [job_meta, tpl_params, job_params]

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
			name=str(job_info_id),
			misfire_grace_time=missfire_sec,
			coalesce=True,
			jobstore='default',
			replace_existing=True,
		)

		return sj
