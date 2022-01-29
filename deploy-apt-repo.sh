#!/bin/sh

set -e

if [ ! -d apt-repo ]; then
    echo 'Clone gh-pages branch into apt-repo folder: '
    echo '    git clone -b gh-pages --single-branch git@github.com:dtcooper/raspotify.git apt-repo'
    exit 1
fi

if [ -z "$GPG_KEY_ID" ]; then
    echo 'Set environment variable GPG_KEY_ID'
    exit 1
fi

if [ -z "$GPG_SECRET_KEY_BASE64" ]; then
    echo 'Set environment variable GPG_SECRET_KEY_BASE64'
    exit 1
fi

if [ -z "$RELEASE_TAG" ]; then
    echo 'Set environment variable RELEASE_TAG'
    exit 1
fi

if [ $(ls -1 *_armhf.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one *_armhf.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 *_arm64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one *_arm64.deb package needs to be in folder.'
    exit 1
fi

ARMHF_DEB_PKG_NAME="$(ls -1 *_armhf.deb | head -n 1)"
echo "Using package: $ARMHF_DEB_PKG_NAME"

ARM64_DEB_PKG_NAME="$(ls -1 *_arm64.deb | head -n 1)"
echo "Using package: $ARM64_DEB_PKG_NAME"

echo "Importing gpg key"
echo "$GPG_SECRET_KEY_BASE64" | base64 -d | gpg --import

cd apt-repo

# Clear out old stuff
rm -rf conf db pool dists

mkdir conf
# Keep jessie for backward compatibility
cat <<EOF > conf/distributions
Codename: jessie
Components: main
Architectures: armhf
SignWith: $GPG_KEY_ID

Codename: raspotify
Components: main
Architectures: armhf arm64
SignWith: $GPG_KEY_ID
EOF

reprepro includedeb jessie "../$ARMHF_DEB_PKG_NAME"
reprepro includedeb raspotify "../$ARMHF_DEB_PKG_NAME"
reprepro includedeb raspotify "../$ARM64_DEB_PKG_NAME"
rm -rf conf db

ln -fs "$(find . -name '*_armhf.deb' -type f -printf '%P\n' -quit)" raspotify-latest_armhf.deb
ln -fs "$(find . -name '*_arm64.deb' -type f -printf '%P\n' -quit)" raspotify-latest_arm64.deb

echo "Repo created in directory apt-repo with packages $ARMHF_DEB_PKG_NAME and $ARM64_DEB_PKG_NAME"

gpg --armor --export "$GPG_KEY_ID" > key.asc
cp -v ../README.md ../LICENSE ../install.sh .
git add -A
git -c 'user.name=Automated Release' -c 'user.email=automated-release@users.noreply.github.com' \
    commit -m "Update gh-pages apt repository (released tag $RELEASE_TAG)"
git push origin gh-pages
