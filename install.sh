#!/bin/sh

# Install script for Raspotify. Downloads and installs Debian package.

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
    echo "Please run on a Raspberry Pi"
    exit 1
fi


if ! which curl > /dev/null; then
    do_apt_get_update
    sudo apt-get install -y curl
fi


LATEST_RELEASE="$(curl -Ls https://api.github.com/repos/dtcooper/raspotify/releases/latest | grep browser_download_url | head -n 1 | cut -d '"' -f 4)"
if [ -z "$LATEST_RELEASE" ]; then
    echo "Can't find latest Raspotify release on GitHub"
    exit 1
fi

do_apt_get_update
sudo apt-get install -y libasound2 adduser

cd /tmp
curl -Lo raspotify-latest.deb "$LATEST_RELEASE"
sudo dpkg -i --force-confold raspotify-latest.deb
rm raspotify-latest.deb
