# Raspotify

_**Spotify Connect client for the Raspberry Pi that Just Works™.**_

## tl;dr

Install the Spotify Connect client on your Raspberry Pi,

```
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

## Introduction

Raspotify is a [Spotify Connect](https://www.spotify.com/connect/) client for
[Raspbian](https://www.raspberrypi.org/downloads/raspbian/) on the Raspberry Pi
that Just Works™. Raspotify is a
[Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_\(file_format\))
which thinly wraps the awesome
[librespot](https://github.com/librespot-org/librespot) library by
[Paul Lietar](https://github.com/plietar) and others. It works out of the box on
all three revisions of the Pi, immediately after installation.

## Download Latest Version

Head on over to the [releases](https://github.com/dtcooper/raspotify/releases/latest)
page to download themost recent version and install the Debian package. Or follow
the [directions below](#easy-installation).

### Requirements

Raspotify works on a Raspberry Pi running [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).
You'll need a [Spotify Premium](https://www.spotify.com/premium/) account in order
to use Connect.

Raspotify should work on _any_ Pi but it has been tested on,

* Raspberry Pi (v1) model B
* Raspberry Pi 2 model B
* Raspberry Pi 3 model B and B+

### Easy Installation

This command downloads and installs the Debian package and adds its apt repository,
which ensures you'll always be up to date with upstream changes.

```
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

That's it! Plug a speaker into your Pi on your local network, select the device
in Spotify et voilà!

### Hard installation

Essentially, here's what the easy installer does,

```
# Install curl and https apt transport
sudo apt-get -y install curl apt-transport-https

# Add repo and its GPG key
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo apt-key add -v -
echo 'deb https://dtcooper.github.io/raspotify jessie main' | sudo tee /etc/apt/sources.list.d/raspotify.list

# Install package
sudo apt-get update
sudo apt-get -y install raspotify
```

Or just download the latest .deb package and install it manually:

 * [`raspotify-latest.deb`](https://dtcooper.github.io/raspotify/raspotify-latest.deb)

### Uninstalling

To uninstall, remove the package,

```
sudo apt-get remove -y raspotify
```

To completely remove Raspotify and its Debian repository from your system try,
```
sudo apt-get remove -y --purge raspotify
sudo rm -v /etc/apt/sources.list.d/raspotify.list
```

## Configuration

Raspotify works out of the box and should be discoverable by Spotify Connect on
your local network, however you can configure it by editing `/etc/default/raspotify`
which passes arguments to [librespot](https://github.com/librespot-org/librespot).

```
# /etc/default/raspotify -- Arguments/configuration for librespot

# Device name on Spotify Connect
#DEVICE_NAME="raspotify"

# Bitrate, one of 96 (low quality), 160 (default quality), or 320 (high quality)
#BITRATE="160"

# Additional command line arguments for librespot can be set below.
# See `librespot -h` for more info. Make sure whatever arguments you specify
# aren't already covered by other variables in this file. (See the daemon's
# config at `/lib/systemd/system/raspotify.service` for more technical details.)
#
# To make your device visible on Spotify Connect across the Internet add your
# username and password which can be set via "Set device password", on your
# account settings, use `--username` and `--password`.
#
# To choose a different output device (ie a USB audio dongle or HDMI audio out),
# use `--device` with something like `--device hw:0,1`. Your mileage may vary.
#
#OPTIONS="--username <USERNAME> --password <PASSWORD>"

# Uncomment to use a cache for downloaded audio files. Cache is disabled by
# default. It's best to leave this as-is if you want to use it, since
# permissions are properly set on the directory `/var/cache/raspotify'.
#CACHE_ARGS="--cache /var/cache/raspotify"

# By default, the volume normalization is enabled, add alternative volume
# arguments here if you'd like, but these should be fine.
#VOLUME_ARGS="--enable-volume-normalisation --linear-volume --initial-volume=100"

# Backend could be set to pipe here, but it's for very advanced use cases of
# librespot, so you shouldn't need to change this under normal circumstances.
#BACKEND_ARGS="--backend alsa"
```

After editing restart the daemon by running: `sudo systemctl restart raspotify`

## Building the Package Yourself

All that's required is [Docker](https://www.docker.com/) on a \*nix system with
[git](https://git-scm.com/) and [Make](https://www.gnu.org/software/make/). It
can be built on any amd64 platform that runs docker using Raspberry Pi's
cross-compiler (tested on Ubuntu 16.04 LTS and macOS El Capitan).

```
git clone https://github.com/dtcooper/raspotify
cd raspotify
make
```

There should be a built Debian package (a `.deb` file) in your project directory.

> #### Note About Raspotify's APT Repository
>
> You _can_ actually use GitHub to host an APT repository for Raspotify as I
> have done, but that's very much out of the scope of this Readme. Have a look
> at the [Makefile](Makefile)'s `apt-repo` and `apt-deploy` directives, and its
> `APT_GPG_KEY` and `APT_GH_PAGES_REPO` variables. You'll _at least_ need this
> repository cloned on GitHub, GitHub Pages enabled for the `gh-pages` branch,
> and a [GPG](https://www.gnupg.org/) key. I **can't** and **won't** support any
> users trying to do this at this time, but _have fun and good luck!_

## Troubleshooting

> *My volume on Spotify is 100% and it's still too quiet!*

Have you tried turning the volume up using the command `alsamixer`?

> *Other issues*

File an issue and if we get it sorted, I'll add to this list.

## Donations

If you're so inclined, Bitcoin my address is `1PoDcAStyJoB7zZz2mny4KjtjiEu8S44ns`. :)

(I'd rather you donate to [librespot](https://github.com/librespot-org/librespot)
instead, but there's no public address for those folks.)

## Final Note

_...and remember kids, have fun!_

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar) for
[librespot](https://github.com/librespot-org/librespot) (and its additional authors),
which Raspotify packages. Without [librespot](https://github.com/librespot-org/librespot),
Raspotify would simply not exist.
