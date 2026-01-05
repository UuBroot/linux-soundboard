#!/bin/bash

# Exit on error
set -e

APP_NAME="Soundboard"
APP_ID="com.uubroot.Soundboard"
BUILD_DIR="build-appimage"
APPDIR="$BUILD_DIR/AppDir"

# Clean previous builds
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR"

# 1. Install dependencies and the app using Meson into AppDir
# Note: Ensure libsndfile and portaudio are installed on your system
# as they are required dependencies for sound functionality.
meson setup "$BUILD_DIR/meson-build" --prefix=/usr
DESTDIR="$(realpath "$APPDIR")" meson install -C "$BUILD_DIR/meson-build"

# 2. Setup AppImage structure
# linuxdeploy will handle most of this, but we need to ensure icons and desktop files are in the right place
# Meson already installs them to /usr/share/...

# 3. Download linuxdeploy and plugins
export ARCH=$(uname -m)
if [ ! -f linuxdeploy-$ARCH.AppImage ]; then
    wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-$ARCH.AppImage
    chmod +x linuxdeploy-$ARCH.AppImage
fi

if [ ! -f linuxdeploy-plugin-python-$ARCH.AppImage ]; then
    wget https://github.com/linuxdeploy/linuxdeploy-plugin-python/releases/download/continuous/linuxdeploy-plugin-python-$ARCH.AppImage
    chmod +x linuxdeploy-plugin-python-$ARCH.AppImage
fi

# 4. Run linuxdeploy
# We need to tell linuxdeploy-plugin-python which requirements to install
# We also include the current directory in PYTHON_SOURCES to ensure all local modules are picked up
export PYTHON_SOURCES="main.py model service views"
export PIP_REQUIREMENTS="pyside6 soundfile numpy pynput platformdirs"
# Ensure we use the same version of python as the plugin expects or bundle it
export PYTHON_VERSION="3.11" 

# Use linuxdeploy to package everything
./linuxdeploy-$ARCH.AppImage --appdir "$APPDIR" \
    --plugin python \
    --output appimage \
    --desktop-file "$APPDIR/usr/share/applications/$APP_ID.desktop" \
    --icon-file "$APPDIR/usr/share/icons/hicolor/scalable/apps/$APP_ID.jpg" \
    --executable "$APPDIR/usr/bin/$APP_ID"

echo "AppImage build complete."
