# CHANGELOG

This is the history of changes of the `unav-recordingmonitor` package

> This file should be filled by maintainers, using pull requests
> Please, follow this [guide](http://keepachangelog.com/en/0.3.0/)

## 0.3.0 // 2018-02-12

* special command-template for capturing UNAV
* fix tiny bugs

## 0.2.0 // 2017-12-10

* API: new route /api/v0/about/pid
* API: add job using channel NAME (not only ID is consumable now)
* DB: stricter structure - add FK for log-records
* DB: allow to add jobs with `date_from` in the past
* config: allow to use templates for output destinations
* config: new capturing template for "CAPTURE" jobs
* config: list all templating variables, and add several new variables
* notification: channel-on-air will notify only if channels' states changed
* scheduler: explicit timezones for jobs
* scripts: scritp for creating jobs (ported from old crontab)

* misc: tiny fixes and new tests

* deps: update apscheduler (3.4.0)

## 0.1.3 // 2017-12-05

* check channels (on air)
* capture stream data for channels
* repeatable capturing (cron-like and by-interval)
* check for free space
* store info in sqlite (configurable)
* notification - email, fully configurable

* `startup` scripts
* update README file

* bundler upon pyinstaller
* docker builder (for old version of glib)

## 0.0.3 // 2017-11-??

* **Sentry** integration
