# -*- coding: utf-8 -*-

import logging
import traceback

from .models.logs import TaskLogRecord


class SQLAlchemyHandler(logging.Handler):
	'''
	A very basic logger that commits a LogRecord to the SQL Db
	logging to sqlalchemy

	.. seealso::
		https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/logging/sqlalchemy_logger.html

	'''
	def emit(self, record):

		dd = dict(record.__dict__)

		message = record.getMessage()
		trace = None
		exc = record.__dict__['exc_info']
		if exc:
			trace = traceback.format_exc(exc)

		qw = {}
		qw['logger'] = dd.pop('name', None)
		qw['level'] = dd.pop('levelname', None)
		qw['job_info_id'] = dd.pop('job_info_id', None)
		qw['job_template_name'] = dd.pop('job_template_name', None)
		qw['trace'] = trace
		qw['message'] = message
		qw['data'] = dd
		qw['ts'] = dd.pop('created', None)

		# remove redudant fields:
		dd.pop('stack_info', None)
		dd.pop('exc_info', None)
		dd.pop('exc_text', None)
		dd.pop('msg', None)
		dd.pop('levelno', None)
		dd.pop('stack_info', None)
		# should go to the message!
		dd.pop('args', None)

		# print('*' * 80)
		# print('*' * 80)
		# print(json.dumps(qw, indent=4))
		# print('*' * 80)
		# print('*' * 80)

		# {
		#   "filename": "app.py",
		#   "funcName": "run",
		#   "lineno": 56,
		#   "module": "app",
		#   "msecs": 504.58788871765137,
		#   "pathname": "./unav/recordingmonitor/app.py",
		#   "process": 10135,
		#   "processName": "MainProcess",
		#   "relativeCreated": 874.6976852416992,
		#   "thread": 139779874174720,
		#   "threadName": "MainThread"
		# }

		log = TaskLogRecord(**qw)

		log.save()


class ExtendExtraLogAdapter(logging.LoggerAdapter):
	"""
	This will take `extra` from adapter and extends it with `extra` from
	`log` call args.
	"""
	def process(self, msg, kwargs):
		kw = dict(self.extra)
		try:
			kw.update(kwargs['extra'])
		except KeyError:
			pass

		kwargs['extra'] = kw
		return msg, kwargs
