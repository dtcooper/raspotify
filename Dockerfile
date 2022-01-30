FROM debian:stable

ENV INSIDE_DOCKER_CONTAINER 1

RUN dpkg --add-architecture arm64

# Install git and compilers, let's toss gnupg and reprepro in there so we can
# use this container to make the apt repo as well
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libasound2-dev \
        crossbuild-essential-arm64 \
        libasound2-dev:arm64 \
        curl \
        git \
        gnupg \
        pandoc \
        pkg-config \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        reprepro \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install \
        jinja2-cli \
        unidecode

RUN mkdir /toolchain
WORKDIR /toolchain

# Check out Raspbian cross-compiler (this will work on *ALL* Raspberry Pi versions)
RUN git clone --depth 1 git://github.com/raspberrypi/tools.git rpi-tools \
    && rm -rf rpi-tools/.git
ENV PATH "/toolchain/rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/:${PATH}"

# Create wrapper around gcc to point to rpi sysroot
# Thanks @ https://github.com/herrernst/librespot/blob/build-rpi/.travis.yml
RUN echo '#!/bin/sh\narm-linux-gnueabihf-gcc --sysroot /toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot "$@"' \
        > rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/gcc-wrapper \
    && chmod +x rpi-tools/arm-bcm2708/gcc-linaro-arm-linux-gnueabihf-raspbian-x64/bin/gcc-wrapper \
    && ln -s ld-linux.so.3 rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot/lib/ld-linux-armhf.so.3

# Install alsa-utils which is needed for compilation
ENV PKG_CONFIG_ALLOW_CROSS 1
ENV PKG_CONFIG_PATH "/toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot/lib/pkgconfig"
RUN curl -O https://www.alsa-project.org/files/pub/lib/alsa-lib-1.2.6.tar.bz2 \
    && tar xvjf alsa-lib-1.2.6.tar.bz2 && cd alsa-lib-1.2.6 \
    && CC=arm-linux-gnueabihf-gcc ./configure --host=arm-linux-gnueabihf --disable-python \
        --prefix=/toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot \
    && make -j $(nproc --all) && make install \
    && cd .. && rm -rf alsa-lib-1.2.6.tar.bz2 alsa-lib-1.2.6

RUN mkdir /build

# Install most recent version of rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH "/root/.cargo/bin/:$PATH"
ENV CARGO_TARGET_DIR "/build"
ENV CARGO_HOME "/build/cache"
