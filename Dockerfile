FROM rust:bullseye

ENV INSIDE_DOCKER_CONTAINER=1 \
    DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NOWARNINGS=yes \
    PKG_CONFIG_ALLOW_CROSS=1 \
    PKG_CONFIG_PATH="/usr/lib/arm-linux-gnueabihf/pkgconfig" \
    PATH="/root/.cargo/bin/:$PATH" \
    CARGO_INSTALL_ROOT="/root/.cargo" \
    CARGO_TARGET_DIR="/build" \
    CARGO_HOME="/build/cache"

RUN dpkg --add-architecture arm64 \
    && dpkg --add-architecture armhf \
    && apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libasound2-dev \
        libpulse-dev \
        crossbuild-essential-arm64 \
        libasound2-dev:arm64 \
        libpulse-dev:arm64 \
        crossbuild-essential-armhf \
        libasound2-dev:armhf \
        libpulse-dev:armhf \
        cmake \
        clang-16 \
        git \
        bc \
        liblzma-dev \
        pkg-config \
        gettext-base \
    && rm -rf /var/lib/apt/lists/* \
    ;

RUN mkdir /build /.cargo \
    && rustup target add aarch64-unknown-linux-gnu \
    && rustup target add armv7-unknown-linux-gnueabihf \
    && echo '[target.aarch64-unknown-linux-gnu]\nlinker = "aarch64-linux-gnu-gcc"' > /.cargo/config.toml \
    && echo '[target.armv7-unknown-linux-gnueabihf]\nlinker = "arm-linux-gnueabihf-gcc"' >> /.cargo/config.toml \
    && echo '[target.x86_64-unknown-linux-gnu]\nlinker = "gcc"' >> /.cargo/config.toml \
    && cargo install --jobs "$(nproc)" cargo-deb \
    && cargo install --force --locked --root /usr bindgen-cli \
    ;

RUN git config --global --add safe.directory /mnt/raspotify \
    && git config --global --add safe.directory /mnt/raspotify/librespot
