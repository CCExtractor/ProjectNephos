FROM python:3.6

WORKDIR /xirvik/recordingmonitor/

ADD dist/ /xirvik/dist/
RUN pip install /xirvik/dist/xirvik-recordingmonitor-0.0.1.dev0.tar.gz

VOLUME /xirvik/recordingmonitor/data/

CMD ["XirvikRecordingMonitor"]
