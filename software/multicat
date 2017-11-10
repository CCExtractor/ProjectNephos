#!/bin/sh

# will be run this way:
# $ multicat {timeout} -u @{channel_ip}{options} {out_file}
#
# PARAMS: {
# 	'channel_ip': channel_ip, // 127.0.0.1:1234
# 	'ifaddr':     ifaddr,
# 	'out_file':   out,
# 	'timeout':    _timeout,
# 	'options':    _options,
# })

# But for debugging we are going to use netcat
# for capturing (not sure about broadcast):
# nc -l -u {host} {port}
# 		(_h, _p) = channel_ip.split(':')

echo "1" | out_file
