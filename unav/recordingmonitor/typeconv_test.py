# -*- coding: utf-8 -*-

import pytest
from .typeconv import str2bool


class Test_str2bool(object):
	@pytest.mark.parametrize('raw, default, exp', [
		(None, 'x', 'x'),

		('empty',  -198,  -198),
		('ASDF',   -1,    -1),
		('Ono',    'aaa',  'aaa'),

		(True,      -1,   True),
		('true',   -198,  True),
		('1',      -198,  True),
		('t',      -198,  True),
		('Y',      -198,  True),
		('yes',    -198,  True),
		('On',     -198,  True),

		(False,      -1,  False),
		('fAlse',  -198,  False),
		('0',      -198,  False),
		('f',      -198,  False),
		('n',      -198,  False),
		('no',     -198,  False),
		('off',    -198,  False)
	])
	def test_str2bool(self, raw, default, exp):
		act = str2bool(raw, default=default)
		assert act == exp

	def test_str2bool_defaultDefault(self):
		act = str2bool('xxxxxxxxxxxxxNoisdnfa')

		assert act is None
