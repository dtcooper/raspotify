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

if [ $(ls -1 raspotify*_armhf.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one raspotify*_armhf.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 raspotify*_arm64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one raspotify*_arm64.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 raspotify*_amd64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one raspotify*_amd64.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 raspotify*_riscv64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one raspotify*_riscv64.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 asound-conf-wizard*_armhf.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one asound-conf-wizard*_armhf.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 asound-conf-wizard*_arm64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one asound-conf-wizard*_arm64.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 asound-conf-wizard*_amd64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one asound-conf-wizard*_amd64.deb package needs to be in folder.'
    exit 1
fi

if [ $(ls -1 asound-conf-wizard*_riscv64.deb | wc -l) -ne 1 ]; then
    echo 'Exactly one asound-conf-wizard*_riscv64.deb package needs to be in folder.'
    exit 1
fi

RASPOTIFY_ARMHF_DEB_PKG_NAME="$(ls -1 raspotify*_armhf.deb | head -n 1)"
echo "Using package: $RASPOTIFY_ARMHF_DEB_PKG_NAME"

RASPOTIFY_ARM64_DEB_PKG_NAME="$(ls -1 raspotify*_arm64.deb | head -n 1)"
echo "Using package: $RASPOTIFY_ARM64_DEB_PKG_NAME"

RASPOTIFY_AMD64_DEB_PKG_NAME="$(ls -1 raspotify*_amd64.deb | head -n 1)"
echo "Using package: $RASPOTIFY_AMD64_DEB_PKG_NAME"

RASPOTIFY_RISCV64_DEB_PKG_NAME="$(ls -1 raspotify*_riscv64.deb | head -n 1)"
echo "Using package: $RASPOTIFY_RISCV64_DEB_PKG_NAME"

AWIZ_ARMHF_DEB_PKG_NAME="$(ls -1 asound-conf-wizard*_armhf.deb | head -n 1)"
echo "Using package: $AWIZ_ARMHF_DEB_PKG_NAME"

AWIZ_ARM64_DEB_PKG_NAME="$(ls -1 asound-conf-wizard*_arm64.deb | head -n 1)"
echo "Using package: $AWIZ_ARM64_DEB_PKG_NAME"

AWIZ_AMD64_DEB_PKG_NAME="$(ls -1 asound-conf-wizard*_amd64.deb | head -n 1)"
echo "Using package: $AWIZ_AMD64_DEB_PKG_NAME"

AWIZ_RISCV64_DEB_PKG_NAME="$(ls -1 asound-conf-wizard*_riscv64.deb | head -n 1)"
echo "Using package: $AWIZ_RISCV64_DEB_PKG_NAME"

echo "Importing gpg key"
echo "$GPG_SECRET_KEY_BASE64" | base64 -d | gpg --import

cd apt-repo

# Clear out old stuff
rm -rf conf db pool dists

mkdir conf
cat <<EOF > conf/distributions
Codename: raspotify
Components: main
Architectures: armhf arm64 amd64 riscv64
SignWith: $GPG_KEY_ID
EOF

reprepro includedeb raspotify "../$RASPOTIFY_ARMHF_DEB_PKG_NAME"
reprepro includedeb raspotify "../$RASPOTIFY_ARM64_DEB_PKG_NAME"
reprepro includedeb raspotify "../$RASPOTIFY_AMD64_DEB_PKG_NAME"
reprepro includedeb raspotify "../$RASPOTIFY_RISCV64_DEB_PKG_NAME"
reprepro includedeb raspotify "../$AWIZ_ARMHF_DEB_PKG_NAME"
reprepro includedeb raspotify "../$AWIZ_ARM64_DEB_PKG_NAME"
reprepro includedeb raspotify "../$AWIZ_AMD64_DEB_PKG_NAME"
reprepro includedeb raspotify "../$AWIZ_RISCV64_DEB_PKG_NAME"
rm -rf conf db

ln -fs "$(find . -name 'raspotify*_armhf.deb' -type f -printf '%P\n' -quit)" raspotify-latest_armhf.deb
ln -fs "$(find . -name 'raspotify*_arm64.deb' -type f -printf '%P\n' -quit)" raspotify-latest_arm64.deb
ln -fs "$(find . -name 'raspotify*_amd64.deb' -type f -printf '%P\n' -quit)" raspotify-latest_amd64.deb
ln -fs "$(find . -name 'raspotify*_riscv64.deb' -type f -printf '%P\n' -quit)" raspotify-latest_riscv64.deb
ln -fs "$(find . -name 'asound-conf-wizard*_armhf.deb' -type f -printf '%P\n' -quit)" asound-conf-wizard-latest_armhf.deb
ln -fs "$(find . -name 'asound-conf-wizard*_arm64.deb' -type f -printf '%P\n' -quit)" asound-conf-wizard-latest_arm64.deb
ln -fs "$(find . -name 'asound-conf-wizard*_amd64.deb' -type f -printf '%P\n' -quit)" asound-conf-wizard-latest_amd64.deb
ln -fs "$(find . -name 'asound-conf-wizard*_riscv64.deb' -type f -printf '%P\n' -quit)" asound-conf-wizard-latest_riscv64.deb

echo "Repo created in directory apt-repo with packages:"
echo "$RASPOTIFY_ARMHF_DEB_PKG_NAME, $RASPOTIFY_ARM64_DEB_PKG_NAME, $RASPOTIFY_AMD64_DEB_PKG_NAME, $RASPOTIFY_RISCV64_DEB_PKG_NAME"
echo "$AWIZ_ARMHF_DEB_PKG_NAME, $AWIZ_ARM64_DEB_PKG_NAME, $AWIZ_AMD64_DEB_PKG_NAME, and $AWIZ_RISCV64_DEB_PKG_NAME."

gpg --armor --export "$GPG_KEY_ID" > key.asc
cp -v ../README.md ../LICENSE ../install.sh .
git add -A
git -c 'user.name=Automated Release' -c 'user.email=automated-release@users.noreply.github.com' \
    commit -m "Update gh-pages apt repository (released tag $RELEASE_TAG)"
git push origin gh-pages
