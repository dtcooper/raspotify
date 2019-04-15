FROM debian:stretch

ENV INSIDE_DOCKER_CONTAINER 1

# Install git and compilers, let's toss gnupg and reprepro in there so we can
# use this container to make the apt repo as well
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        gnupg \
        pandoc \
        pkg-config \
        python-pip \
        python-setuptools \
        python-wheel \
        reprepro \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        jinja2-cli  \
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

# Install 1.0.x alsa-utils which is needed for compilation
ENV PKG_CONFIG_ALLOW_CROSS 1
ENV PKG_CONFIG_PATH "/toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot/lib/pkgconfig"
RUN curl -O https://www.mirrorservice.org/sites/ftp.alsa-project.org/pub/lib/alsa-lib-1.0.29.tar.bz2 \
    && tar xvjf alsa-lib-1.0.29.tar.bz2 && cd alsa-lib-1.0.29 \
    && CC=arm-linux-gnueabihf-gcc ./configure --host=arm-linux-gnueabihf --disable-python \
        --prefix=/toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot \
    && make -j $(nproc --all) && make install \
    && cd .. && rm -rf alsa-lib-1.0.29.tar.bz2 alsa-lib-1.0.29

RUN mkdir /build
