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

- DB for internal data -- `recordingmonitor.sqlite`

They will contain configuration and running data of the application

### Using Docker

First you need to get an image (it is private). You could download it (not
implemented yet) or **build** (see _development section_ of this guide)

Having image locally you can run a container:
`docker run --rm --name mon unav/recordingmonitor:0.0.1`

Some settings can be set through environment variables. But it is possible to
mount configuration file from host-machine.

## Setup

### Time zone

Time zone could be set in the configuration property `scheduler.tz` with
fallback to `'utc'` time zone.

Applicable values are described in the documentation for PyTZ module:

http://pythonhosted.org/pytz/

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

The result -- `unav-recordingmonitor-X.Y.Z.tar.gz` file in the `/dist` folder.

### Build new Docker image

You need to have targzipped package in the `/dist` folder (see _Publish new
version_ section of this guide)

**!! don't forget trailing dot !!**

```
docker build -f docker/recordingmonitor/Dockerfile -t unav/recordingmonitor .
```

### Build new PyInstaller bundle

There are several steps:

1. create package (any environment, this package is a pure python package)
2. switch to the appropriate environment (CentOS-6 is good for unav.es)
3. install this package `pip install unav-recordingmonitor-X.Y.Z.tar.gz`
4. install `pip install PyInstaller`
5. patches
  1. fix APSchedule
6. copy `/pyinstaller-entry` from this project
7. run pyinstall
8. tar-gzip the bundle
9. distribute the gzipped bundle

#### 5.1 fix apschedule

Fix APschedule `__init__.py` (inside site-package), use this content:

```python
# These will be removed in APScheduler 4.0.
# release = __import__('pkg_resources').get_distribution('APScheduler').version.split('-')[0]
# version_info = tuple(int(x) if x.isdigit() else x for x in release.split('.'))
# version = __version__ = '.'.join(str(x) for x in version_info[:3])

release = "3.3.1cf" # __import__('pkg_resources').get_distribution('APScheduler').version.split('-')[0]
version_info = "3.3.1cf" # tuple(int(x) if x.isdigit() else x for x in release.split('.'))
version = __version__ = '.'.join(str(x) for x in version_info[:3])
```

#### 7 run pyinstall

```
pyinstaller -y --log-level=WARN pyinstaller/recordingmonitor.spec

# pyinstaller -y --clean --specpath=pyinstaller --log-level=INFO pyinstaller/recordingmonitor.spec
```

#### 8 targz

```
tar --directory=dist -czf recordingmonitor.bundle.tgz ./recordingmonitor
```
