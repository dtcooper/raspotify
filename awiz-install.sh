#!/bin/sh

set -e

SUDO="sudo"
APT="apt"

if ! which sudo > /dev/null; then
    SUDO=""

    if [ "$(id -u)" -ne 0 ]; then
        echo "\nInsufficient privileges:\n"
        echo "Please run this script as root."
        exit 1
    fi
fi

ARCH="$(dpkg-architecture -q DEB_TARGET_ARCH)"

PACKAGE="asound-conf-wizard_0.1.1_$ARCH.deb"
PACKAGE_URL="https://github.com/JasonLG1979/asound-conf-wizard/releases/download/0.1.1/$PACKAGE"

wget -q "$PACKAGE_URL"

$SUDO $APT update
$SUDO $APT -y install "./$PACKAGE"

rm -rf $PACKAGE
