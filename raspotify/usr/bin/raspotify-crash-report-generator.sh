#!/bin/bash

crash_report="/etc/raspotify/crash_report"

config="/etc/raspotify/conf"

# We don't want user names or passwords in the crash report.
username="LIBRESPOT_USERNAME"
password="LIBRESPOT_PASSWORD"

librespot="LIBRESPOT_"
tmp_dir="TMPDIR"

logs=$(journalctl -u raspotify --since "1min ago" -q)

fail_count=$(echo "$logs" | grep -o "raspotify.service: Failed" | wc -l)

{
	echo -e "-- System Info --\n"
	uname -a
	cat /etc/os-release
	echo -e "\n-- Logs --\n"
	echo "$logs"
	echo -e "\n-- Config --\n"
} >$crash_report 2>/dev/null

while read -r line; do
	if { [[ $line = $librespot* ]] && [[ $line != $username* ]] && [[ $line != $password* ]]; } || [[ $line = $tmp_dir* ]]; then
		echo "$line" >>$crash_report 2>/dev/null
	fi
done <$config

{
	echo -e "\n-- Ouput of aplay -l --\n"
	aplay -l
	echo -e "\n-- Ouput of aplay -L --\n"
	aplay -L
	echo -e "\n-- Ouput of librespot -d ? --"
	librespot -d "?"
} >>$crash_report 2>/dev/null

systemctl reset-failed raspotify

if [ "$fail_count" -lt 6 ]; then
	# delay restarts by 10 sec to debounce
	sleep 10
	systemctl restart raspotify
fi
