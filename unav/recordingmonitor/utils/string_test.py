# -*- coding: utf-8 -*-

import pytest
from .string import format_with_emptydefault
from .string import decode_and_superstrip


class Test_decode_and_superstrip:
	@pytest.mark.parametrize('s, exp', [
		(''.encode(), None),
		(' '.encode(), None),

		('x'.encode(), 'x'),
	])
	def test_common(self, s, exp):
		act = decode_and_superstrip(s)

		assert act == exp

	def test_none_str(self):
		act = decode_and_superstrip(None)

		assert act is None


class Test_format_with_emptydefault:
	@pytest.mark.parametrize('tpl, data, exp', [
		('123', {}, '123'),
	])
	def test_common(self, tpl, data, exp):
		act = format_with_emptydefault(tpl, data)

		assert act == exp

	@pytest.mark.parametrize('tpl, data, exp', [
		('my |{address}| and |{name}|', {'name': 123}, 'my || and |123|'),
	])
	def test_missing_key(self, tpl, data, exp):
		act = format_with_emptydefault(tpl, data)

		assert act == exp

	@pytest.mark.parametrize('data', [
		({}),
		({'name': 123}),
	])
	def test_null_tpl(self, data):
		act = format_with_emptydefault(None, data)

		assert act is None
