# Base44 development image for Cinnabar.
#
# Only system-level tooling is baked in. The repository is bind-mounted at /work
# and every build/run step happens at container startup, so the live working tree
# is always what runs; nothing here copies application source.
FROM rust:1.93

# The Go core and the Go registry/analysis tools share this image.
COPY --from=golang:1.26 /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"

RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      ca-certificates curl unzip git pkg-config \
      libwayland-dev libxkbcommon-dev libxkbcommon-x11-0 \
      libx11-6 libx11-xcb1 libxcb1 libxcb-render0 libxcb-shape0 libxcb-xfixes0 \
      libxi6 libxcursor1 libxrandr2 libxext6 \
      xvfb x11vnc x11-utils procps imagemagick \
      novnc websockify \
      mesa-vulkan-drivers libvulkan1 vulkan-tools libgl1-mesa-dri libegl1 \
 && rm -rf /var/lib/apt/lists/*
