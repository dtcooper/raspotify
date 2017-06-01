FROM debian:stretch

# Install git and compilers
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

RUN mkdir /toolchain
WORKDIR /toolchain

# Check out Raspbian cross-compiler (this will work on *ALL* Raspberry Pi versions)
RUN git clone --depth 1 https://github.com/raspberrypi/tools.git rpi-tools \
    && rm -rf rpi-tools/.git
ENV PATH="/toolchain/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/:${PATH}"

# Create wrapper around gcc to point to rpi sysroot
# Thanks @ https://github.com/herrernst/librespot/blob/build-rpi/.travis.yml
RUN echo '#!/bin/sh\narm-linux-gnueabihf-gcc --sysroot /toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot "$@"' \
        > rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/gcc-wrapper \
    && chmod +x rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/gcc-wrapper \
    && ln -s ld-linux.so.3 rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot/lib/ld-linux-armhf.so.3

# Download and exact libasound2 from Raspbian
RUN curl -OL http://mirrordirector.raspbian.org/raspbian/pool/main/a/alsa-lib/libasound2_1.0.25-4_armhf.deb \
    && curl -OL http://mirrordirector.raspbian.org/raspbian/pool/main/a/alsa-lib/libasound2-dev_1.0.25-4_armhf.deb \
    && ar p libasound2_1.0.25-4_armhf.deb data.tar.gz \
        | tar -xvz -C rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot \
    && ar p libasound2-dev_1.0.25-4_armhf.deb data.tar.gz \
        | tar -xz -C rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot \
    && rm *.deb

# Set up Rust
ENV PATH="/root/.cargo/bin/:${PATH}"

RUN mkdir /.cargo \
    && echo '[target.arm-unknown-linux-gnueabihf]\nlinker = "gcc-wrapper"' \
        > /.cargo/config \
    && rustup target add arm-unknown-linux-gnueabihf

RUN mkdir /build
ENV CARGO_TARGET_DIR /build
ENV CARGO_HOME /build/cache

ADD librespot /librespot
CMD /mnt/build_raspotify.sh in_docker_container
