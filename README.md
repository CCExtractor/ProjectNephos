# Recording Monitor

[![SLACK](https://img.shields.io/badge/slack-50/2-pink.svg)](https://xrvflgrp001.slack.com)

----------------------------------------

## Quickstart

### Using PIP and package

1. download package `unav-recordingmonitor-0.0.1.tar.gz` (or any other version)
2. install `pip install unav-recordingmonitor-0.0.1.tar.gz`
3. run `RecordingMonitor` **OR** `python3 -m unav.recordingmonitor`
4. open http://127.0.0.1:9000 in your browser

Script will create:

- default config -- `recordingmonitor.yml`
- DB for internal data -- `recordingmonitor.sqlite`

They will contain configuration and running data of the application

### Using Docker

First you need to get an image (it is private). You could download it (not
implemented yet) or **build** (see _development section_ of this guide)

Having image locally you can run a container:
`docker run --rm --name mon unav/recordingmonitor:0.0.1`

Some settings can be set through environment variables. But it is possible to
mount configuration file from host-machine.

## Development

Enable virtualenv:

```
virtualenv env/recordingmonitor
source env/recordingmonitor/bin/activate
```

Install dev-dependencies:

```
pip install -r requirements-dev.txt
```

Modify:

1. Create a branch: `git checkout -b dev/my-feature`
2. Edit files
3. Commit changes: `git commit -m 'config: my changes'`
4. Lint: `python -m flake8`
5. Test: `python -m pytest`

Send to upstream:

1. Rebase (to keep history clean): `git rebase upstream/master`
2. Push to your fork: `git push origin`
3. Create PULL REQUEST and wait for acceptance!

### Publish new version

To create new package run:

```
python setup.py sdist
```

### Build new Docker image

You need to have targzipped package in the `/dist` folder (see _Publish new
version_ section of this guide)

```
docker build -f docker/Dockerfile -t unav/recordingmonitor:0.0.1 .
```
