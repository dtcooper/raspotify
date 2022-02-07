#!/bin/bash -e

SOURCE_REPO="deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main"

SYSTEMD_MIN_VER="247.3"
HELPER_MIN_VER="1.6"
LIBASOUND_MIN_VER="1.2.4"

# Install script for Raspotify. Adds the Debian repo and installs.

if ! which apt-get apt-key sudo > /dev/null || uname -a | grep -F -ivq -e armv7 -e aarch64 -e x86_64; then
    echo "Unspported architecture:"
    echo "Please make sure you are running a compatible armhf (ARMv7), arm64, or amd64 Debian based OS."
    exit 1
fi

# You should probably have all of these installed unless ofc you're running a systemd-less Debian derivative.
# If they're installed but the min versions are not meet you're not running a compatible Debian based OS.

check_packages () {
    MISSING_PACKAGES=
    if ! dpkg-query -W -f='${db:Status-Status}\n' curl 2> /dev/null | grep -q '^installed$'; then
        MISSING_PACKAGES="curl\n$MISSING_PACKAGES"
    fi

    if ! dpkg-query -W -f='${db:Status-Status}\n' apt-transport-https 2> /dev/null | grep -q '^installed$'; then
        MISSING_PACKAGES="apt-transport-https\n$MISSING_PACKAGES"
    fi

    if ! dpkg-query -W -f='${db:Status-Status}\n' systemd 2> /dev/null | grep -q '^installed$' \
        || eval dpkg --compare-versions "$(dpkg-query -W -f='${Version}' systemd)" gt "$SYSTEMD_MIN_VER"; then
        MISSING_PACKAGES="systemd (>= $SYSTEMD_MIN_VER)\n$MISSING_PACKAGES"
    fi

    if ! dpkg-query -W -f='${db:Status-Status}\n' init-system-helpers 2> /dev/null | grep -q '^installed$' \
        || eval dpkg --compare-versions "$(dpkg-query -W -f='${Version}' init-system-helpers)" gt "$HELPER_MIN_VER"; then
        MISSING_PACKAGES="init-system-helpers (>= $HELPER_MIN_VER)\n$MISSING_PACKAGES"
    fi

    if ! dpkg-query -W -f='${db:Status-Status}\n' libasound2 2> /dev/null | grep -q '^installed$' \
        || eval dpkg --compare-versions "$(dpkg-query -W -f='${Version}' libasound2)" gt "$LIBASOUND_MIN_VER"; then
        MISSING_PACKAGES="libasound2 (>= $LIBASOUND_MIN_VER)\n$MISSING_PACKAGES"
    fi
}

check_packages

if [ "$MISSING_PACKAGES" ]; then
    echo -e "Unmet dependencies:\n\n$MISSING_PACKAGES"
    echo -n "Do you want to install them? [y/N] "
    read -r REPLY      
    if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then exit 0; fi

    sudo apt update
    sudo apt install -y systemd init-system-helpers libasound2 curl apt-transport-https

    check_packages

    if [ "$MISSING_PACKAGES" ]; then
        echo -e "\nThere are still unmet dependencies:\n\n$MISSING_PACKAGES"
        echo "Please make sure you are running a compatible Debian based OS with the minimum required package versions."
        exit 1

    fi
fi

# Add public key to apt
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo tee /usr/share/keyrings/raspotify_key.asc > /dev/null
sudo chmod 644 /usr/share/keyrings/raspotify_key.asc
echo "$SOURCE_REPO" | sudo tee /etc/apt/sources.list.d/raspotify.list

sudo apt-get update
sudo apt-get -y install raspotify
