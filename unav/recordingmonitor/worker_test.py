# -*- coding: utf-8 -*-

import pytest
from .worker import _to_start_date

import datetime

import arrow


class Test__to_start_date:

	def test_general(self):
		now = datetime.datetime.now(datetime.timezone.utc)
		now20_00 = datetime.datetime(
			now.year,
			now.month,
			now.day,
			20, 00,
			tzinfo=datetime.timezone.utc
		)

		act = _to_start_date('20:00', 'Asia/Karachi')

		assert act == now20_00

	def test_none(self):
		act = _to_start_date(None, 'Asia/Karachi')
		assert act is None

	def test_unrecognized_format(self):
		act = _to_start_date('20-00', 'utc')
		assert act is None
