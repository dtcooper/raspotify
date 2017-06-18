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

# Install 1.0.x alsa-utils which is needed for compilation
RUN curl -O ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.29.tar.bz2 \
    && tar xvjf alsa-lib-1.0.29.tar.bz2 && cd alsa-lib-1.0.29 \
    && CC=arm-linux-gnueabihf-gcc ./configure --host=arm-linux-gnueabihf \
        --prefix=/toolchain/rpi-tools/arm-bcm2708/arm-bcm2708hardfp-linux-gnueabi/arm-bcm2708hardfp-linux-gnueabi/sysroot \
    && make -j $(nproc --all) && make install \
    && cd .. && rm -rf alsa-lib-1.0.29.tar.bz2 alsa-lib-1.0.29

# Set up Rust
ENV PATH="/root/.cargo/bin/:${PATH}"

RUN mkdir /.cargo \
    && echo '[target.arm-unknown-linux-gnueabihf]\nlinker = "gcc-wrapper"' \
        > /.cargo/config \
    && rustup target add arm-unknown-linux-gnueabihf

RUN mkdir /build
ENV CARGO_TARGET_DIR /build
ENV CARGO_HOME /build/cache

CMD /mnt/build.sh in_docker_container
