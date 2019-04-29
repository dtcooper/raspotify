#!/bin/sh

if [ "$INSIDE_DOCKER_CONTAINER" != "1" ]; then
    echo "Must be run in docker container"
    exit 1
fi

echo 'Making apt repo in Docker container'

set -e
cd /mnt/raspotify

if [ -z "$GPG_KEY" ]; then
    echo "Set environment variable GPG_KEY"
    exit 1
fi

DEB_PKG_NAME="$(ls -1 *.deb | head -n 1)"
if [ -z "$DEB_PKG_NAME" ]; then
    echo 'No .deb package found! Exiting.'
    exit 1
fi

echo "Using package: $DEB_PKG_NAME"

cd apt-repo

# Clear out old stuff
rm -rf conf db pool dists

mkdir conf
# Keep jessie for backward compatibility
cat <<EOF > conf/distributions
Codename: jessie
Components: main
Architectures: armhf
SignWith: $GPG_KEY

Codename: raspotify
Components: main
Architectures: armhf
SignWith: $GPG_KEY
EOF

reprepro includedeb jessie "../$DEB_PKG_NAME"
reprepro includedeb raspotify "../$DEB_PKG_NAME"
rm -rf conf db

ln -fs "$(find . -name '*.deb' -type f -printf '%P\n' -quit)" raspotify-latest.deb

# Perm fixup. Not needed on macOS, but is on Linux
chown -R "$PERMFIX_UID:$PERMFIX_GID" /mnt/raspotify/* 2> /dev/null

echo "Repo created in directory apt-repo with package $DEB_PKG_NAME"
