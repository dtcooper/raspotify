# Changelog

All notable changes to this project will be documented in this file.

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
