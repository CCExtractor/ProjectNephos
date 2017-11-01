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
MINFREEKB=1048576 # 1 GB

#TODO: args para cambiar estos valores
removepid="0"
ignorepid="0"

ip=""
length=""
program_name=""
PIDFILE=""

PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/redhen/software

function safe_exit
{
        if [[ "$PIDFILE" != "" ]] ; then
                rm $PIDFILE
        fi
        exit $1
}

function useParam
{
        echo "Unknown parameter $1"
        safe_exit 1
}

function set_length
{
        length="$1"
}

function set_program_name
{
        program_name=`echo "$1" | xargs | sed 's/ /_/g'`
}

function set_station
{
        canal="$1"
        test=`cat /home/redhen/etc/canales.conf |grep -v "^#" | grep "^$1" |wc -l`
        echo cat /home/redhen/etc/canales.conf |grep -v "^#" | grep '^$1'
        if [[ "$test" != "1" ]] ; then
                echo "Station channel not found in list ($test): $LISTA_CANALES"
                safe_exit 2
        fi
        ip_short=`cat /home/redhen/etc/canales.conf |grep -v "^#" | grep "^$1" |cut -c41-`
        canal_short=`echo "$canal" | xargs | sed 's/ /-/g'`
}

function record_station
{
        if [[ "$length" == "0" ]] ; then
                echo "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file}
                "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file}
        else
                echo timeout ${length} "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file}
                timeout ${length} "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file}
        fi
        ls -l ${stream_file}
}

free=`df -k / |sed -e '1d' |awk '{print $4'}`
if [ "$free" -lt $MINFREEKB ]; then
        echo "Less than 1 GB in recording node, this program will be skipped." | mail -s "Low space $0 in `hostname`" carlos@ccextractor.org
        exit 1
fi

if [[ "$removepid" == "1" ]] ; then
        rm $PIDFILE
fi

if [[ -f $PIDFILE ]] && [[ "$ignorepid" == "0" ]]; then
        OLD=`stat -c %Z $PIDFILE`; NOW=`date +%s`; (( DIFF = NOW - OLD )) ;
        if [[ $DIFF -lt 3600 ]] ; then # 1 hour
                if [[ "$quiet" == "0" ]] ; then
                        echo "Another instance of $0 ($DIFF seconds old) is running, exiting."
                fi
                exit 4
        else
                echo "A pid file $DIFF seconds old exists. Because this is delicate I'm not going to do anything. Fix manually." | mail -s "Stuck $0 in `hostname`" carlos@ccextractor.org
                exit 5
        fi
fi

while [ "$1" != "" ]; do
        case "$1" in
                "-station" )
                        set_station "$2"
                        shift
                        ;;
                "-length")
                        set_length "$2"
                        shift
                        ;;
                "-program")
                        set_program_name "$2"
                        shift
                        ;;
                *)
                        useParam "$1"
                        ;;
        esac
        shift
done


echo "IP: $ip_short"
echo "Length: $length"
echo "Program name: $program_name"

if [[ "$ip_short" == "" ]] || [[ "$length" == "" ]] || [[ "$program_name" == "" ]] ; then
        echo "Missing parameters"
        safe_exit 2
fi

dt=`date +%F_%H%M`
stream_file_prefix="${DIR_TEMP_RECORDINGS}/${dt}_ES_${canal_short}_${program_name}"
PIDFILE=${stream_file_prefix}.pid
stream_file=${stream_file_prefix}.mpg
echo "Stream file: $stream_file"
echo "PID file: $PIDFILE"

echo $$> $PIDFILE || { echo "Failed to write PID file." ; exit 15 ; }  # Failed to write PID file

record_station

rm $PIDFILE
