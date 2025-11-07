.PHONY: all armhf arm64 amd64 riscv64 clean distclean
.DEFAULT_GOAL := all

RASPOTIFY_AUTHOR?=Kim Tore Jensen <kimtjen@gmail.com>

builder:
	docker build --pull -t raspotify .
	docker build --pull -t raspotify_riscv64 -f Dockerfile.riscv64 .

armhf:
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env ARCHITECTURE="armhf" \
		raspotify /mnt/raspotify/build.sh

arm64:
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env ARCHITECTURE="arm64" \
		raspotify /mnt/raspotify/build.sh

amd64:
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env ARCHITECTURE="amd64" \
		raspotify /mnt/raspotify/build.sh

riscv64:
	docker run \
			--rm \
			--volume "$(CURDIR):/mnt/raspotify" \
			--env PERMFIX_UID="$$(id -u)" \
			--env PERMFIX_GID="$$(id -g)" \
			--env RASPOTIFY_AUTHOR="$(RASPOTIFY_AUTHOR)" \
			--env ARCHITECTURE="riscv64" \
		raspotify_riscv64 /mnt/raspotify/build.sh

all: armhf arm64 amd64 riscv64

clean:
	rm -rf *.deb librespot asound-conf-wizard raspotify/usr/bin/librespot raspotify/usr/share raspotify/DEBIAN/control apt-repo

distclean: clean
	docker rmi -f raspotify || true
