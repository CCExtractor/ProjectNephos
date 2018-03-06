# -*- coding: utf-8 -*-

import argparse
import dotenv
import atexit

from .version import __version__
from .version import __description__
from .version import __title__
from .version import __copyright__
from .version import __release__

from .app import Application
from .utils.context import nullcontext


__all__ = [
	'Application', 'main',
	'__version__',
	'__title__',
	'__description__',
	'__copyright__',
	'__release__',
]


def main():
	# ------------------------------------------------------------
	# ARGS PARSE:
	# ------------------------------------------------------------
	aparser = argparse.ArgumentParser(
		description=__description__,
		add_help=False
	)

	aparser.add_argument('--config-path', '-c', type=str,
		help='Path to configuration file', default='recordingmonitor.yml')
	aparser.add_argument('--daemonize', '-d', action='store_true',
		help='Run RecordingMonitor as a daemon')

	silent_parser = aparser.add_mutually_exclusive_group(required=False)
	silent_parser.add_argument('--silent', dest='silent', action='store_true',
		help='Hide a greeting message and several other `print` messages')
	silent_parser.add_argument('--no-silent', dest='silent', action='store_false',
		help='Show all additional messages (do not affect logging). Default.')
	aparser.set_defaults(silent=False)

	aparser.add_argument('--version', '-V', action='version', version=__version__)
	aparser.add_argument('--help', '-?', action='help')

	args = aparser.parse_args()

	if not args.silent:
		print('-' * 40)
		print('{title} [{release}]\n{description}\n{copyright}\n'.format(
			title=__title__,
			release=__release__,
			description=__description__,
			copyright=__copyright__,
		))
		print('-' * 40)

	# ------------------------------------------------------------

	dotenv.load_dotenv('.env')

	# ------------------------------------------------------------
	# Init app
	# ------------------------------------------------------------
	wapp = Application(
		config_path=args.config_path,
	)

	def _cleanup():
		wapp.cleanup()
	atexit.register(_cleanup)

	if False and args.daemonize:
		# ctx = daemon.DaemonContext()
		print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
		print('Daemonize currently not supported')
		print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
		ctx = nullcontext()
	else:
		ctx = nullcontext()

	with ctx:
		wapp.run()
		wapp.cleanup()


if __name__ == '__main__':
	main()
