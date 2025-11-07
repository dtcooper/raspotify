#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, amd64 or riscv64 Debian based OS."

LIBC_MIN_VER="2.31"
CUTILS_MIN_VER="8.32"
SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
ALSA_UTILS_VER="1.2.4"
LIBPULSE_MIN_VER="14.2"

SUDO="sudo"
APT="apt"

REQ_PACKAGES="libc6 coreutils systemd init-system-helpers alsa-utils libpulse0"

PACKAGES_TO_INSTALL=
MIN_NOT_MET=

if ! which apt >/dev/null; then
	APT="apt-get"

	if ! which apt-get >/dev/null; then
		echo "\nUnspported OS:\n"
		echo "$ERROR_MESG"
		exit 1
	fi
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

for package in $REQ_PACKAGES; do
	if ! dpkg-query -W -f='${db:Status-Status}\n' "$package" 2>/dev/null | grep -q '^installed$'; then
		PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $package"
	fi
done

if [ "$PACKAGES_TO_INSTALL" ]; then
	$SUDO $APT update
	$SUDO $APT -y install $PACKAGES_TO_INSTALL
fi

for package in $REQ_PACKAGES; do
	case "$package" in
	"libc6")
		MIN_VER=$LIBC_MIN_VER
		;;
	"coreutils")
		MIN_VER=$CUTILS_MIN_VER
		;;
	"systemd")
		MIN_VER=$SYSTEMD_MIN_VER
		;;
	"alsa-utils")
		MIN_VER=$ALSA_UTILS_VER
		;;
	"libpulse0")
		MIN_VER=$LIBPULSE_MIN_VER
		;;
	"init-system-helpers")
		MIN_VER=$HELPER_MIN_VER
		;;
	esac

	VER="$(dpkg-query -W -f='${Version}' $package)"

	if eval dpkg --compare-versions "$VER" lt "$MIN_VER"; then
		MIN_NOT_MET="$MIN_NOT_MET$package >= $MIN_VER is required but $VER is installed.\n"
	fi
done

if [ "$MIN_NOT_MET" ]; then
	echo "\nUnmet minimum required package version(s):\n"
	echo "$MIN_NOT_MET"
	echo "$ERROR_MESG"
	exit 1
fi

curl -sSL https://dtcooper.github.io/raspotify/key.asc | $SUDO tee /usr/share/keyrings/raspotify_key.asc >/dev/null
$SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $SUDO tee /etc/apt/sources.list.d/raspotify.list

$SUDO $APT update
$SUDO $APT -y install raspotify

echo "\nThanks for installing Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:\n"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "\nAnd if you're feeling generous you could buy me a RedBull:\n"
echo "https://github.com/sponsors/JasonLG1979"
