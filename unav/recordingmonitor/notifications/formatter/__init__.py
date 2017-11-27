# -*- coding: utf-8 -*-

import logging

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import ChoiceLoader
# from jinja2 import ModuleLoader
# from jinja2 import PackageLoader
# from jinja2 import Template
from jinja2 import select_autoescape

log = logging.getLogger(__name__)


_env = Environment(
	loader=ChoiceLoader([
		FileSystemLoader('./unav/recordingmonitor/notifications/formatter/templates'),
		# ModuleLoader(path)
	]),
	autoescape=select_autoescape(['html', 'xml'])
)


def complile():
	# _env.compile_templates('compiled', log_function=log.error, zip=None)
	pass


def render(template_name, data):
	_t = '{}.html'.format(template_name)
	template = _env.get_template(_t)
	message = template.render(data)

	return message
