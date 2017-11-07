# Recording Monitor

[![SLACK](https://img.shields.io/badge/slack-50/2-pink.svg)](https://xrvflgrp001.slack.com)

----------------------------------------

_so the first task would be record for example from TVE1 from 15:00 to 15:45
(server local time, which is UTC+1 I think)_

## Quickstart

### Using PIP and package

1. download package `unav-recordingmonitor-0.0.1.tar.gz` (use the latest
  version, plz)
2. install `pip install unav-recordingmonitor-0.0.1.tar.gz`
3. run `RecordingMonitor` **OR** `python3 -m unav.recordingmonitor`
4. open http://127.0.0.1:9000 in your browser

Script will automatically create its DB (internal storage) --
`recordingmonitor.sqlite`

### Using Docker

**OBSOLETE**

First you need to get an image (it is private). You could download it (not
implemented yet) or **build** (see _development section_ of this guide)

Having image locally you can run a container:

```bash
docker run --rm --name mon unav/recordingmonitor`
```

Some settings can be set through environment variables. But it is possible to
mount configuration file from host-machine.

## Setup

### Time zone

Time zone could be set in the configuration property `scheduler.tz` with
fallback to `'utc'` time zone.

Applicable values are described in the documentation for PyTZ module:

http://pythonhosted.org/pytz/

--------------------------------------------------------------------------------

## Development

Create virtualenv (run once):

```bash
virtualenv env/recordingmonitor
```

Enable virtualenv:

```bash
source env/recordingmonitor/bin/activate
```

Install dev-dependencies:

```bash
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

# Client UI

Client UI is a Vue-application (javascript framework).

To rebuild client UI you will need:

1. Install *Node.JS* (version >= 4.0.0)
2. go to sources (`cd client`) and install dependencies: `npm install`

It is very useful to connect Python and JS parts by linking Vue-app as a static
asset:

```bash
# run from the root folder of the local git-repo
ln -r -s ./client/dist ./unav/recordingmonitor/web/ui/dist
```

--------------------------------------------------------------------------------

## DEPLOYMENT

### Create PyPI

To create new package run:

```
python setup.py sdist
```

The result -- `unav-recordingmonitor-X.Y.Z.tar.gz` file in the `/dist` folder.

### Build new PyInstaller bundle with Docker image

To create a new version of a prebuilt bundle you will need a _Docker image for
building_. For the first time you could create it (locally) with this command:

```
cd docker/pack-centos6
docker build -f Dockerfile --tag unav-recordingmonitor-packer .
cd ../..
```

Now you can use this image to create bundle. It is easier than it sounds. Just
run the command (**from the root folder of the repository**):

```
docker run -u `id -u` --rm -v `pwd`:/pack unav-recordingmonitor-packer
```

This will run temporary container (`--rm` option). This container will run the
bundling-commands inside. As a result you will get a new shiny package
`./dist/unav-recordingmonitor-bundle-X.Y.Z.tgz`

PS: we use docker image because it has the appropriate environment, the most
importatant thing - **old glibc**, installed on unav server.

Several observations about bundle version:

* during build process the appscheduler lib will be patched (see section below)
* bundle is a result of running `PyInstaller` (see section below)

#### fix apschedule

Without this fix bundled version of the app will not work.

Fix APschedule `__init__.py` (inside site-package), use this content:

```python
# These will be removed in APScheduler 4.0.
release = '3.3.1cf' # __import__('pkg_resources').get_distribution('APScheduler').version.split('-')[0]
version_info = '3.3.1cf' # tuple(int(x) if x.isdigit() else x for x in release.split('.'))
version = __version__ = '.'.join(str(x) for x in version_info[:3])
```

Original solution: https://github.com/agronholm/apscheduler/issues/158#issuecomment-299444402

#### 7 run pyinstall

```bash
pyinstaller -y --log-level=WARN pyinstaller/recordingmonitor.spec
```

--------------------------------------------------------------------------------

## OBSOLETE: build Docker image with installed recordingmonitor

**OBSOLETE**: nobody will use docker for running this app :(

You need to have targzipped package in the `/dist` folder (see _Publish new
version_ section of this guide)

**!! don't forget trailing dot !!**

```bash
docker build -f docker/recordingmonitor/Dockerfile -t unav/recordingmonitor .
```

--------------------------------------------------------------------------------

## API USAGE

### Channel: create

```bash
curl -X POST \
    http://127.0.0.1:5000/api/v0/channels
    -H 'Content-TYpe: application/json'
    -d '{
        "name": "TVE1",
        "ip_string": "239.255.20.1:1234"
    }'
```

### Job: create

```bash
curl -X POST \
    http://127.0.0.1:5000/api/v0/jobs \
    -H 'content-type: application/json' \
    -d '{
        "name": "rick and mortie",
        "date_from": "2017-10-07T14:00:00+0500",
        "date_trim": "2017-12-12T14:00:05+0500",
        "template_name": "capture",
        "channel_ID": "1b5c65e4-a03e-430c-a554-be6d3a41e721",
        "job_params": {
            "message": "nothing",
            "host": "localhost",
            "port": 1234
        }
    }'
```
