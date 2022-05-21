.PHONY: all armhf arm64 amd64 clean distclean
.DEFAULT_GOAL := all

RASPOTIFY_AUTHOR?=David Cooper <david@dtcooper.com>

armhf:
	docker build -t raspotify .
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env BUILD_TARGET="armv7-unknown-linux-gnueabihf" \
			--env ARCHITECTURE="armhf" \
		raspotify /mnt/raspotify/build.sh

arm64:
	docker build -t raspotify .
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env BUILD_TARGET="aarch64-unknown-linux-gnu" \
			--env ARCHITECTURE="arm64" \
		raspotify /mnt/raspotify/build.sh

amd64:
	docker build -t raspotify .
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env BUILD_TARGET="x86_64-unknown-linux-gnu" \
			--env ARCHITECTURE="amd64" \
		raspotify /mnt/raspotify/build.sh

all: armhf arm64 amd64

clean:
	rm -rf *.deb librespot raspotify/usr raspotify/DEBIAN/control apt-repo

distclean: clean
	docker rmi -f raspotify || true
