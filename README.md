# Raspotify

_**Spotify Connect client for the Raspberry Pi that Just Works™.**_

## tl;dr

Install the Spotify Connect client on your Raspberry Pi,

```
curl -sL https://raw.github.com/dtcooper/raspotify/master/install.sh | sh -s
```

## Introduction

Raspotify is a Spotify Connect client for [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on the
Raspberry Pi that Just Works™. Raspotify is a Debian package which thinly wraps the awesome
[librespot](https://github.com/plietar/librespot) library by [Paul Lietar]([https://github.com/plietar) that
works out of the box, immediately after installation.

## Download Latest Version

Head on over to the [releases](https://github.com/dtcooper/raspotify/releases/latest) page to download the
most recent version and install the Debian package. Or follow the [directions below](#easy-installation).

### Requirements

Raspotify works on a Raspberry Pi running [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).
You'll need a Spotify Premium account in order to use Connect.

Raspotify should work on _any_ Pi but it has been tested on,

* Raspberry Pi (v1) model B
* Raspberry Pi 2 model B
* Raspberry Pi 3 Model B

### Easy Installation

Download the Debian package and install it. Run the following at the command line on your Pi to install
the latest version.

```
curl -sL https://raw.github.com/dtcooper/raspotify/master/install.sh | sh -s
```

That's it! Plug a speaker into your Pi on your local network, select the device in Spotify et voilà!

### Uninstalling

To uninstall, remove the package,

```
sudo apt-get remove -y raspotify
```

## Configuration

Raspotify works out of the box and should be discoverable on Spotify Connect on your local network, however
you can configure it by editing `/etc/default/raspotify` which passes arguments to
[librespot](https://github.com/plietar/librespot).

```
# /etc/default/raspotify -- Arguments for librespot

# Device name
DEVICE_NAME="raspotify"

# Bitrate, one of 96 (low quality), 160 (medium quality), or 320 (high quality)
BITRATE="160"

# Additional options, see `librespot -h' for more info. Can be safely left blank
OPTIONS=""

# To make your device visible on Spotify Connect across the Internet add your
# username and password which can be set via "Set device password", on your
# account settings.
#OPTIONS="--username <USERNAME> --password <PASSWORD>"
```

After editing restart the daemon by running `sudo service raspotify restart`.

## Building the Package Yourself

All that's required is [Docker](https://www.docker.com/) and a \*nix system (tested on Ubuntu 16.04 LTS and
macOS El Capitan).

```
git clone --recursive https://github.com/dtcooper/raspotify
cd raspotify
./build_raspotify.sh
```

There should be a built Debian package (a `.deb` file) in your project directory.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## Acknowledgments

Special thanks to [Paul Lietar]([https://github.com/plietar) for
[librespot](https://github.com/plietar/librespot), which Raspotify packages.
