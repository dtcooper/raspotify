#!/bin/sh
# vi: set noexpandtab sw=4 ts=4 sts=4:

if [ "$INSIDE_DOCKER_CONTAINER" != "1" ]; then
	echo "Must be run in docker container"
	exit 1
fi

set -e

now() {
	date -u +%s.%N
}

duration_since() {
	duration_secs=$(echo "$(now) - $1" | bc)

	hours=$(echo "$duration_secs / 3600" | bc)
	remaining_secs=$(echo "$duration_secs - ($hours * 3600)" | bc)

	mins=$(echo "$remaining_secs / 60" | bc)
	secs=$(echo "$remaining_secs - ($mins * 60)" | bc)

	if [ "$((mins + hours))" -eq 0 ]; then
		printf "%fs\n" "$secs"
	elif [ "$hours" -eq 0 ]; then
		printf "%dm %fs\n" "$mins" "$secs"
	else
		printf "%dh %dm %fs\n" "$hours" "$mins" "$secs"
	fi
}

packages() {
	echo "Build $ARCHITECTURE packages..."

	START_PACKAGES=$(now)

	cd /mnt/raspotify
	git submodule init librespot
	git submodule update librespot

	DOC_DIR="raspotify/usr/share/doc/raspotify"

	if [ ! -d "$DOC_DIR" ]; then
		echo "Copy copyright & readme files..."
		mkdir -p "$DOC_DIR"
		cp -v LICENSE "$DOC_DIR/copyright"
		cp -v readme "$DOC_DIR/readme"
		cp -v librespot/LICENSE "$DOC_DIR/librespot.copyright"
	fi

	cd librespot

	echo 'Obtaining latest Librespot Git repository tag for DEB package version suffix ...'
	LIBRESPOT_VER="$(git describe --tags "$(git rev-list --tags --max-count=1)" || echo unknown)"
	LIBRESPOT_HASH="$(git rev-parse HEAD | cut -c 1-7 || echo unknown)"

	echo "Build Librespot binary..."
	cargo build --jobs "$(nproc)" --profile release --target "$BUILD_TARGET" --no-default-features --features "alsa-backend pulseaudio-backend with-avahi"

	echo "Copy Librespot binary to package root..."
	cd /mnt/raspotify

	cp -v /build/"$BUILD_TARGET"/release/librespot raspotify/usr/bin

	# Compute final package version + filename for Debian control file
	DEB_PKG_VER="${RASPOTIFY_GIT_VER}~librespot.${LIBRESPOT_VER}-${LIBRESPOT_HASH}"
	DEB_PKG_NAME="raspotify_${DEB_PKG_VER}_${ARCHITECTURE}.deb"

	# https://www.debian.org/doc/debian-policy/ch-controlfields.html#installed-size
	# "The disk space is given as the integer value of the estimated installed size
	# in bytes, divided by 1024 and rounded up."
	INSTALLED_SIZE="$((($(du -bs raspotify --exclude=raspotify/DEBIAN/control | cut -f 1) + 2048) / 1024))"

	echo "Generate Debian control..."
	export DEB_PKG_VER
	export INSTALLED_SIZE
	envsubst <control.debian.tmpl >raspotify/DEBIAN/control

	echo "Build Raspotify deb..."
	dpkg-deb -b raspotify "$DEB_PKG_NAME"

	PACKAGE_SIZE="$(du -bs "$DEB_PKG_NAME" | cut -f 1)"
	BUILD_TIME=$(duration_since "$START_PACKAGES")

	echo "Raspotify package built as:  $DEB_PKG_NAME"
	echo "Estimated package size:      $PACKAGE_SIZE (Bytes)"
	echo "Estimated installed size:    $INSTALLED_SIZE (KiB)"
	echo "Build time:                  $BUILD_TIME"

	START_AWIZ=$(now)

	if [ ! -d asound-conf-wizard ]; then
		echo "Get https://github.com/JasonLG1979/asound-conf-wizard..."
		git clone https://github.com/JasonLG1979/asound-conf-wizard.git
	fi

	cd asound-conf-wizard

	echo "Build asound-conf-wizard deb..."
	cargo-deb --profile default --target "$BUILD_TARGET" -- --jobs "$(nproc)"

	cd /build/"$BUILD_TARGET"/debian

	AWIZ_DEB_PKG_NAME=$(ls -1 -- *.deb)

	echo "Copy asound-conf-wizard deb to raspotify root..."
	cp -v "$AWIZ_DEB_PKG_NAME" /mnt/raspotify

	cd /mnt/raspotify

	INSTALLED_SIZE=$(dpkg -f "$AWIZ_DEB_PKG_NAME" Installed-Size)
	PACKAGE_SIZE="$(du -bs "$AWIZ_DEB_PKG_NAME" | cut -f 1)"
	BUILD_TIME=$(duration_since "$START_AWIZ")

	echo "asound-conf-wizard package built as:  $AWIZ_DEB_PKG_NAME"
	echo "Estimated package size:               $PACKAGE_SIZE (Bytes)"
	echo "Estimated installed size:             $INSTALLED_SIZE (KiB)"
	echo "Build time:                           $BUILD_TIME"

	BUILD_TIME=$(duration_since "$START_PACKAGES")

	echo "$ARCHITECTURE packages build time: $BUILD_TIME"
}

