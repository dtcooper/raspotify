# Raspotify

_**A [Spotify Connect](https://www.spotify.com/connect/) client for Raspberry Pi's
that Just Works™**_ *(Premium account required)*

More precisely Raspotify is a
[Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_\(file_format\)) for [Raspberry Pi OS lite](https://www.raspberrypi.org/downloads/raspbian/)
which thinly wraps the awesome
[librespot](https://github.com/librespot-org/librespot) library by
[Paul Lietar](https://github.com/plietar) and others up as a [systemd](https://en.wikipedia.org/wiki/Systemd) [daemon](https://en.wikipedia.org/wiki/Daemon_(computing)) that can easily installed on [Raspberry Pi's](https://www.raspberrypi.com/products).

Raspotify is primarily intended to be used in a _[headless enviroment](https://en.wikipedia.org/wiki/Headless_computer) (Raspberry Pi OS lite)_ and has been verified to work on:

* Raspberry Pi (v1) model B
* Raspberry Pi Zero
* Raspberry Pi 2 model B
* Raspberry Pi 3 model B and B+
* Raspberry Pi 4
* Orange Pi Zero LTS with Expansion board (for the 3.5mm jack)

_For desktop versions of Raspberry Pi OS [spotifyd](https://spotifyd.github.io/spotifyd/installation/Raspberry-Pi.html) offers similar functionality, much better PulseAudio compatibility and is a better choice._

## Installation

_**The easy way**_

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

That's it! Plug a speaker into your Pi on your local network, select the device
in Spotify et voilà!

_**The hard way**_

Essentially, here's what the easy installer does,

```bash
# Install curl and https apt transport
sudo apt-get -y install curl apt-transport-https

# Add the raspotify key to the keyring
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo tee /usr/share/keyrings/raspotify_key.asc  > /dev/null
sudo chmod 644 /usr/share/keyrings/raspotify_key.asc

# Create the apt repo
echo 'deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list

# Install package
sudo apt-get update
sudo apt-get -y install raspotify
```

Or you can just download the latest .deb package and install it manually from
here ([`raspotify-latest.deb`](https://dtcooper.github.io/raspotify/raspotify-latest.deb)),

_**Don't forget to checkout the [wiki](https://github.com/dtcooper/raspotify/wiki) for tips, tricks and configuration info!!!**_

## Donations

If you're so inclined, Bitcoin my address is `1PoDcAStyJoB7zZz2mny4KjtjiEu8S44ns`. :)

(I'd rather you donate to [librespot](https://github.com/librespot-org/librespot)
instead, but there's no public address for those folks.)

## Disclaimer

Per librespot's disclaimer, using librespot &mdash; the underlying library behind
raspotify &mdash; to connect to Spotify's API _"is probably forbidden by them."_
We've not received word about that, however use at your own risk.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar),  [librespot org](https://github.com/librespot-org) and it's many contributors for 
[librespot](https://github.com/librespot-org/librespot),
which Raspotify packages. Without [librespot](https://github.com/librespot-org/librespot),
Raspotify would simply not exist.

## Final Note

_...and remember kids, have fun!_
