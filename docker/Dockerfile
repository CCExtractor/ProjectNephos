FROM python:3.6

WORKDIR /opt/recordingmonitor/

ADD dist/ /tmp/dist/
RUN \
	pip install /tmp/dist/unav-recordingmonitor-0.0.1.dev1.tar.gz && \
	rm -r /tmp/dist/


VOLUME /var/recordingmonitor/data/

CMD ["RecordingMonitor"]
