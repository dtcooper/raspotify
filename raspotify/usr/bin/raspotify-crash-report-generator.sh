#!/bin/bash

crash_report="/etc/raspotify/crash_report"

config="/etc/raspotify/conf"

# We don't want credentials in the crash report.
username="LIBRESPOT_USERNAME"
password="LIBRESPOT_PASSWORD"
access_token="LIBRESPOT_ACCESS_TOKEN"
proxy="LIBRESPOT_PROXY"

librespot="LIBRESPOT_"

logs=$(journalctl -u raspotify --since "2min ago" -q)

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
	stripped_line=$(echo "$line" | awk '{$1=$1};1')

	case $stripped_line in
	$username*)
		echo "$username=XXXXXXXX" >>$crash_report 2>/dev/null
		;;
	$password*)
		echo "$password=XXXXXXXX" >>$crash_report 2>/dev/null
		;;
	$access_token*)
		echo "$access_token=XXXXXXXX" >>$crash_report 2>/dev/null
		;;
	$proxy*)
		echo "$proxy=XXXXXXXX" >>$crash_report 2>/dev/null
		;;
	$librespot*)
		echo "$stripped_line" >>$crash_report 2>/dev/null
		;;
	*)
		:
		;;
	esac
done <$config

{
	echo -e "\n-- Output of aplay -l --\n"
	aplay -l
	echo -e "\n-- Output of aplay -L --\n"
	aplay -L
	echo -e "\n-- Output of librespot -d ? --"
	librespot -d "?"
} >>$crash_report 2>/dev/null

if [ "$fail_count" -lt 6 ]; then
	sleep 10
	systemctl restart raspotify
fi
