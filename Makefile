.PHONY: all clean container

RASPOTIFY_AUTHOR?=David Cooper <david@dtcooper.com>

raspotify_*.deb:
	docker build -t raspotify .
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env BUILD_TARGET="arm-unknown-linux-gnueabihf" \
			--env BUILD_LINKER="gcc-wrapper" \
			--env ARCHITECTURE="armhf" \
		raspotify /mnt/raspotify/build.sh
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env BUILD_TARGET="aarch64-unknown-linux-gnu" \
			--env BUILD_LINKER="aarch64-linux-gnu-gcc" \
			--env ARCHITECTURE="arm64" \
		raspotify /mnt/raspotify/build.sh

clean:
	rm -rf *.deb librespot raspotify/usr raspotify/DEBIAN/control apt-repo

distclean: clean
	docker rmi -f raspotify || true

all: raspotify_*.deb
