# -*- coding: utf-8 -*-

import logging
import smtplib
from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
# from email.message import Message

from .formatter import render

# # Create the container (outer) email message.
# msg = MIMEMultipart()

log = logging.getLogger(__name__)


class EmailsNotifier:
	def __init__(
		self,
		smtp_host=None,
		smtp_port=None,
		smtp_ssl=True,
		smtp_tls=False,

		username=None,
		password=None,

		email_subject=None,
		email_from=None,
		email_to=None
	):
		self.smtp_host = smtp_host
		self.smtp_port = smtp_port
		self.smtp_ssl = smtp_ssl
		self.smtp_tls = smtp_tls

		self.username = username
		self.password = password

		self.email_subject = email_subject
		self.email_from = email_from

		# self.email_to = email_to
		if isinstance(email_to, str):
			self.email_to = [email_to]
		elif isinstance(email_to, (tuple, list)):
			self.email_to = list(email_to)
		else:
			raise TypeError('email to must be string or list')

		self.email_to = ','.join(self.email_to)

	def _create_smtp_client(self):
		if self.smtp_ssl:
			cl = smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
		else:
			cl = smtplib.SMTP(host=self.smtp_host, port=self.smtp_port)

		return cl

	def notify(self, sender, notification_code, data):

		template_name = 'emails/{}'.format(notification_code)
		message = render(template_name, data)

		log.debug(
			'email notify, sender=[%s], data=[%s]',
			sender,
			data,
		)

		emsg = MIMEText(message)
		emsg['Subject'] = self.email_subject
		emsg['From'] = self.email_from
		emsg['To'] = self.email_to

		with self._create_smtp_client() as server:

			if self.smtp_tls:
				server.starttls()

			server.login(user=self.username, password=self.password)

			# server.set_debuglevel(1)
			server.send_message(emsg)
			server.quit()
