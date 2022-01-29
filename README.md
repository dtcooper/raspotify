# Raspotify

_**A [Spotify Connect](https://www.spotify.com/connect/) client for Raspberry Pi's
that Just Works™**_ *(Premium account required)*

More precisely Raspotify is a
[Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_\(file_format\)) for [Raspberry Pi OS lite (Bullseye)](https://www.raspberrypi.org/downloads/raspbian/)
which thinly wraps the awesome
[librespot](https://github.com/librespot-org/librespot) library by
[Paul Lietar](https://github.com/plietar) and others up as a [systemd](https://en.wikipedia.org/wiki/Systemd) [daemon](https://en.wikipedia.org/wiki/Daemon_(computing)) that can be easily installed on [Raspberry Pi's](https://www.raspberrypi.com/products).

Raspotify is primarily intended to be used in a _[headless enviroment](https://en.wikipedia.org/wiki/Headless_computer) (Raspberry Pi OS lite Bullseye)_ and has been verified to work on:

* ~~Raspberry Pi (v1) model B~~
* Raspberry Pi Zero * *(Your mileage may vary)*
* Raspberry Pi 2 model B
* Raspberry Pi 3 model B and B+
* Raspberry Pi 4
* Orange Pi Zero LTS with Expansion board (for the 3.5mm jack)

_For desktop versions of Raspberry Pi OS (and/or systems with PulseAudio installed) [spotifyd](https://spotifyd.github.io/spotifyd/installation/Raspberry-Pi.html) offers similar functionality, much better PulseAudio compatibility and is a better choice._

If you're looking for a turnkey audio solution for Raspberry Pi's with Spotify Connect support we recommend [moOde™ audio player](https://moodeaudio.org/).

# Migration from version <= 0.31.3 to 0.31.4+

⚠️ _**Version 0.31.4 introduces breaking changes to the Raspotify Package!!!**_ ⚠️

Please see the [wiki for details](https://github.com/dtcooper/raspotify/wiki/Migration-from-older-versions-to-0.31.4-and-beyond).

The short version is that you'll need to `sudo apt purge raspotify` and `sudo apt install raspotify` to make sure Raspotify is not left in a broken state if you're upgrading to 0.31.4.

If you've installed Raspotify after that version there's nothing to see here move along.

## Aarch64

64bit packages are not provided and installing on 64bit systems is not _officially_ supported but is possible.

**Pull Requests are welcome to add Aarch64 and x86-64 builds.**  

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

## Bug Reports and Feature Requests

As stated above Raspotify is just a package. The actual program that's run by the service is [librespot](https://github.com/librespot-org/librespot). Unless it's a packaging issue or a basic confguration question this is the wrong place to file your bug reports and/or feature requests.

**Only the most current version of Raspberry Pi OS lite is supported (_currently Bullseye_).** Raspotify may work on other OS's and/or other Raspberry Pi OS version but bugs to do with compatibility issues in unsupported systems will be closed. 

## Disclaimer

Per librespot's disclaimer, using librespot &mdash; the underlying library behind
raspotify &mdash; to connect to Spotify's API _"is probably forbidden by them."_
We've not received word about that, however use at your own risk.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar), [librespot org](https://github.com/librespot-org)
and its many contributors for [librespot](https://github.com/librespot-org/librespot),
which Raspotify packages. Without [librespot](https://github.com/librespot-org/librespot),
Raspotify would simply not exist.

### 📻 _"And Now, For Something Completely Different!"_ 🎙️

Raspotify's author [David Cooper](https://jew.pizza/) has abandoned being a software
engineer to pursue a career as a radio personality. If you find Raspotify useful, you
can support him by checking out his [radio work here](https://jew.pizza/) or
[give him a follow on Twitter](https://twitter.com/dtcooper).

On a related note, [@JasonLG1979](https://github.com/JasonLG1979) has become the
de-facto maintainer of the project. So an additional thank you to him as well.

If you'd like to buy Jason a Red Bull you can [❤️ Sponsor Him](https://github.com/sponsors/JasonLG1979).

## Final Note

_...and remember kids, have fun!_
