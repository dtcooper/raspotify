#!/bin/sh

REQUIRED_PACKAGES="libasound2 adduser"

# Install script for Raspotify. Downloads and installs Debian package.

run_on_pi_only() {
    echo "Raspotify installer only runs on a Raspberry Pi"
    exit 1
}

if ! which apt-get > /dev/null; then
    run_on_pi_only
fi

DID_APT_GET_UPDATE=

do_apt_get_update() {
    if [ -z "$DID_APT_GET_UPDATE" ]; then
        sudo apt-get update
        DID_APT_GET_UPDATE=1
    fi
}

if ! which lsb_release > /dev/null; then
    do_apt_get_update
    sudo apt-get install -y lsb-release
fi

if lsb_release -si | fgrep -ivq raspbian; then
    run_on_pi_only
fi


if ! which curl > /dev/null; then
    do_apt_get_update
    sudo apt-get install -y curl
fi


LATEST_RELEASE="$(curl -Ls https://api.github.com/repos/dtcooper/raspotify/releases/latest | fgrep browser_download_url | head -n 1 | cut -d '"' -f 4)"
if [ -z "$LATEST_RELEASE" ]; then
    echo "Can't find latest Raspotify release on GitHub"
    exit 1
fi

PACKAGES_TO_INSTALL=
for package in $REQUIRED_PACKAGES; do
    if ! dpkg-query --show --showformat='${db:Status-Status}\n' "$package" 2> /dev/null | grep -q '^installed$'; then
        PACKAGES_TO_INSTALL="$package $PACKAGES_TO_INSTALL"
    fi
done

if [ "$PACKAGES_TO_INSTALL" ]; then
    do_apt_get_update
    sudo apt-get -y install $PACKAGES_TO_INSTALL
fi

cd /tmp
curl -Lo raspotify-latest.deb "$LATEST_RELEASE"
sudo dpkg -i --force-confold raspotify-latest.deb
rm raspotify-latest.deb
