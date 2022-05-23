
[<img src="https://github.com/dtcooper/raspotify/blob/master/raspotify.svg?sanitize=true">](https://github.com/dtcooper/raspotify)

#

Raspotify is a
[Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_(file_format)) for Debian Stable and other Debian Stable based/compatible OS's 
which thinly wraps the awesome
[librespot](https://github.com/librespot-org/librespot) library by
[Paul Lietar](https://github.com/plietar) and others up as a [systemd](https://en.wikipedia.org/wiki/Systemd) [daemon](https://en.wikipedia.org/wiki/Daemon_(computing)).

Raspotify is primarily intended to be used in a *[headless enviroment](https://en.wikipedia.org/wiki/Headless_computer)*.

*For desktop OS's [spotifyd](https://spotifyd.github.io/spotifyd/installation/Raspberry-Pi.html) offers similar functionality and is probably a better choice.*

If you're looking for a turnkey audio solution for Raspberry Pi's with Spotify Connect support we recommend [moOde™ audio player](https://moodeaudio.org/).

## Dependencies

**Raspotify will not install without these packages and minimum versions:**
* [libc6 (>= 2.31)](https://tracker.debian.org/pkg/libc6)
* [systemd (>= 247.3)](https://tracker.debian.org/pkg/systemd)
* [libasound2 (>= 1.2.4)](https://tracker.debian.org/pkg/libasound2)
* [alsa-utils (>= 1.2.4)](https://tracker.debian.org/pkg/alsa-utils)
* [libpulse0 (>= 14.2)](https://tracker.debian.org/pkg/libpulse0)
* [init-system-helpers (>= 1.60)](https://tracker.debian.org/pkg/init-system-helpers)

## Installation

***The easy way***

```sh
sudo apt-get -y install curl && curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

***The hard way***

Essentially, here's what the easy installer does minus the compatibility checks:

```sh
# Install curl
sudo apt-get -y install curl

# Add the raspotify key to the keyring
curl -sSL https://dtcooper.github.io/raspotify/key.asc | sudo tee /usr/share/keyrings/raspotify_key.asc  > /dev/null
sudo chmod 644 /usr/share/keyrings/raspotify_key.asc

# Create the apt repo
echo 'deb [signed-by=/usr/share/keyrings/raspotify_key.asc] https://dtcooper.github.io/raspotify raspotify main' | sudo tee /etc/apt/sources.list.d/raspotify.list

# Install package
sudo apt-get update
sudo apt-get -y install raspotify
```

Or you can just download the latest .deb package and install it manually from here:
* [`raspotify-latest_armhf.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_armhf.deb)
* [`raspotify-latest_arm64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb)
* [`raspotify-latest_amd64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_amd64.deb)

### [Support for ARMv6 (Pi v1 and Pi Zero v1.x) has been dropped.](https://github.com/dtcooper/raspotify/commit/345f15c5d695736db8f90d1acc7e542803db5ca0)

[0.31.8.1](https://github.com/dtcooper/raspotify/releases/tag/0.31.8.1) was the last version to be built with ARMv6 support.

*You can install and run that version on an ARMv6 device, but you will never get updates and doing so is completely unsupported.*

```
curl https://github.com/dtcooper/raspotify/releases/download/0.31.8.1/raspotify_0.31.8.1.librespot.v0.3.1-54-gf4be9bb_armhf.deb
```
```
sudo apt install ./raspotify_0.31.8.1.librespot.v0.3.1-54-gf4be9bb_armhf.deb
```

***Don't forget to checkout the [wiki](https://github.com/dtcooper/raspotify/wiki) for tips, tricks and configuration info!!!***

## Bug Reports and Feature Requests

As stated above Raspotify is just a package. The actual program that's run by the service is [librespot](https://github.com/librespot-org/librespot). Unless it's a packaging issue or a basic confguration question this is the wrong place to file your bug reports and/or feature requests.

## Disclaimer

Per librespot's disclaimer, using librespot &mdash; the underlying library behind
raspotify &mdash; to connect to Spotify's API *"is probably forbidden by them."*
We've not received word about that, however use at your own risk.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar), [librespot org](https://github.com/librespot-org)
and its [many contributors](https://github.com/librespot-org/librespot/graphs/contributors) for [librespot](https://github.com/librespot-org/librespot),
which Raspotify packages. Without [librespot](https://github.com/librespot-org/librespot),
Raspotify would simply not exist.

### 📻 *"And Now, For Something Completely Different!"* 🎙️

Raspotify's author [David Cooper](https://jew.pizza/) has abandoned being a software
engineer to pursue a career as a radio personality. If you find Raspotify useful, you
can support him by checking out his [radio work here](https://jew.pizza/) or
[give him a follow on Twitter](https://twitter.com/dtcooper).

On a related note, [@JasonLG1979](https://github.com/JasonLG1979) has become the
de-facto maintainer of the project. So an additional thank you to him as well.

If you'd like to buy Jason a Red Bull you can [❤️ Sponsor Him](https://github.com/sponsors/JasonLG1979).

## Final Note

***...and remember kids, have fun!***
