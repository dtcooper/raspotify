#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, amd64 or riscv64 Debian based OS."

SUDO="sudo"

if ! which apt-get >/dev/null; then
	echo "\nUnspported OS:\n"
	echo "$ERROR_MESG"
	exit 1
fi

if uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64 -e riscv64; then
	echo "\nUnspported architecture:\n"
	echo "$ERROR_MESG"
	echo "\nSupport for ARMv6 (Pi v1 and Pi Zero v1.x) has been dropped."
	echo "0.31.8.1 was the last version to be built with ARMv6 support."
	echo "\nhttps://github.com/dtcooper/raspotify/releases/tag/0.31.8.1\n"
	echo "You can install and run that version on an ARMv6 device,"
	echo "but you will never get updates and doing so is completely unsupported."
	exit 1
fi

if ! which sudo >/dev/null; then
	SUDO=""

	if [ "$(id -u)" -ne 0 ]; then
		echo "\nInsufficient privileges:\n"
		echo "Please run this script as root."
		exit 1
	fi
fi

$SUDO curl -sSfL https://dtcooper.github.io/raspotify/key.asc -o /usr/share/keyrings/raspotify_key.asc
$SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $SUDO tee /etc/apt/sources.list.d/raspotify.list

$SUDO apt-get update
$SUDO apt-get -y install raspotify

echo "\nThanks for installing Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:\n"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "\nAnd if you're feeling generous you could buy me a RedBull:\n"
echo "https://github.com/sponsors/JasonLG1979"
