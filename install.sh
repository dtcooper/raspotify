#!/bin/sh

set -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"
ERROR_MESG="Please make sure you are running a compatible armhf (ARMv7), arm64, or amd64 Debian based OS."
MIN_NOT_MET_MESG="\nUnmet minimum required package version(s):\n"

SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
LIBASOUND_MIN_VER="1.2.4"
LIBPULSE_MIN_VER="14.2"

SUDO="sudo"
APT="apt"

REQ_PACKAGES="systemd init-system-helpers libasound2 libpulse0 curl"

PACKAGES_TO_INSTALL=
MIN_NOT_MET=

if ! which apt > /dev/null; then
    APT="apt-get"

    if ! which apt-get > /dev/null; then
        echo "\nUnspported OS:\n"
        echo "$ERROR_MESG"
        exit 1
    fi
fi

if uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64; then
    echo "\nUnspported architecture:\n"
    echo "$ERROR_MESG"
    exit 1
fi

if ! which sudo > /dev/null; then
    SUDO=""

    if [ "$(id -u)" -ne 0 ]; then
        echo "\nInsufficient privileges:\n"
        echo "Please run this script as root."
        exit 1
    fi
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

for package in $REQ_PACKAGES; do
    case "$package" in
       "systemd") MIN_VER=$SYSTEMD_MIN_VER
       ;;
       "libasound2") MIN_VER=$LIBASOUND_MIN_VER
       ;;
       "libpulse0") MIN_VER=$LIBPULSE_MIN_VER
       ;;
       "init-system-helpers") MIN_VER=$HELPER_MIN_VER
       ;;
       *) MIN_VER=
       ;;
    esac

    if [ "$MIN_VER" ]; then
        VER="$(dpkg-query -W -f='${Version}' $package)"

        if eval dpkg --compare-versions "$VER" lt "$MIN_VER"; then
            MIN_NOT_MET="$MIN_NOT_MET$package >= $MIN_VER is required but $VER is installed.\n"
        fi
    fi
done

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

echo "\nThanks for installing Raspotify! Don't forget to checkout the wiki for tips, tricks and configuration info!:\n"
echo "https://github.com/dtcooper/raspotify/wiki"
echo "\nAnd if you're feeling generous you could buy me a RedBull:\n"
echo "https://github.com/sponsors/JasonLG1979"
