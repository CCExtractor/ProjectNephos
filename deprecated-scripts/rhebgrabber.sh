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
PIDFILE="/home/redhen/var/run/rhepggrabber.pid"

#TODO: args para cambiar estos valores
removepid="0"
ignorepid="0"

PATH=/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/redhen/software

function safe_exit
{
        if [[ "$PIDFILE" != "" ]] ; then
                rm $PIDFILE
        fi
        exit $1
}

function comprobarcanales
{
        cambios="0"
        errores="0"
        fichero_informe="${DIR_TEMP}/informe.txt"
        fichero_errores="${DIR_TEMP}/errores.txt"
        rm $fichero_informe $fichero_errores 2>/dev/null
        tmp_unc="${DIR_TEMP}/tmp_uncommented"
        printf "%-40s%-20s%-20s%-20s\n" "Canal" "IP:puerto" "Estado anterior" "Estado actual" >$fichero_informe
        grep -v "^#" $LISTA_CANALES >${tmp_unc}
        while read line; do
                echo "$line"
                canal=`echo "$line" | cut -c1-40`
                ip=`echo "$line" | cut -c41-`
                canal_short=`echo "$canal" | xargs | sed 's/ /_/g'`
                ip_short=`echo "$ip" | xargs`
                echo "    Canal: $canal_short, IP: $ip_short"
                estado_antes="Desconocido"
                estado_despues="Desconocido"
                fichero_estado="$DIR_MONITOR/${canal_short}.estado"
                if [[ -f "$fichero_estado" ]] ; then
                        estado_antes=`cat $fichero_estado`
                fi
                echo "    Estado anterior: $estado_antes"
                stream_file="${DIR_TEMP}/${canal_short}.ts"
                echo timeout 10 "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file}
                timeout 10 "${DIR_SOFTWARE}/multicat" -u @${ip_short}/ifaddr=${IP_IPTV} ${stream_file} 2>&1
                if [[ ! -f ${stream_file} ]] ; then
                        estado_despues="Fichero inexistente, comprobar permisos en $DIR_TEMP"
                else
                        if [[ ! -s ${stream_file} ]] ; then
                                estado_despues="Stream vacio"
                        else
                                ists=`ffprobe ${stream_file} 2>&1  | grep -c "Input #0, mpegts"`
                                if [[ "$ists" == "0" ]] ; then
                                        estado_despues="Corrupto"
                                else
                                        estado_despues="OK"
                                        ${DIR_SOFTWARE}/ccextractor -xmltv -out=null ${stream_file}
                                        xmlfile="${DIR_TEMP}/${canal_short}_epg.xml"
                                        ls -l ${xmlfile}
                                        echo /usr/bin/curl -v -u novik:184412 -F do=upload -F "file_data=@${xmlfile}" http://epgtests.xirvik.com/fm/
                                        # Subir al servidor de desarrollo. Esto hay que quitarlo en cuanto este todo fino.
                                        /usr/bin/curl -s -u novik:184412 -F do=upload -F "file_data=@${xmlfile}" http://epgtests.xirvik.com/fm/
                                fi
                        fi
                fi
                echo "    Estado nuevo: $estado_despues"
                if [[ "$estado_antes" != "$estado_despues" ]] ; then
                        cambios="1"
                        printf "%-40s%-20s%-20s%-20s\n" "$canal" "$ip_short" "$estado_antes" "$estado_despues" >>$fichero_informe
                fi
                if [[ "$estado_despues" != "OK" ]] ; then
                        errores="1"
                        printf "%-40s%-20s%-20s%-20s\n" "$canal" "$ip_short" "$estado_antes" "$estado_despues" >>$fichero_errores

                fi
                echo $estado_despues >${fichero_estado}
        done < <(cat "$tmp_unc")
        t=`date`
        if [[ "$errores" == "0" ]] ; then
                echo "$t: Todos los canales OK" >>${MONITOR_LOG}
        else
                echo "$t: ERROR (lista a continuacion)" >>${MONITOR_LOG}
                cat $fichero_errores >>${MONITOR_LOG}
        fi

        echo "Cambios: $cambios"
        if [[ "$cambios" == "1" ]] ; then
                echo "Hay cambios de estado"
                cat ${fichero_informe}
                cat ${fichero_informe} |mail -s "RedHen Unav: Cambios en canales" ${EMAIL_ADMIN}
        fi
        # Mover ficheros de EPG del directorio temporal al de proceso
        mv ${DIR_TEMP}/*.xml ${DIR_EPG}
        # Borrar todo lo demas
        rm ${DIR_TEMP}/*.aux ${DIR_TEMP}/*.ts
        # Importar los datos
        /usr/bin/php /var/www/public/index.php convert directory ${DIR_EPG}
}

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

echo $$> $PIDFILE || { echo "Failed to write PID file." ; exit 15 ; }  # Failed to write PID file

comprobarcanales

safe_exit 0
