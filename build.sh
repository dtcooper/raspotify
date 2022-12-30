#!/bin/sh

if [ "$INSIDE_DOCKER_CONTAINER" != "1" ]; then
	echo "Must be run in docker container"
	exit 1
fi

echo "Building in docker container"

set -e
cd /mnt/raspotify

# Get the git rev of raspotify for .deb versioning
RASPOTIFY_GIT_VER="$(git describe --tags "$(git rev-list --tags --max-count=1)" 2>/dev/null || echo unknown)"

if [ ! -d librespot ]; then
	echo "No directory named librespot exists! Cloning..."
	# Use a vendored version of librespot.
	# https://github.com/librespot-org/librespot does not regularly or really ever update their dependencies on released versions.
	# https://github.com/librespot-org/librespot/pull/1068
	git clone https://github.com/JasonLG1979/librespot
	cd librespot
	git checkout raspotify
	cd /mnt/raspotify
fi

cd librespot

# Get the git rev of librespot for .deb versioning
LIBRESPOT_VER="$(git describe --tags "$(git rev-list --tags --max-count=1)" 2>/dev/null || echo unknown)"
LIBRESPOT_HASH="$(git rev-parse HEAD | cut -c 1-7 2>/dev/null || echo unknown)"

# Build librespot
cargo build --jobs "$(nproc)" --profile raspotify --target "$BUILD_TARGET" --no-default-features --features "alsa-backend pulseaudio-backend"

# Copy librespot to pkg root
cd /mnt/raspotify

cp -v /build/"$BUILD_TARGET"/raspotify/librespot raspotify/usr/bin

# Copy over copyright files
DOC_DIR="raspotify/usr/share/doc/raspotify"
mkdir -p "$DOC_DIR"
cp -v LICENSE "$DOC_DIR/copyright"
cp -v librespot/LICENSE "$DOC_DIR/librespot.copyright"

# Markdown to plain text for readme
pandoc -f markdown -t plain --columns=80 README.md |
	sed "s/LICENSE/copyright/" | unidecode -e utf8 >"$DOC_DIR/readme"

# Compute final package version + filename for Debian control file
DEB_PKG_VER="${RASPOTIFY_GIT_VER}~librespot.${LIBRESPOT_VER}-${LIBRESPOT_HASH}"
DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_${ARCHITECTURE}.deb"

# https://www.debian.org/doc/debian-policy/ch-controlfields.html#installed-size
# "The disk space is given as the integer value of the estimated installed size in bytes,
# divided by 1024 and rounded up."
INSTALLED_SIZE="$((($(du -bs raspotify --exclude=raspotify/DEBIAN/control | cut -f 1) + 2048) / 1024))"

jinja2 \
	-D "VERSION=$DEB_PKG_VER" \
	-D "RUST_VERSION=$(rustc -V)" \
	-D "RASPOTIFY_AUTHOR=$RASPOTIFY_AUTHOR" \
	-D "ARCHITECTURE=$ARCHITECTURE" \
	-D "INSTALLED_SIZE=$INSTALLED_SIZE" \
	control.debian.tmpl >raspotify/DEBIAN/control

# Finally, build debian package
dpkg-deb -b raspotify "$DEB_PKG_NAME"

PACKAGE_SIZE="$(du -bs "$DEB_PKG_NAME" | cut -f 1)"

echo "Raspotify package built as $DEB_PKG_NAME"
echo "Raspotify package estimated Size $PACKAGE_SIZE (Bytes)"
echo "Raspotify package estimated Installed Size $INSTALLED_SIZE (KiB)"

if [ ! -d asound-conf-wizard ]; then
	echo "No directory named asound-conf-wizard exists! Cloning..."
	git clone https://github.com/JasonLG1979/asound-conf-wizard.git
fi

cd asound-conf-wizard

# Build asound-conf-wizard
/build/cache/bin/cargo-deb --profile default --target "$BUILD_TARGET" -- --jobs "$(nproc)"

cd /build/"$BUILD_TARGET"/debian

AWIZ_DEB_PKG_NAME=$(ls -1 -- *.deb)

cp -v "$AWIZ_DEB_PKG_NAME" /mnt/raspotify

echo "asound-conf-wizard package built as $AWIZ_DEB_PKG_NAME"

# Perm fixup. Not needed on macOS, but is on Linux
chown -R "$PERMFIX_UID:$PERMFIX_GID" /mnt/raspotify 2>/dev/null || true
