
[<img src="https://raw.githubusercontent.com/dtcooper/raspotify/master/raspotify.svg?sanitize=true">](https://github.com/dtcooper/raspotify)

Raspotify is a [Debian package and associated repository](https://en.wikipedia.org/wiki/Deb_(file_format)) for [Debian Stable](https://www.debian.org/releases/stable/) ( ***Currently Debian 11 "Bullseye"*** ) and other Debian Stable based/compatible OS's ( ***your mileage may vary*** ) which thinly wraps the awesome [librespot](https://github.com/librespot-org/librespot) library by [Paul Lietar](https://github.com/plietar) and others up as a [systemd](https://en.wikipedia.org/wiki/Systemd) [daemon](https://en.wikipedia.org/wiki/Daemon_(computing)).

Raspotify is intended to be used in a *[headless enviroment](https://en.wikipedia.org/wiki/Headless_computer)*. For desktop OS's [spotifyd](https://github.com/Spotifyd/spotifyd) offers similar functionality and is a better choice. If you're looking for a turnkey audio solution for Raspberry Pi's with Spotify Connect support we recommend [moOde™ audio player](https://moodeaudio.org/).

**Librespot, and therefore Raspotify, requires a premium account.**

## Installation

There are various *"guides"* floating around online. Most if not all of them are outdated and/or present incorrect information. **Don't follow them.**

```sh
sudo apt-get -y install curl && curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

Or you can just download the latest .deb package and install it manually from here:
* [`raspotify-latest_armhf.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_armhf.deb)
* [`raspotify-latest_arm64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_arm64.deb)
* [`raspotify-latest_amd64.deb`](https://dtcooper.github.io/raspotify/raspotify-latest_amd64.deb)

### [Raspotify does NOT support ARMv6 Pi's (Pi v1 and Pi Zero v1.x)](https://github.com/dtcooper/raspotify/wiki/Raspotify-on-Pi-v1's-and-Pi-Zero-v1.x)

## Configuration

The [wiki](https://github.com/dtcooper/raspotify/wiki) is full of useful information. The [Basic Setup Guide](https://github.com/dtcooper/raspotify/wiki/Basic-Setup-Guide) is a good place to start.

## Bug Reports, Questions and Feature Requests

**Please read the [Troubleshooting Guide](https://github.com/dtcooper/raspotify/wiki/Troubleshooting), the [Basic Setup Guide](https://github.com/dtcooper/raspotify/wiki/Basic-Setup-Guide), and search though [open](https://github.com/dtcooper/raspotify/issues?q=is%3Aopen+is%3Aissue) and [closed](https://github.com/dtcooper/raspotify/issues?q=is%3Aissue+is%3Aclosed) issues and [discussions](https://github.com/dtcooper/raspotify/discussions) before opening an issue or asking a question.**

## Disclaimer

Per librespot's disclaimer, using librespot &mdash; the underlying library behind raspotify &mdash; to connect to Spotify's API *"is probably forbidden by them."* We've not received word about that, however use at your own risk.

**Raspotify and librespot are intended for personal private use. Please DO NOT use Raspotify or librespot in any sort of commercial and/or public presentation. Doing so is a flagrant violation of Spotify's terms of service and could potentially lead to them blocking all Raspotify and librespot users.**

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar), [librespot org](https://github.com/librespot-org) and its [many contributors](https://github.com/librespot-org/librespot/graphs/contributors) for [librespot](https://github.com/librespot-org/librespot), which Raspotify packages (a slightly modded version of). Without [librespot](https://github.com/librespot-org/librespot), Raspotify would simply not exist.

### 📻 *"And Now, For Something Completely Different!"* 🎙️

Raspotify's author [David Cooper](https://jew.pizza/) has abandoned being a software engineer to pursue a career as a radio personality. If you find Raspotify useful, you can support him by checking out his [radio work here](https://jew.pizza/) or [give him a follow on Twitter](https://twitter.com/dtcooper).

On a related note, [Kim Tore Jensen](https://github.com/kimtore) has stepped up and is maintaing the project.

Special thanks to [@JasonLG1979](https://github.com/JasonLG1979), a former maintainer of the project.

## Final Note

***...and remember kids, have fun!***
