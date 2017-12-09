#!/bin/bash

# create channels

API_URL=http://127.0.0.1:5000

curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TVE1",                "ip_string": "239.255.20.1:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "La 2",                "ip_string": "239.255.20.2:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Antena 3",            "ip_string": "239.255.20.3:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Cuatro",              "ip_string": "239.255.20.4:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Tele 5",              "ip_string": "239.255.20.5:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "La Sexta",            "ip_string": "239.255.20.6:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TVE 24Horas",         "ip_string": "239.255.20.8:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Navarra TV",          "ip_string": "239.255.20.10:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Navarra TV2",         "ip_string": "239.255.20.11:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "TDP",                 "ip_string": "239.255.20.12:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "13TV",                "ip_string": "239.255.20.13:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "BBC World News",      "ip_string": "239.255.20.14:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "CNN International",   "ip_string": "239.255.20.15:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "AL Jazzeera English", "ip_string": "239.255.20.16:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "France 24 (english",  "ip_string": "239.255.20.17:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Russia Today",        "ip_string": "239.255.20.18:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "CCTV News",           "ip_string": "239.255.20.19:1234"}'
curl -X POST $API_URL/api/v0/channels -H 'Content-Type:application/json' -d '{"name": "Bloomberg Europe TV", "ip_string": "239.255.20.20:1234"}'

curl -X GET $API_URL/api/v0/channels
