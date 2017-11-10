# -*- coding: utf-8 -*-

import os
import logging
from flask import Blueprint


log = logging.getLogger(__name__)

_static_folder = os.path.join(
	'dist/'
)

ui_blueprint = Blueprint(
	'ui',
	__name__,
	static_folder=_static_folder,
	static_url_path='',
	template_folder='templates',
)

# @ui_blueprint.errorhandler(404)
# def page_not_found(e):
# 	print('DBG ERROR HANDLER - NOT FOUND 404')
# 	return 'ERROR HANDLER - NOT FOUND 404', 404


@ui_blueprint.route('/')
def index():
	# return send_from_directory(
	return ui_blueprint.send_static_file('index.html')
