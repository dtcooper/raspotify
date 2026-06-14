# Raspotify on ARMv6 (Raspberry Pi 1 / Pi Zero v1.x)

ARMv6 support was dropped in February 2022 ([commit `345f15c`](https://github.com/dtcooper/raspotify/commit/345f15c)) for two stated reasons:

1. **Performance** — "the Pi 1 and Zero v1.x CPU … aren't powerful enough for volume normalization".
2. **librespot** — "librespot will soon be merging a rewrite that is incompatible with ARMv6 (it will not compile)".

This document records an investigation into whether that is still true, and wires up a working ARMv6 build.

## TL;DR

Modern librespot (0.8.0) **compiles and runs on a Pi Zero v1.x** (ARM1176JZF‑S, ARMv6 + VFPv2). Reason #2 turned out to be **stale** — it compiles fine. Getting a binary that actually *runs* on an ARM1176 required fixing two things that have nothing to do with librespot's source:

- **`ring` (the crypto crate behind rustls) ships hand‑written ARMv7/NEON assembly** that ignores `-march=armv6` and faults on an ARM1176. → Fixed by building librespot with the **`native-tls`** (OpenSSL) backend instead of `rustls-tls-native-roots`, which removes `ring` entirely.
- **Debian's `armhf` cross‑toolchain is ARMv7‑baseline.** Its `crt1.o` has a **Thumb‑2 `_start`**, so *even a hello‑world* Rust binary linked with it SIGILLs on an ARM1176 before `main` runs. → Fixed by cross‑compiling against a genuine **Raspberry Pi OS (Raspbian) ARMv6 sysroot** and linking with *its* v6 startfiles (`crt1.o`/`crti.o`/`crtn.o`/`libgcc.a`).

With both fixes, a stock **stable** Rust toolchain (no nightly, no `-Z build-std`) produces a binary tagged `Tag_CPU_arch: v6 / Thumb-1 / VFPv2` that runs cleanly.

Reason #1 (performance) is **not addressed here and remains the real open question** — it can only be judged on real hardware.

## How it was verified

The build was exercised under QEMU's strict `arm1176` CPU model (the exact Pi Zero v1.x core, VFPv2, no NEON, no Thumb‑2):

| Build | Tag | Runs on `arm1176` |
|---|---|---|
| rustls (`ring`) + Debian armhf toolchain | v7 / Thumb‑2 / VFPv3 | ❌ SIGILL (NEON/ARMv7 asm) |
| native-tls, Debian `crt1.o` | v7 / Thumb‑2 | ❌ SIGILL (Thumb‑2 `_start`) |
| **native-tls + Raspbian v6 sysroot + v6 `crt1.o`** | **v6 / Thumb‑1 / VFPv2** | ✅ `librespot --version` and full startup OK |

Controls confirmed QEMU's `arm1176` is faithful: native C `v6/VFPv2` code (including TLS + pthreads) runs fine on it, all three ARMv6 core models (`arm1136`, `arm1176`, `arm11mpcore`) reject the bad binaries identically, and every ARMv7 core (`cortex-a7/a8/a15`) runs them — exactly the signature of real ARMv7‑only instructions.

## Building

Requires Docker with QEMU/binfmt enabled for `linux/arm/v6` (Docker Desktop has this; on Linux run `docker run --privileged --rm tonistiigi/binfmt --install arm` once).

```sh
make armv6
```

This produces `raspotify_<version>_armv6.deb` in the repo root. Copy it to your Pi and install:

```sh
sudo dpkg -i raspotify_*_armv6.deb
sudo apt-get -f install   # pull in any missing runtime deps
```

### How the build differs from the other architectures

`Dockerfile.armv6` is a separate builder (like `Dockerfile.riscv64`) that:

1. Assembles a Raspberry Pi OS (Raspbian, ARMv6) sysroot with `libasound2-dev`, `libpulse-dev` and `libssl-dev` (multi‑stage `FROM --platform=linux/arm/v6`, installed under emulation).
2. Relativizes the sysroot's glibc linker‑script symlinks and drops the static `libc`/`libpthread`/… archives so cross‑linking resolves the shared, loader‑aware libraries.
3. Stages the Raspbian **v6** startfiles + `libgcc.a` into a clean `-B` directory so Debian's link driver doesn't substitute its ARMv7 `crt1.o`.

`build.sh`'s `build_armv6()` then builds the Rust target `arm-unknown-linux-gnueabihf` with `--features "alsa-backend pulseaudio-backend with-avahi native-tls"` and the sysroot link flags.

## Caveats

- **Performance is unverified.** The original 2022 concern (volume normalization on a single ~700 MHz ARM1176) stands. Test on real hardware before relying on it; consider disabling volume normalization.
- **Not served via the apt repo.** Raspberry Pi OS reports ARMv6 as `armhf` — the same architecture string as the ARMv7 build — so the two packages cannot coexist in one apt repository. The ARMv6 build is distributed as a standalone `.deb`; `install.sh` directs ARMv6 users accordingly.
- **mDNS:** the package uses Avahi (`with-avahi`); ensure `avahi-daemon` is running, or librespot also supports the pure‑Rust `with-libmdns` backend.
