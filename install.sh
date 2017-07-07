#!/bin/sh

SOURCE_REPO="deb https://dtcooper.github.io/raspotify jessie main"

# Install script for Raspotify. Adds the Debian repo and installs.
set -e

run_on_pi_only() {
    echo "Raspotify installer only runs on a Raspberry Pi"
    exit 1
}

if ! which apt-get apt-key > /dev/null; then
    run_on_pi_only
fi

# You probably have these
PREREQ_PACKAGES="curl apt-transport-https lsb-release"
PREREQ_PACKAGES_TO_INSTALL=
for package in $PREREQ_PACKAGES; do
    if ! dpkg-query --show --showformat='${db:Status-Status}\n' "$package" 2> /dev/null | grep -q '^installed$'; then
        PREREQ_PACKAGES_TO_INSTALL="$package $PREREQ_PACKAGES_TO_INSTALL"
    fi
done

if [ "$PREREQ_PACKAGES_TO_INSTALL" ]; then
    sudo apt-get update
    sudo apt-get -y install $PREREQ_PACKAGES_TO_INSTALL
fi

if lsb_release -si | fgrep -ivq raspbian; then
    run_on_pi_only
fi

# Add public key to apt
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo "$SOURCE_REPO" | sudo tee /etc/apt/sources.list.d/raspotify.list

sudo apt-get update
sudo apt-get -y install raspotify
