# Recording Monitor

[![SLACK](https://img.shields.io/badge/slack-50/2-pink.svg)](https://xrvflgrp001.slack.com)

--------------------------------------------------------------------------------

## Quickstart

This guide for the **redhen** server (depends on paths and environment).

1. Download the latest `unav-recordingmonitor-bundle-x.x.x.tgz` from
    [GitHub Releases](https://github.com/XirvikMadrid/RecordingMonitor/releases)
2. Extract to the `/home/redhen/recordingmonitor`
3. Add the following line to crontab ([why use exec](http://www.somacon.com/p38.php)):
    `*/15 * * * * root exec /bin/bash /home/redhen/recordingmonitor/scripts/public/start.sh`
4. DONE!

`cron` will ensure that app is running (and start it when necessary) every
15 minutes. `cron` restart is not required.


It it a rough file-tree structure (correct for version 0.1.3):

```
  
/home/redhen/
├── recordingmonitor
│   ├── recordingmonitor       // yes, it's recordingmonitor in recordingmonitor
│   │   │
│   │   ├── array.so                   // \
│   │   ├── base_library.zip           //  \
│   │   ├── xxxxxxxx.so                //   * - 3d-party libraries
│   │   ├── ...........                //  /
│   │   ├── binascii.so                // /
│   │   │
│   │   ├── recordingmonitor           // MAIN BINARY (recordingmonitor again)
│   │   ├── unav                       // UI and other app dependencies
│   │   │
│   │   └── scripts                    // \
│   │       └── public                 //  \
│   │           ├── channels-create.sh //   * - script helpers
│   │           └── start.sh           //  /
│   │
│   ├── log                            // log files
│   │   └── recordingmonitor.log
│   │
│   ├── recordingmonitor.sqlite        // DB
│   ├── recordingmonitor.yml           // config file
│   │
│   └── tmp                        // working directory, with capturing results
│       └── maintenance
│
│
├── unav-recordingmonitor-bundle-0.1.3.dev0.tgz // - original package
│
└── software                   // \
    ├── ccextractor            //  * - external utilities
    ├── multicat               // /
    └── ...

```

--------------------------------------------------------------------------------


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

First, you need to get an image (it is private). You could download it (not
implemented yet) or **build** (see _development section_ of this guide)

Having image locally you can run a container:

```bash
docker run --rm --name mon unav/recordingmonitor`
```

Some settings can be set through environment variables. But it is possible to
mount configuration file from host machine.

## Setup

### Time zone

Time zone could be set in the configuration property `scheduler.tz` with
fallback to `'UTC'` time zone.

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

To create a new version of a pre-built bundle you will need a _Docker image for
building_. For the first time you could create it (locally) with this command:

```
cd docker/pack-centos6
docker build -f Dockerfile --tag unav-recordingmonitor-packer .
cd ../..
```

Now you can use this image to create the bundle. It is easier than it sounds. Just
run the command (**from the root folder of the repository**):

```
docker run -u `id -u` --rm -v `pwd`:/pack unav-recordingmonitor-packer
```

This will run temporary container (`--rm` option). This container will run the
bundling-commands inside. As a result, you will get a new shiny package
`./dist/unav-recordingmonitor-bundle-X.Y.Z.tgz`

PS: we use docker image because it has the appropriate environment, the most
important thing - **old glibc**, installed on the `unav` server.

Several observations about bundle version:

* during build process the `appscheduler` lib will be patched (see section below)
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

#### run pyinstall

```bash
pyinstaller -y --log-level=WARN pyinstaller/recordingmonitor.spec
```

--------------------------------------------------------------------------------

## OBSOLETE: build Docker image with installed recordingmonitor

**OBSOLETE**: nobody will use docker for running this app `:(`

You need to have targzipped package in the `/dist` folder (see _Publish new
version_ section of this guide)

**!! don't forget trailing dot !!**

```bash
docker build -f docker/recordingmonitor/Dockerfile -t unav/recordingmonitor .
```

--------------------------------------------------------------------------------

## API USAGE

### Service

#### Service: ping

```bash
curl -X GET http://127.0.0.1:5000/api/v0/about/ping
```

#### Service: pid

Almost the same as `about/ping` but returns PID of the main process.

```bash
curl -X GET http://127.0.0.1:5000/api/v0/about/pid
```

--------------------------------------------------------------------------------

### Channels

#### Channel: list

```bash
curl -X GET http://127.0.0.1:5000/api/v0/channels
```

#### Channel: create

```bash
curl -X POST http://127.0.0.1:5000/api/v0/channels \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "TVE1",
        "ip_string": "239.255.20.1:1234"
    }'
```

--------------------------------------------------------------------------------

### Jobs

#### Job: list

```bash
curl -X GET http://127.0.0.1:5000/api/v0/jobs
```

#### Job: create

```bash

curl -X POST http://127.0.0.1:5000/api/v0/jobs \
    -H 'content-type: application/json' \
    -d '{
        "name": "rick and mortie",
        "date_from": "2017-12-02T17:40:00+0500",
        "duration_sec": 15,
        "repeat": {
          "interval": {
            "minutes": 1,
            "date_trim": "2017-12-02T17:45:00+0500"
          }
        },
        "template_name": "capture",
        "channel_ID": "d327c73c-1577-42d4-843c-ec494425cec4",
        "job_params": {
          "ftp_host": "127.0.0.1",
          "ftp_user": "user",
          "ftp_password": "123"
        }
    }'
```

--------------------------------------------------------------------------------

## AUTHORS

* Maksim Koryukov

## LICENSE

Private project
