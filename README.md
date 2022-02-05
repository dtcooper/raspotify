# Raspotify

_**A [Spotify Connect](https://www.spotify.com/connect/) client that mostly Just Works™**_ *(Now featuring arm64 & amd64 builds!!!)*

Raspotify is a
[Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_\(file_format\)) for Debian Stable (and other Debian Stable based/compatible OS's) 
which thinly wraps the awesome
[librespot](https://github.com/librespot-org/librespot) library by
[Paul Lietar](https://github.com/plietar) and others up as a [systemd](https://en.wikipedia.org/wiki/Systemd) [daemon](https://en.wikipedia.org/wiki/Daemon_(computing)).

Raspotify is primarily intended to be used in a _[headless enviroment](https://en.wikipedia.org/wiki/Headless_computer)_.

_For desktop OS's (and/or systems with PulseAudio installed) [spotifyd](https://spotifyd.github.io/spotifyd/installation/Raspberry-Pi.html) offers similar functionality, much better PulseAudio compatibility and is a better choice._

If you're looking for a turnkey audio solution for Raspberry Pi's with Spotify Connect support we recommend [moOde™ audio player](https://moodeaudio.org/).

[Support for ARMv6 (Pi v1 and Pi Zero v1.x) has been dropped.](https://github.com/dtcooper/raspotify/commit/345f15c5d695736db8f90d1acc7e542803db5ca0)

## Dependencies

* [libasound2 (>= 1.2.4)](https://tracker.debian.org/pkg/libasound2)
* [systemd (>= 247.3)](https://tracker.debian.org/pkg/systemd)
* [init-system-helpers (>= 1.60)](https://tracker.debian.org/pkg/init-system-helpers)

## Installation

_**The easy way**_

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

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

Or you can just download the latest .deb package and install it manually from here:
* [`raspotify-latest_armhf.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_armhf.deb) *_ARMv7_ (Not compatabile with ARMv6 devices)
* [`raspotify-latest_arm64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb)
* [`raspotify-latest_amd64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_amd64.deb)

_**Don't forget to checkout the [wiki](https://github.com/dtcooper/raspotify/wiki) for tips, tricks and configuration info!!!**_

## Bug Reports and Feature Requests

As stated above Raspotify is just a package. The actual program that's run by the service is [librespot](https://github.com/librespot-org/librespot). Unless it's a packaging issue or a basic confguration question this is the wrong place to file your bug reports and/or feature requests.

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
