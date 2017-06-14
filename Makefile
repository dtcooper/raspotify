raspotify_*.deb:
		./build.sh

clean:
		rm -rf *.deb librespot raspotify/usr raspotify/DEBIAN/control

.PHONY: all
all: raspotify_*.deb
