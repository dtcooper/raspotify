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
		raspotify /mnt/raspotify/build.sh

clean:
	rm -rf *.deb librespot raspotify/usr raspotify/DEBIAN/control apt-repo

distclean: clean
	docker rmi -f raspotify || true

all: raspotify_*.deb
