FROM python:3.6

WORKDIR /opt/recordingmonitor/

ADD dist/ /tmp/dist/

RUN \
	pip install gunicorn

VOLUME /var/recordingmonitor/data/

RUN \
	pip install /tmp/dist/unav-recordingmonitor-0.0.2.tar.gz && \
	rm -r /tmp/dist/

CMD ["gunicorn", "--workers=2", "unav.recordingmonitor:get_gunicorn_app"]
