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

    cd /mnt
    RASPOTIFY_GIT_VER="$(git describe --tags --always --dirty=-modified 2>/dev/null || echo unknown)"

    cd librespot
    LIBRESPOT_GIT_REV="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

    DEB_PKG_VER="${RASPOTIFY_GIT_VER}~librespot-${LIBRESPOT_GIT_REV}-1"
    DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_armhf.deb"
    sed "s/<<<VERSION>>>/$DEB_PKG_VER/g" /mnt/control.debian.tmpl > /mnt/raspotify/DEBIAN/control

    cargo build --release --target arm-unknown-linux-gnueabihf --no-default-features --features alsa-backend

    mkdir -p /mnt/raspotify/usr/bin
    cp -v /build/arm-unknown-linux-gnueabihf/release/librespot /mnt/raspotify/usr/bin

    # Strip dramatically decreases the size
    arm-linux-gnueabihf-strip /mnt/raspotify/usr/bin/librespot

    cd /mnt
    fakeroot dpkg-deb -b raspotify "$DEB_PKG_NAME"
    echo "Package built as $DEB_PKG_NAME"
fi
