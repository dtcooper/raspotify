#!/bin/sh

# We're NOT in the docker container, so let's build it and enter
if [ "$1" != 'in_docker_container' ]; then
    cd "$(dirname "$0")"

    if [ ! -d librespot ]; then
        echo "No directory named librespot exists! Cloning..."
        git clone https://github.com/plietar/librespot.git
    fi

    # Build Docker container and run script
    docker build -t raspotify .
    docker run --rm -v "$(pwd):/mnt" raspotify
else
    echo 'Building in docker container'

    cd /librespot
    LIBRESPOT_GIT_REV="$(git rev-parse --short HEAD)"

    DEB_PKG_VER="$(grep '^Version:' /mnt/raspotify/DEBIAN/control | sed 's/^Version: //')"
    if echo "$DEB_PKG_VER" | fgrep -vq "$LIBRESPOT_GIT_REV"; then
        echo 'Librespot git revision not found in package version. Aborting.'
        exit 1
    fi

    DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_armhf.deb"

    cargo build --release --target arm-unknown-linux-gnueabihf --no-default-features --features alsa-backend

    mkdir -p /mnt/raspotify/usr/bin
    cp -v /build/arm-unknown-linux-gnueabihf/release/librespot /mnt/raspotify/usr/bin

    # Strip dramatically decreases the size
    arm-linux-gnueabihf-strip /mnt/raspotify/usr/bin/librespot

    cd /mnt
    fakeroot dpkg-deb -b raspotify "$DEB_PKG_NAME"
    echo "Package built as $DEB_PKG_NAME"
fi
