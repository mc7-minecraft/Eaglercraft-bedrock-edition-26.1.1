#!/bin/sh
# Base44 preview launcher for the Cinnabar client.
#
# The client is a native Bevy/wgpu window, so it is rendered onto a virtual X
# display inside the sandbox and that display is bridged to the browser with
# VNC over a WebSocket on port 3000. The client itself runs unmodified and with
# no arguments, which is the launcher/menu path.
set -eu

cd /work
export CARGO_TERM_COLOR=never

echo "base44: building the Go core beside the client binary"
go build -o target/debug/bedrock-core ./core/cmd/bedrock-core

echo "base44: building the client (the first run compiles the Rust workspace)"
cargo build --locked -p bedrock-client

echo "base44: starting the virtual display :99"
Xvfb :99 -screen 0 1280x720x24 -nolisten tcp -ac >/tmp/xvfb.log 2>&1 &
attempt=0
while [ "$attempt" -lt 150 ]; do
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 0.2
done
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "base44: Xvfb failed to start:"
    cat /tmp/xvfb.log
    exit 1
fi

echo "base44: starting the VNC server and the browser bridge on port 3000"
web_root=/tmp/cinnabar-novnc
rm -rf "$web_root"
mkdir -p "$web_root"
cp -r /usr/share/novnc/. "$web_root/"
cp -f .base44/novnc/index.html "$web_root/index.html"
x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -quiet -noxdamage -repeat \
    -o /tmp/x11vnc.log &
websockify --web="$web_root" 0.0.0.0:3000 127.0.0.1:5900 >/tmp/websockify.log 2>&1 &

echo "base44: launching bedrock-client (no arguments => the launcher menu)"
exec ./target/debug/bedrock-client
