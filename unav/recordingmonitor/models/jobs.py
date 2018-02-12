# -*- coding: utf-8 -*-

# import arrow
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.arrow import ArrowType as TypeArrowDate

from .base import Model
from ..db.mixins import MixinIdGuid
from ..db.types import TypeJson
from ..db.types import TypeUuid

from ..errors import ValidationError


class JobInfo(MixinIdGuid, Model):

	__tablename__ = 'job_info'

	name = sa.Column(sa.String(1200))
	date_from = sa.Column(TypeArrowDate)
	duration_sec = sa.Column(sa.Integer)
	timezone = sa.Column(sa.String(128), default=None)

	template_name = sa.Column(sa.String(4800))
	job_params = sa.Column(TypeJson)
	job_ID = sa.Column(sa.String(96))
	repeat = sa.Column(TypeJson)
	is_removed = sa.Column(sa.Boolean, default=False)

	channel_ID = sa.Column(TypeUuid, ForeignKey('channel.ID'), nullable=True)
	meta_teletext_page = sa.Column(sa.String(128))
	meta_country_code = sa.Column(sa.String(16))
	meta_language_code3 = sa.Column(sa.String(16))
	meta_video_source = sa.Column(sa.String(1200))

	job_launch_list = relationship('JobLaunch', back_populates='job_info')

	DURATION_SEC_MIN = 5
	DURATION_SEC_MAX = 10 * 60 * 60

	# def __init__(self):
	# 	super().__init__()

	def validate(self):
		# now = arrow.get()
		# if self.date_from < now:
		# 	raise ValidationError('Cannot add a Job in the past')

		if self.duration_sec < self.DURATION_SEC_MIN:
			raise ValidationError('Job is too short: {}sec < {}sec'.format(
				self.duration_sec,
				self.DURATION_SEC_MIN
			))

		if self.duration_sec > self.DURATION_SEC_MAX:
			raise ValidationError('Job is too long: {}sec > {}sec'.format(
				self.duration_sec,
				self.DURATION_SEC_MAX
			))

		# TODO: validate 'repeat' - should not run earlier than 'duration'


class JobLaunch(MixinIdGuid, Model):

	__tablename__ = 'job_launch'

	job_info_ID = sa.Column(TypeUuid, ForeignKey('job_info.ID'))
	date_from = sa.Column(TypeArrowDate)

	job_info = relationship('JobInfo', back_populates='job_launch_list')
