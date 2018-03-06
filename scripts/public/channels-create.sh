#!/bin/bash

# create channels

API_URL=http://127.0.0.1:5000

curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TVE1",                "ip_string": "239.255.20.1:1234",  "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "La 2",                "ip_string": "239.255.20.2:1234",  "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Antena 3",            "ip_string": "239.255.20.3:1234",  "meta_teletext_page": "888", "meta_country_code": "ES", "meta_language_code3": "SPA", "meta_timezone": "Europe/Madrid", "meta_video_source": "Universidad de Navarra, Spain"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Cuatro",              "ip_string": "239.255.20.4:1234",  "meta_teletext_page": "888", "meta_country_code": "ES", "meta_language_code3": "SPA", "meta_timezone": "Europe/Madrid", "meta_video_source": "Universidad de Navarra, Spain"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Tele 5",              "ip_string": "239.255.20.5:1234",  "meta_teletext_page": "888", "meta_country_code": "ES", "meta_language_code3": "SPA", "meta_timezone": "Europe/Madrid", "meta_video_source": "Universidad de Navarra, Spain"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "La Sexta",            "ip_string": "239.255.20.6:1234",  "meta_teletext_page": "888", "meta_country_code": "ES", "meta_language_code3": "SPA", "meta_timezone": "Europe/Madrid", "meta_video_source": "Universidad de Navarra, Spain"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TVE 24Horas",         "ip_string": "239.255.20.8:1234",  "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Navarra TV",          "ip_string": "239.255.20.10:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Navarra TV2",         "ip_string": "239.255.20.11:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TDP",                 "ip_string": "239.255.20.12:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "13TV",                "ip_string": "239.255.20.13:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "BBC World News",      "ip_string": "239.255.20.14:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "CNN International",   "ip_string": "239.255.20.15:1234", "meta_teletext_page": "150", "meta_country_code": "DE", "meta_language_code3": "DEU", "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "AL Jazzeera English", "ip_string": "239.255.20.16:1234", "meta_teletext_page": "150", "meta_country_code": "DE", "meta_language_code3": "DEU", "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "France 24 (english",  "ip_string": "239.255.20.17:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Russia Today",        "ip_string": "239.255.20.18:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "CCTV News",           "ip_string": "239.255.20.19:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Bloomberg Europe TV", "ip_string": "239.255.20.20:1234", "meta_teletext_page": null,  "meta_country_code": null, "meta_language_code3": null,  "meta_timezone": null,            "meta_video_source": null}'

# AlJazeera-EU      ) TP=150 ; CTRY=DE ; LANG=DEU ;;
# CNN-International ) TP=150 ; CTRY=DE ; LANG=DEU ;;
# Antena-3          ) TP=888 ; CTRY=ES ; LANG=SPA ; LOC="Europe/Madrid" ; SRC="Universidad de Navarra, Spain" ;;
# La-Sexta          ) TP=888 ; CTRY=ES ; LANG=SPA ; LOC="Europe/Madrid" ; SRC="Universidad de Navarra, Spain" ;;
# Cuatro            ) TP=888 ; CTRY=ES ; LANG=SPA ; LOC="Europe/Madrid" ; SRC="Universidad de Navarra, Spain" ;;
# Tele-5            ) TP=888 ; CTRY=ES ; LANG=SPA ; LOC="Europe/Madrid" ; SRC="Universidad de Navarra, Spain" ;;

# 1TV               ) TP=888 ; CTRY=RU ; LANG=RUS ; LOC="Europe/Moscow" ; SRC="Saratov, Russia" ;;
# TVC               ) TP=888 ; CTRY=RU ; LANG=RUS ; LOC="Europe/Moscow" ; SRC="Saratov, Russia" ;;
# CT1               ) TP=888 ; CTRY=CZ ; LANG=CES ; LOC="Europe/Prague" ; SRC="Petr Kutalek, Prague" ;;
# DasErste          ) TP=150 ; CTRY=DE ; LANG=DEU ;;
# EuroNews          ) TP=150 ; CTRY=DE ; LANG=DEU ;;
# N-TV              ) TP=341 ; CTRY=DE ; LANG=DEU ;;
# RTL               ) TP=888 ; CTRY=DE ; LANG=DEU ;;
# Tagesschau24      ) TP=150 ; CTRY=DE ; LANG=DEU ;;
# ZDF               ) TP=777 ; CTRY=DE ; LANG=DEU ;;
# *             ) echo -e "\n\tUnknown network $NWK -- please add to `basename $0`\n" ; exit ;;

curl -X GET $API_URL/api/v0/channels
