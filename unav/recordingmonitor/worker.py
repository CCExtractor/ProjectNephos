# -*- coding: utf-8 -*-

import logging

import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

from apscheduler.triggers.date import DateTrigger

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

log = logging.getLogger(__name__)


def broadcasting(event):
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
	def __init__(self, app_config):

		jobstores = {
			'default': SQLAlchemyJobStore(url=app_config.connection_string)
		}
		executors = {
			'default': ProcessPoolExecutor(app_config.get('scheduler.process_limit')),
		}
		job_defaults = {
			'coalesce': False,
			'max_instances': 1,
		}
		s = BackgroundScheduler()
		self._scheduler = s

		s.add_listener(
			broadcasting,
			EVENT_JOB_ADDED | EVENT_JOB_SUBMITTED | EVENT_JOB_MODIFIED | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
		)

		self._scheduler.configure(
			jobstores=jobstores,
			executors=executors,
			job_defaults=job_defaults,
			timezone=pytz.utc,
		)

		# .. do something else here, maybe add jobs etc.

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
		return self._scheduler.get_jobs()

	def job_add(self, job_info_id, template_name, date_from, date_trim, job_params=None):
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
		func = 'unav.recordingmonitor.jobtemplates.{tpl}'.format(
			tpl=template_name
		)

		trig = DateTrigger(run_date=date_from)

		missfire_sec = int((date_trim - date_from).total_seconds())

		sj = self._scheduler.add_job(
			func,
			args=[job_info_id, job_params],
			trigger=trig,
			name=str(job_info_id),
			misfire_grace_time=missfire_sec,
			coalesce=True,
			replace_existing=True,
		)

		return sj