build_armhf() {
	ARCHITECTURE="armhf"
	BUILD_TARGET="armv7-unknown-linux-gnueabihf"
	packages
}

build_arm64() {
	ARCHITECTURE="arm64"
	BUILD_TARGET="aarch64-unknown-linux-gnu"
	packages
}

build_amd64() {
	ARCHITECTURE="amd64"
	BUILD_TARGET="x86_64-unknown-linux-gnu"
	packages
}

build_riscv64() {
	ARCHITECTURE="riscv64"
	BUILD_TARGET="riscv64gc-unknown-linux-gnu"
	packages
}

build_all() {
	build_armhf
	build_arm64
	build_amd64
}

START_BUILDS=$(now)

cd /mnt/raspotify

echo 'Obtaining latest Git repository tag for DEB package version ...'
RASPOTIFY_GIT_VER="$(git describe --tags "$(git rev-list --tags --max-count=1)" || :)"
if [ -z "$RASPOTIFY_GIT_VER" ]; then
	# Derive from origin URL whether this is dtcooper/raspotify and hence supposed to have tags.
	# If so, exit right here, else get tags from dtcooper/raspotify via GitHub API, since forks often do not have any tags.
	url="$(git remote get-url origin || :)"
	if [ "$url" = 'https://github.com/dtcooper/raspotify' ] || [ "$url" = 'https://github.com/dtcooper/raspotify/' ] || [ "$url" = 'https://github.com/dtcooper/raspotify.git' ]; then
		echo 'E: Could not obtain any tag. Exiting ...'
		exit 1
	else
		echo 'W: Could not obtain latest tag from local repository. Obtaining it from upstream: https://api.github.com/repos/dtcooper/raspotify/tags'
		RASPOTIFY_GIT_VER="$(curl -sSf  "https://api.github.com/repos/dtcooper/raspotify/tags" | awk -F\" '/^ *"name": "/{print $4;exit}' || :)"
		if [ -z "$RASPOTIFY_GIT_VER" ]; then
			echo 'E: Could not obtain latest tag from upstream repository either. Exiting ...'
			exit 1
		fi
	fi
fi
RASPOTIFY_HASH="$(git rev-parse HEAD | cut -c 1-7 || echo unknown)"

echo "Build Raspotify $RASPOTIFY_GIT_VER~$RASPOTIFY_HASH..."

case $ARCHITECTURE in
"armhf")
	build_armhf
	;;
"arm64")
	build_arm64
	;;
"amd64")
	build_amd64
	;;
"riscv64")
	build_riscv64
	;;
"all")
	build_all
	;;
esac

# Fix broken permissions resulting from running the Docker container as root.
[ $(id -u) -eq 0 ] && chown -R "$PERMFIX_UID:$PERMFIX_GID" /mnt/raspotify

BUILD_TIME=$(duration_since "$START_BUILDS")

echo "Total packages build time: $BUILD_TIME"
