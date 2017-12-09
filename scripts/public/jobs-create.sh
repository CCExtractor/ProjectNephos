#!/bin/bash

# create jobs (from old crontab)

API_URL=http://127.0.0.1:5000

function cronjob()
{
	channel=$1
	program=$2
	days=$3
	hour=$4
	min=$5
	duration_sec=$6

	# days: mon,tue,wed,thu,fri,sat,sun
	# 		"timezone": "Europe/Madrid"

	payload='{"channel_name": "'$channel'", "name": "'$program'", "duration_sec": '$duration_sec', "template_name": "capture",
		"repeat": {
			"cron": {
				"day_of_week": "'$days'",
				"hour": "'$hour'",
				"minute": "'$min'"
			}
		},
		"job_params": {},
		"timezone": "Asia/Yekaterinburg"
	}'

	curl -X POST $API_URL/api/v0/jobs -H 'Content-Type:application/json' -d "$payload"
}

cronjob 'Antena 3' 'Noticias mañana'                             'mon,tue,wed,thu,fri'            6   15  9900
cronjob 'Antena 3' 'Espejo público'                              'mon,tue,wed,thu,fri'            9   00  12600
cronjob 'Antena 3' 'Noticias Deportes El tiempo'                 'mon,tue,wed,thu,fri,sat,sun'    15  00  5400
cronjob 'Antena 3' 'Noticias Deportes El tiempo'                 'mon,tue,wed,thu,fri'            21  00  2700
cronjob 'Antena 3' 'Noticias Deportes El tiempo'                 'sat,sun'                        21  00  4200
cronjob 'Antena 3' 'El hormiguero'                               'mon,tue,wed,thu'                21  45  3300

cronjob 'Cuatro'   'Las mañanas de Cuatro'                       'mon,tue,wed,thu,fri'            11  30  9900
cronjob 'Cuatro'   'Callejeros viajeros'                         'sat,sun'                        12  00  7200
cronjob 'Cuatro'   'Noticias Cuatro Mediodia El tiempo Deportes' 'mon,tue,wed,thu,fri'            14  15  6300
cronjob 'Cuatro'   'Noticias Cuatro Mediodia El tiempo Deportes' 'sat,sun'                        14  00  6300
cronjob 'Cuatro'   'Noticias Cuatro Noche El tiempo Deportes'    'mon,tue,wed,thu,fri'            20  05  5100
cronjob 'Cuatro'   'Noticias Cuatro Noche El tiempo Deportes'    'sat,sun'                        20  00  5400
cronjob 'Cuatro'   'Cintora a pie de calle'                      'mon'                            22  30  5100
cronjob 'Cuatro'   'Cintora a pie de calle'                      'fri'                            21  30  5400
cronjob 'Cuatro'   'Soy noticia'                                 'mon'                            23  55  9300
cronjob 'Cuatro'   '21 dias'                                     'fri'                            23  00  13800

cronjob 'Tele 5'   'Informativos'                                'mon,tue,wed,thu,fri'            6   30  5100
cronjob 'Tele 5'   'Cazamariposas VIP'                           'sat'                            12  00  9000
cronjob 'Tele 5'   'El programa de Ana Rosa'                     'mon,tue,wed,thu,fri'            8   55  10200
cronjob 'Tele 5'   'Informativos Mediodia Deportes El tiempo'    'mon,tue,wed,thu,fri,sat,sun'    14  59  3600
cronjob 'Tele 5'   'Sálvame Limón'                               'mon,tue,wed,thu,fri'            16  00  3600
cronjob 'Tele 5'   'Sálvame Naranja'                             'mon,tue,wed,thu,fri'            16  59  11400
cronjob 'Tele 5'   'Informativos Deportes El tiempo'             'mon,tue,wed,thu,fri,sat'        21  05  3300
cronjob 'Tele 5'   'Informativos Noche'                          'sun'                            20  50  2400
cronjob 'Tele 5'   'Sálvame Naranja'                             'fri'                            22  00  15300

cronjob 'La Sexta' 'Al rojo vivo'                                'mon,tue,wed,thu,fri'            12  20  6000
cronjob 'La Sexta' 'Noticias Mediodia Jugones El tiempo'         'mon,tue,wed,thu,fri,sat,sun'    14  00  6300
cronjob 'La Sexta' 'Más vale tarde'                              'mon,tue,wed,thu,fri'            17  15  9900
cronjob 'La Sexta' 'Noticias Noche El tiempo Deporte'            'mon,wed,thu,fri,sat,sun'        20  00  5400
cronjob 'La Sexta' 'The Very Best of El Intermedio'              'tue'                            21  00  1800
cronjob 'La Sexta' 'Noticias Noche El tiempo Deporte'            'tue'                            20  00  2600
cronjob 'La Sexta' 'El Intermedio'                               'mon,tue,wed,thu'                21  30  6000
cronjob 'La Sexta' 'La Sexta Columna'                            'fri'                            21  30  3600
cronjob 'La Sexta' 'La Sexta Noche'                              'sat'                            21  30  14400
cronjob 'La Sexta' 'Salvados'                                    'sun'                            21  30  3600
cronjob 'La Sexta' 'El objetivo'                                 'sun'                            22  30  4500


# test-cronjob 'La Sexta' 'El objetivo'                                 'sat,sun'                         20  40  45

curl -X GET $API_URL/api/v0/jobs
