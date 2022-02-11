#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, or amd64 Debian based OS."
MIN_NOT_MET_MESG="Unmet minimum required package version:"

SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
LIBASOUND_MIN_VER="1.2.4"
LIBPULSE_MIN_VER="14.2"

SUDO="sudo"
APT="apt"

REQ_PACKAGES="systemd init-system-helpers libasound2 libpulse0 curl"

PACKAGES_TO_INSTALL=
MIN_NOT_MET=

if ! which apt-get apt-key > /dev/null; then
    echo "Unspported OS:"
    echo "$ERROR_MESG"
    exit 1
fi

if uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64; then
    echo "Unspported architecture:"
    echo "$ERROR_MESG"
    exit 1
fi

if ! which sudo > /dev/null; then
    SUDO=""
    if [ "$(id -u)" -ne 0 ]; then
        echo "Insufficient privileges:"
        echo "Please run this script as root."
        exit 1
    fi
fi

if ! which apt > /dev/null; then
    APT="apt-get"
fi

for package in $REQ_PACKAGES; do
    if ! dpkg-query -W -f='${db:Status-Status}\n' "$package" 2> /dev/null | grep -q '^installed$'; then
        PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL $package"
    fi
done

if [ "$PACKAGES_TO_INSTALL" ]; then
    $SUDO $APT update
    $SUDO $APT -y install $PACKAGES_TO_INSTALL

fi

HELPER_VER="$(dpkg-query -W -f='${Version}' init-system-helpers)"
if eval dpkg --compare-versions "$HELPER_VER" lt "$HELPER_MIN_VER"; then
    MIN_NOT_MET="init-system-helpers >= $HELPER_MIN_VER is required but $HELPER_VER is installed."
fi

LIBPULSE_VER="$(dpkg-query -W -f='${Version}' libpulse0)"
if eval dpkg --compare-versions "$LIBPULSE_VER" lt "$LIBPULSE_MIN_VER"; then
    MIN_NOT_MET="libpulse0 >= $LIBPULSE_MIN_VER is required but $LIBPULSE_VER is installed.\n$MIN_NOT_MET"
fi

LIBASOUND_VER="$(dpkg-query -W -f='${Version}' libasound2)"
if eval dpkg --compare-versions "$LIBASOUND_VER" lt "$LIBASOUND_MIN_VER"; then
    MIN_NOT_MET="libasound2 >= $LIBASOUND_MIN_VER is required but $LIBASOUND_VER is installed.\n$MIN_NOT_MET"
fi

SYSTEMD_VER="$(dpkg-query -W -f='${Version}' systemd)"
if eval dpkg --compare-versions "$SYSTEMD_VER" lt "$SYSTEMD_MIN_VER"; then
    MIN_NOT_MET="systemd >= $SYSTEMD_MIN_VER is required but $SYSTEMD_VER is installed.\n$MIN_NOT_MET"
fi

if [ "$MIN_NOT_MET" ]; then
    echo "$MIN_NOT_MET_MESG"
    echo "$MIN_NOT_MET"
    echo "$ERROR_MESG"
    exit 1
fi

curl -sSL https://dtcooper.github.io/raspotify/key.asc | $SUDO tee /usr/share/keyrings/raspotify_key.asc > /dev/null
$SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $SUDO tee /etc/apt/sources.list.d/raspotify.list

$SUDO $APT update
$SUDO $APT -y install raspotify

echo "Thanks for install Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "And if you're feeling generous you could buy me a RedBull:"
echo "https://github.com/sponsors/JasonLG1979"
