#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, or amd64 Debian based OS."
MIN_NOT_MET_MESG="Unmet minimum required package version:"

SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
LIBASOUND_MIN_VER="1.2.4"
LIBPULSE_MIN_VER="14.2"

MAYBE_SUDO="sudo"

REQ_PACKAGES="systemd init-system-helpers libasound2 libpulse0 curl apt-transport-https"

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
    MAYBE_SUDO=""
    if [ "$(id -u)" -ne 0 ]; then
        echo "Insufficient privileges:"
        echo "Please run this script as root."
        exit 1
    fi
fi

$MAYBE_SUDO apt-get update
$MAYBE_SUDO apt-get -y install $REQ_PACKAGES

SYSTEMD_VER="$(dpkg-query -W -f='${Version}' systemd)"
if eval dpkg --compare-versions "$SYSTEMD_VER" lt "$SYSTEMD_MIN_VER"; then
    echo "$MIN_NOT_MET_MESG"
    echo "systemd (>= $SYSTEMD_MIN_VER) but $SYSTEMD_VER is installed."
    echo "$ERROR_MESG"
    exit 1
fi

HELPER_VER="$(dpkg-query -W -f='${Version}' init-system-helpers)"
if eval dpkg --compare-versions "$HELPER_VER" lt "$HELPER_MIN_VER"; then
    echo "$MIN_NOT_MET_MESG"
    echo "init-system-helpers (>= $HELPER_MIN_VER) but $HELPER_VER is installed."
    echo "$ERROR_MESG"
    exit 1
fi

LIBASOUND_VER="$(dpkg-query -W -f='${Version}' libasound2)"
if eval dpkg --compare-versions "$LIBASOUND_VER" lt "$LIBASOUND_MIN_VER"; then
    echo "$MIN_NOT_MET_MESG"
    echo "libasound2 (>= $LIBASOUND_MIN_VER) but $LIBASOUND_VER is installed."
    echo "$ERROR_MESG"
    exit 1
fi

LIBPULSE_VER="$(dpkg-query -W -f='${Version}' libpulse0)"
if eval dpkg --compare-versions "$LIBPULSE_VER" lt "$LIBPULSE_MIN_VER"; then
    echo "$MIN_NOT_MET_MESG"
    echo "libpulse0 (>= $LIBPULSE_MIN_VER) but $LIBPULSE_VER is installed."
    echo "$ERROR_MESG"
    exit 1
fi

curl -sSL https://dtcooper.github.io/raspotify/key.asc | $MAYBE_SUDO tee /usr/share/keyrings/raspotify_key.asc > /dev/null
$MAYBE_SUDO chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | $MAYBE_SUDO tee /etc/apt/sources.list.d/raspotify.list

$MAYBE_SUDO apt-get update
$MAYBE_SUDO apt-get -y install raspotify

echo "Thanks for install Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "And if you're feeling generous you could buy me a RedBull:"
echo "https://github.com/sponsors/JasonLG1979"
