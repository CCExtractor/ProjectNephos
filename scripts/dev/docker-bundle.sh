#!/bin/sh

docker run -u `id -u` --rm -v `pwd`:/pack unav-recordingmonitor-packer
