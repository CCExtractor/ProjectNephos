# -*- coding: utf-8 -*-


def str2bool(raw, default=None):
	if raw is None:
		return default

	rl = str(raw).lower()
	if rl in ['true', '1', 't', 'y', 'yes', 'on']:
		return True
	if rl in ['false', '0', 'f', 'n', 'no', 'off']:
		return False

	return default
