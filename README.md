# Raspotify

> :warning: **NOTE:** *I have **limited to no time** to work on this package
> these days!*
> 
> I am looking for a maintainer to help with issues and updating the package.
> Please reach out via email at <david@jew.pizza> if you have interest in helping.
>
> Cheers,
>
> David

_**Spotify Connect client for the Raspberry Pi that Just Works™.**_

## tl;dr

Install the Spotify Connect client on your Raspberry Pi,

```bash
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
page to download the most recent version and install the Debian package. Or follow
the [directions below](#easy-installation).

### Requirements

Raspotify works on a Raspberry Pi running [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).
You'll need a [Spotify Premium](https://www.spotify.com/premium/) account in order
to use Connect.

Raspotify should work on _any_ Pi but it has been tested on,

* Raspberry Pi (v1) model B
* Raspberry Pi 2 model B
* Raspberry Pi 3 model B and B+
* Raspberry Pi 4
* Orange Pi Zero LTS with Expansion board (for the 3.5mm jack)

### Easy Installation

This command downloads and installs the Debian package and adds its apt repository,
which ensures you'll always be up to date with upstream changes.

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

That's it! Plug a speaker into your Pi on your local network, select the device
in Spotify et voilà!

### Hard installation

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

```bash
wget https://dtcooper.github.io/raspotify/raspotify-latest.deb
sudo dpkg -i raspotify-latest.deb
```

### Play via Bluetooth Speaker on Raspberry Pi Desktop

When running Raspotify with Raspberry Pi Desktop, Raspotify needs to be 
installed as a user service, rather than a system service.  This causes
Raspotify to be in the same process as the PulseAudio service, where the 
PulseAudio service is what is providing sound to your output device.

To configure Raspotify as a user service for your pi user, open a terminal and:
1. `mkdir -p ~/.config/systemd/user`
2. `cd ~/.config/systemd/user`
3. create a file named `raspotify.service` containing:

```
[Unit]
Description=Raspotify
Wants=pulseaudio.service

[Service]
Restart=always
RestartSec=10
Environment="DEVICE_NAME=raspotify (%H)"
Environment="BITRATE=160"
Environment="CACHE_ARGS=--disable-audio-cache"
Environment="VOLUME_ARGS=--enable-volume-normalisation --volume-ctrl linear --initial-volume 100"
Environment="BACKEND_ARGS=--backend alsa"
Environment="DEVICE_TYPE=speaker"
EnvironmentFile=-/etc/default/raspotify
ExecStart=/usr/bin/librespot --name ${DEVICE_NAME} --device-type ${DEVICE_TYPE} $BACKEND_ARGS --bitrate ${BITRATE} $CACHE_ARGS $VOLUME_ARGS $OPTIONS

[Install]
WantedBy=default.target
```

The main difference betweeen this file and the file Raspotify lands in 
`/usr/lib/systemd/system/raspotify.service` is that the following lines are removed:
```
After=network.target

User=raspotify
Group=raspotify
PermissionsStartOnly=true
ExecStartPre=/bin/mkdir -m 0755 -p /var/cache/raspotify ; /bin/chown raspotify:raspotify /var/cache/raspotify

WantedBy=multi-user.target
```

And the following lines have been added:
```
Wants=pulseaudio.service

WantedBy=default.target
```

Once this file is created, run 
`sudo systemctl disable --now raspotify.service` to disable the system service and
`systemctl --user enable --now raspotify.service` to register and start the user service.

At this point, Raspotify should play via whatever audio device is configured 
using the PulseAudio Volume Control on Raspberry Pi Desktop Panel. 

### Play via Bluetooth Speaker without Raspberry Pi Desktop

#### via asound.conf

1. Edit `/etc/asound.conf`:
`> vim /etc/asound.conf

2. Add your bluetooth MAC adresss instead of `XX:XX:XX:XX:XX`:

```
defaults.bluealsa.interface "hci0"
defaults.bluealsa.device "XX:XX:XX:XX:XX"
defaults.bluealsa.profile "a2dp"

pcm.btheadset {
    type plug
    slave {
        pcm {
              type bluealsa
              device XX:XX:XX:XX:XX:XX
              profile "auto"
         }   
    }   
    hint {
         show on
         description "BT Headset"
    }   
}
ctl.btheadset {
    type bluetooth
}
```

3. Restart service:

`> sudo service raspotify restart`

####  via pi-btaudio

Another way to resolve any issues to install `pi-btaudio` alongside with `raspotify`: https://github.com/bablokb/pi-btaudio
(remove pulseaudio if you have it).


### Uninstalling

To uninstall, remove the package,

```bash
sudo apt-get remove -y raspotify
```

To completely remove Raspotify and its Debian repository from your system try,
```bash
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
#VOLUME_ARGS="--enable-volume-normalisation --volume-ctrl linear --initial-volume=100"

# Backend could be set to pipe here, but it's for very advanced use cases of
# librespot, so you shouldn't need to change this under normal circumstances.
#BACKEND_ARGS="--backend alsa"

# The displayed device type in Spotify clients.
# Can be "unknown", "computer", "tablet", "smartphone", "speaker", "tv",
# "avr" (Audio/Video Receiver), "stb" (Set-Top Box), and "audiodongle".
#DEVICE_TYPE="speaker"
```

After editing restart the daemon by running: `sudo systemctl restart raspotify`

## Building the Package Yourself

All that's required is [Docker](https://www.docker.com/) on a \*nix system with
[git](https://git-scm.com/) and [Make](https://www.gnu.org/software/make/). It
can be built on any amd64 platform that runs docker using Raspberry Pi's
cross-compiler (tested on Ubuntu 16.04 LTS and macOS El Capitan).

```bash
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
If you still don't get satisfactory results, try adding `--normalisation-pregain 2`
to VOLUME_ARGS in the configuration file to increase the initial volume.

> *My Raspberry Pi does not use my USB sound card!*

Try to replace the following in the file `/usr/share/alsa/alsa.conf`:

```
defaults.ctl.card 0
defaults.pcm.card 0
```
with
```
defaults.ctl.card 1
defaults.pcm.card 1
```
> *The audio output buzzes a few seconds after audio stops!*

This is likely to be ALSA's Dynamic Audio Power Management (DAPM) shutting down
the sound module of your device to save power. If you want to disable this feature,
create a file called `snd_soc_core.conf` in `/etc/modprobe.d` with this line in:
```
options snd_soc_core pmdown_time -1
```
Once you reboot and play some sound, the issue should be gone.

> *Other issues*

File an issue and if we get it sorted, I'll add to this list.

## Donations

If you're so inclined, Bitcoin my address is `1PoDcAStyJoB7zZz2mny4KjtjiEu8S44ns`. :)

(I'd rather you donate to [librespot](https://github.com/librespot-org/librespot)
instead, but there's no public address for those folks.)

## Final Note

_...and remember kids, have fun!_

## Disclaimer

Per librespot's disclaimer, using librespot &mdash; the underlying library behind
raspotify &mdash; to connect to Spotify's API _"is probably forbidden by them."_
We've not received word about that, however use at your own risk.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE)
file for details.

## Acknowledgments

Special thanks to [Paul Lietar](https://github.com/plietar) for
[librespot](https://github.com/librespot-org/librespot) (and its additional authors),
which Raspotify packages. Without [librespot](https://github.com/librespot-org/librespot),
Raspotify would simply not exist.
