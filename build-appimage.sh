#!/bin/bash

# Exit on error, but allow linuxdeploy to continue on missing optional dependencies
set -e

# 1. Clean and Setup
rm -rf build-appimage squashfs-root
mkdir -p build-appimage

# 2. Install app via Meson
echo "--- Running Meson install ---"
meson setup build-appimage/meson-build --prefix=/usr
DESTDIR="$(realpath build-appimage/AppDir)" meson install -C build-appimage/meson-build

# 3. Download linuxdeploy
if [ ! -f linuxdeploy-x86_64.AppImage ]; then
    wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

export APPIMAGE_EXTRACT_AND_RUN=1
export NO_STRIP=1

# 4. Install Python packages to a custom location
echo "--- Installing Python packages ---"
mkdir -p build-appimage/AppDir/usr/lib/python-packages

pip install --target=build-appimage/AppDir/usr/lib/python-packages \
    pyside6 soundfile numpy pynput platformdirs

# 5. Copy Python source files
echo "--- Copying Python sources ---"
mkdir -p build-appimage/AppDir/usr/lib/soundboard
cp -r model service views main.py build-appimage/AppDir/usr/lib/soundboard/

# 6. Fix icon issue
echo "--- Setting up icon ---"
ICON_DIR="build-appimage/AppDir/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$ICON_DIR"
cp icon.png "$ICON_DIR/com.uubroot.Soundboard.png"
cp icon.png build-appimage/AppDir/com.uubroot.Soundboard.png

# Update desktop file
sed -i 's/Icon=.*/Icon=com.uubroot.Soundboard/g' \
    build-appimage/AppDir/usr/share/applications/com.uubroot.Soundboard.desktop

# 7. Remove optional SQL driver plugins that aren't needed
echo "--- Removing optional database plugins ---"
rm -f build-appimage/AppDir/usr/lib/python-packages/PySide6/Qt/plugins/sqldrivers/libqsqloci.so
rm -f build-appimage/AppDir/usr/lib/python-packages/PySide6/Qt/plugins/sqldrivers/libqsqlmysql.so
rm -f build-appimage/AppDir/usr/lib/python-packages/PySide6/Qt/plugins/sqldrivers/libqsqlpsql.so
rm -f build-appimage/AppDir/usr/lib/python-packages/PySide6/Qt/plugins/sqldrivers/libqsqlodbc.so
rm -f build-appimage/AppDir/usr/lib/python-packages/PySide6/Qt/plugins/sqldrivers/libqsqlmimer.so

# 8. Copy PySide6 Qt libraries (after removing unwanted plugins)
echo "--- Copying PySide6 Qt libraries ---"
PYSIDE6_DIR="build-appimage/AppDir/usr/lib/python-packages/PySide6"

mkdir -p build-appimage/AppDir/usr/lib
if [ -d "$PYSIDE6_DIR/Qt/lib" ]; then
    cp -r "$PYSIDE6_DIR/Qt/lib"/* build-appimage/AppDir/usr/lib/ 2>/dev/null || true
fi

mkdir -p build-appimage/AppDir/usr/plugins
if [ -d "$PYSIDE6_DIR/Qt/plugins" ]; then
    cp -r "$PYSIDE6_DIR/Qt/plugins"/* build-appimage/AppDir/usr/plugins/ 2>/dev/null || true
fi

# 9. Create custom AppRun script directly in AppDir (before linuxdeploy)
echo "--- Creating custom AppRun ---"
cat > build-appimage/AppDir/AppRun << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"

# Use system Python
PYTHON=$(which python3)

# Set up Python path to include our packages
export PYTHONPATH="$APPDIR/usr/lib/python-packages:$APPDIR/usr/lib/soundboard:$PYTHONPATH"

# Set up Qt environment
export QT_PLUGIN_PATH="$APPDIR/usr/plugins"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"

# Disable system Qt theme to avoid conflicts
export QT_QPA_PLATFORMTHEME=""
export QT_STYLE_OVERRIDE=""

# Run the application
exec "$PYTHON" "$APPDIR/usr/lib/soundboard/main.py" "$@"
EOF

chmod +x build-appimage/AppDir/AppRun

# 10. Run linuxdeploy (WITHOUT --custom-apprun since we created it manually)
echo "--- Starting AppImage Generation ---"

# Temporarily disable exit on error for linuxdeploy
set +e
./linuxdeploy-x86_64.AppImage --appdir build-appimage/AppDir \
    --output appimage \
    --desktop-file build-appimage/AppDir/usr/share/applications/com.uubroot.Soundboard.desktop \
    --icon-file "$ICON_DIR/com.uubroot.Soundboard.png" \
    --verbosity=1

LINUXDEPLOY_EXIT=$?
set -e

# Check if AppImage was created despite warnings
if [ -f "Soundboard-x86_64.AppImage" ]; then
    echo ""
    echo "============================================"
    echo "AppImage build complete successfully!"
    echo "Run with: ./Soundboard-x86_64.AppImage"
    echo "============================================"
    exit 0
else
    echo "AppImage build failed."
    exit $LINUXDEPLOY_EXIT
fi