# Changelog

All notable changes to this project will be documented in this file.

## Next version

### Added
* Raspotify now provides experimental builds on the `riscv64` architecture,
  for use on Raspberry Pi clones such as the _VisionFive 2_. These builds
  require Debian Trixie or later.

### Fixed
* Configuration files with empty `LIBRESPOT_AUTOPLAY` values are repaired.
* The `avahi-daemon` package should have been a required dependency for 0.46.0,
  and has now been added.

## [0.46.0] - 2024-12-24

### Changed
Librespot bumped to 0.6.0, changelog from the maintainers follows:

This version takes another step into the direction of the HTTP API, fixes a
couple of bugs, and makes it easier for developers to mock a certain platform.
Also it adds the option to choose avahi, dnssd or libmdns as your zeroconf
backend for Spotify Connect discovery.

Changed

* [core] The access_token for http requests is now acquired by login5
* [core] MSRV is now 1.75 (breaking)
* [discovery] librespot can now be compiled with multiple MDNS/DNS-SD backends
  (avahi, dns_sd, libmdns) which can be selected using a CLI flag. The defaults
  are unchanged (breaking).

Added

* [core] Add get_token_with_client_id() to get a token for a specific client ID
* [core] Add login (mobile) and auth_token retrieval via login5
* [core] Add OS and os_version to config.rs
* [discovery] Added a new MDNS/DNS-SD backend which connects to Avahi via D-Bus.

## [0.45.0] - 2024-10-17

### Fixed
* Fix broken default configuration flag `LIBRESPOT_AUTOPLAY` (#674)
* Disable systemd's `DynamicUser` flag, to enable manual user-initiated OAuth setup (#675)

### Changed
This release contains the long anticipated 0.5.0 release of librespot.
Many thanks to the librespot dev team for their hard work.

## [0.44.1] - 2024-09-20

### Fixed
Default configuration file had some compatibility issues with new version of librespot,
and was updated to run nicely out of the box.

See #673.

## [0.44.0] - 2024-09-18

### Changed
Tracking upstream librespot instead of @JasonLG1979's fork.
Thanks @kimtore!

## [0.43.44] - 2023-05-03

### Fixed
Backport volume bug fix - See: [librespot-org#1159](https://github.com/librespot-org/librespot/pull/1159)

### Changed
Updated dependencies

## [0.43.45] - 2023-05-07

### Changed
Updated dependencies

Revert changes to write_buf - See: https://github.com/JasonLG1979/librespot/commit/c4550f3a473ef7e8bddaa413c6628873bbe1a70c

Improve "debug-ability" of ALSA backend - See: https://github.com/JasonLG1979/librespot/commit/626a51abc0429303d07c5f190c27c4362c240974

## [0.43.46] - 2023-05-12

### Changed
Updated dependencies

Modularize Normalisation a bit - See: https://github.com/JasonLG1979/librespot/commit/1416b09be86677022c3cf7b91260457fd57847d7

## [0.43.47] - 2023-06-17

### Changed
Updated dependencies

### Added
Resampling Support - See: https://github.com/JasonLG1979/librespot/commit/88f38aa7b3d194bb17011df7a0146dbf38460bc8

## [0.43.48] - 2023-06-17

### Fixed
https://github.com/JasonLG1979/librespot/commit/85a7d263ea66ef4231ce021d8431b905081d487c

## [0.43.49] - 2023-06-17

### Changed
Move audio processing out of player - See: https://github.com/JasonLG1979/librespot/commit/28fe6d1e53b47431232028dff098bee35abf1452

## [0.43.50] - 2023-06-18

### Changed
Update ALSA list_compatible_devices to show all combos of supported Formats & Sampling Rates. - See: https://github.com/JasonLG1979/librespot/commit/6b73f4ee38d035a2c94828400d12aff5f6f3d7fb
Make normalization more efficient. - See: https://github.com/JasonLG1979/librespot/commit/bffbbc7daa17241fca8b49809da812fb1d1c554a

## [0.43.51] - 2023-06-18

### Changed
Move the rest of the audio processing and playback out of player - See: https://github.com/JasonLG1979/librespot/commit/06b36d9e1e22c9c8fe03b4883af5bd01d1ac7d08

## [0.43.52] - 2023-06-20

### Added
Add debug logging and explicit error handling in ResampleWorker - See: https://github.com/JasonLG1979/librespot/commit/33747434366f0e2543fe1498dcea0075686bc233

## [0.43.53] - 2023-06-20

### Added
Add debug logging and explicit error handling in Player - See: https://github.com/JasonLG1979/librespot/commit/c1093860c99270324de2adc07e1c45836d0a00c4

## [0.43.54] - 2023-06-20

### Added
Deal with SamplePipeline latency - See: https://github.com/JasonLG1979/librespot/commit/9630b5f787d463e082926785912f51e2bc4e6e2a

## [0.43.55] - 2023-06-21

### Changed
Move time/pcm frame calculations out of player and into seperate PlayerTime helper struct

### Fixed
Fixed default normalisation calculation

For both - See: https://github.com/JasonLG1979/librespot/commit/1a3e870591b4287648427eb5418dcae52dd44c91

## [0.43.56] - 2023-06-21

### Changed
Load balance the Resampler Worker threads - See: https://github.com/JasonLG1979/librespot/commit/24f7f8ae3c05af2cff67894f7a79989881046815
