#!/bin/bash

LISTA_CANALES=/home/redhen/etc/canales.conf
DIR_MONITOR=/home/redhen/var/monitor
DIR_TEMP=/home/redhen/var/temp
DIR_EPG=/home/redhen/var/lastepgs
DIR_SOFTWARE=/home/redhen/software
IP_IPTV="159.237.36.240"
MONITOR_LOG="/var/log/redhen.log"
EMAIL_ADMIN="carlos@ccextractor.org"
DIR_TEMP_RECORDINGS=/home/redhen/var/temp_recordings
PIDFILE="/home/redhen/var/run/upload_ucla.pid"

PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/redhen/software

if [[ "$removepid" == "1" ]] ; then
	rm $PIDFILE
fi

if [[ -f $PIDFILE ]] && [[ "$ignorepid" == "0" ]]; then
	OLD=`stat -c %Z $PIDFILE`; NOW=`date +%s`; (( DIFF = NOW - OLD )) ;
	if [[ $DIFF -lt 10800 ]] ; then # 3 hour
		if [[ "$quiet" == "0" ]] ; then
			echo "Another instance of $0 ($DIFF seconds old) is running, exiting."
		fi
		exit 4
	else
		echo "A pid file $DIFF seconds old exists. Because this is delicate I'm not going to do anything. Fix manually." | mail -s "Stuck $0 in `hostname`" carlos@ccextractor.org
		exit 5
	fi
fi

echo $$> $PIDFILE || { echo "Failed to write PID file." ; exit 15 ; }  # Failed to write PID file

for a in $( ls $DIR_TEMP_RECORDINGS/*.mpg ); do
	bn=`basename $a`
	noext=${a%.*}
	echo "File: $a, basename=$bn"
	if [[ -f ${noext}.pid ]] ; then
		echo "Recording in progress, skipping"
		continue
	fi
	/home/redhen/ucla-scripts/check-cc-single.sh $bn -dur 1
	YYYY=`echo $bn |cut -c1-4`
	YYYYMM=`echo $bn |cut -c1-7`
	YYYYMMDD=`echo $bn |cut -c1-10`
	remotepath="${YYYY}/${YYYYMM}/${YYYYMMDD}"
	echo "Remote path: $remotepath"
	ssh ca mkdir -p ES/${remotepath}
	rsync -v --progress ${noext}.mpg ${noext}.txt ${noext}.len ca:ES/${remotepath}
	if [[ "$?" == "0" ]] ; then
		echo "Transfer successful, file deleted"
		rm ${noext}.mpg ${noext}.len ${noext}.txt ${noext}.aux
	fi
	touch $PIDFILE # Do this as heartbeart, because transmissions can really take many hours and two cron tasks could overlap othersise
done

rm $PIDFILE
