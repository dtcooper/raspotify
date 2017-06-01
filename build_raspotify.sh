#!/bin/sh

# We're NOT in the docker container, so let's build it and enter
if [ "$1" != 'in_docker_container' ]; then
    cd "$(dirname "$0")"

    if git submodule status librespot | grep -q '^-'; then
        echo 'No librespot directory found. Did you clone with submodules?'
        exit 1
    fi


    cd librespot
    LIBRESPOT_GIT_REV="$(git rev-parse --short HEAD)"
    cd ..

    # Build Docker container and run script
    docker build -t raspotify -f Dockerfile .
    docker run \
        -v "$(pwd):/mnt" \
        --env LIBRESPOT_GIT_REV="$LIBRESPOT_GIT_REV" \
        raspotify
else
    echo 'Building in docker container'

    cd /librespot

    DEB_PKG_VER="$(grep '^Version:' /mnt/raspotify/DEBIAN/control | sed 's/^Version: //')"
    if echo "$DEB_PKG_VER" | fgrep -vq "$LIBRESPOT_GIT_REV" && [ "$2" != '-f' -a "$2" != '--force' ]; then
        echo 'Librespot git revision not found in package version. Is this correct?'
        exit 1
    fi

    DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_armhf.deb"

    cargo build --release --target arm-unknown-linux-gnueabihf --no-default-features --features alsa-backend

    mkdir -p /mnt/raspotify/usr/bin
    cp -v /build/arm-unknown-linux-gnueabihf/release/librespot /mnt/raspotify/usr/bin

    cd /mnt
    fakeroot dpkg-deb -b raspotify "$DEB_PKG_NAME"
    echo "Package built as $DEB_PKG_NAME"
fi
