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

if [ $(ls -1 *.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one .deb package needs to be in folder.'
    exit 1
fi

DEB_PKG_NAME="$(ls -1 *.deb | head -n 1)"
echo "Using package: $DEB_PKG_NAME"

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
Architectures: armhf
SignWith: $GPG_KEY_ID
EOF

reprepro includedeb jessie "../$DEB_PKG_NAME"
reprepro includedeb raspotify "../$DEB_PKG_NAME"
rm -rf conf db

ln -fs "$(find . -name '*.deb' -type f -printf '%P\n' -quit)" raspotify-latest.deb

echo "Repo created in directory apt-repo with package $DEB_PKG_NAME"

gpg --armor --export "$GPG_KEY_ID" > key.asc
cp -v ../README.md ../LICENSE ../install.sh .
git add -A
git -c 'user.name=Automated Release' -c 'user.email=automated-release@users.noreply.github.com' \
    commit -m "Update gh-pages apt repository (released tag $RELEASE_TAG)"
git push origin gh-pages
