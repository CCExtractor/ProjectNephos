# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Model
from ..db.mixins import MixinIdGuid
from ..db.types import TypeUuid

# from ..errors import ValidationError


class Channel(MixinIdGuid, Model):

	__tablename__ = 'channel'

	name = sa.Column(sa.String(1200), nullable=False, unique=True)
	name_short = sa.Column(sa.String(1200))
	# enough to store ipv6.. IDNKW, but it is easier to store more bytes, than
	# rewrite schema (especially now - we don't have migration tools)
	ip_string = sa.Column(sa.String(128), nullable=False)

	meta_teletext_page = sa.Column(sa.String(128))
	meta_country_code = sa.Column(sa.String(16))
	meta_language_code3 = sa.Column(sa.String(16))
	meta_timezone = sa.Column(sa.String(128))
	meta_video_source = sa.Column(sa.String(1200))

	channel_status = relationship(
		'ChannelStatus',
		uselist=False,
		back_populates='channel',
		lazy='joined',
	)

	# def __init__(self):
	# 	super().__init__()


class ChannelStatus(MixinIdGuid, Model):

	__tablename__ = 'channel_status'

	channel_ID = sa.Column(TypeUuid, ForeignKey('channel.ID'), nullable=False)

	ts = sa.Column(sa.TIMESTAMP, default=func.now())
	status = sa.Column(sa.String(128))
	error = sa.Column(sa.String(4096))

	channel = relationship('Channel', back_populates='channel_status')

	# def __init__(self):
	# 	super().__init__()
