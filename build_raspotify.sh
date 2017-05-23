#!/bin/sh

set +e

cd "$(dirname "$0")"

if git submodule status librespot | grep -q '^-'
then
    echo 'No librespot directory found. Did you clone with submodules?'
    exit 1
fi

# We're NOT in the docker container, so let's build it
if [ "$1" != 'in_docker_container' ]
then
    echo 'Not in docker container. Building container...'
    BASEDIR="$(pwd)"

    # Build librespot-cross Docker container
    cd librespot
    docker build -t librespot-cross -f contrib/Dockerfile .

    echo 'Running script...'
    docker run \
        -v "$BASEDIR":/pkgbuild \
        librespot-cross \
        /pkgbuild/build_raspotify.sh in_docker_container $@
else
    echo 'Building in docker container'

    # Get versions to prepare build
    cd /pkgbuild/librespot
    LIBRESPOT_GIT_REV="$(git rev-parse --short HEAD)"
    cd /src

    DEB_PKG_VER="$(grep '^Version:' /pkgbuild/raspotify/DEBIAN/control | sed 's/^Version: //')"
    if echo "$DEB_PKG_VER" | fgrep -vq "$LIBRESPOT_GIT_REV" && [ "$2" != '-f' -a "$2" != '--force' ]
    then
        echo 'Librespot git revision not found in package version. Is this correct? Use `--force` if so.'
        exit 1
    fi

    DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_armhf.deb"

    # Cross compile
    cargo build --release --target arm-unknown-linux-gnueabihf --no-default-features --features alsa-backend
    cd /pkgbuild

    mkdir -p raspotify/usr/bin
    cp /build/arm-unknown-linux-gnueabihf/release/librespot raspotify/usr/bin

    # Strip substantially decreases size of binary
    arm-linux-gnueabi-strip raspotify/usr/bin/librespot

    # Build debian package
    fakeroot dpkg-deb -b raspotify "$DEB_PKG_NAME"

    echo "Package built as $DEB_PKG_NAME"
fi
