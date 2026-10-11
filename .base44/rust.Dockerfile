# Development image for the Cinnabar Rust workspace under the Base44 sandbox.
#
# Plain toolchain base image plus the Linux system libraries the client's
# windowing stack needs at build time (see README: building the Wayland backend
# requires libwayland-dev). No repository source is copied in: the checkout is
# bind-mounted at run time and built by docker-compose.base44.yml, so edits are
# never baked into an image.
FROM rust:1.93.1

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libwayland-dev \
        libxkbcommon-dev \
        libxkbcommon-x11-dev \
        libx11-dev \
        libxcursor-dev \
        libxi-dev \
        libxrandr-dev \
        libxcb1-dev \
        libxcb-render0-dev \
        libxcb-shape0-dev \
        libxcb-xfixes0-dev \
        libudev-dev \
        libasound2-dev; \
    rm -rf /var/lib/apt/lists/*
