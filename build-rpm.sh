#!/bin/bash

# Set version
VERSION="0.1.0"
NAME="linux-soundboard"
RPM_ROOT="${HOME}/rpmbuild"

# Create rpmbuild directories if they don't exist
mkdir -p ${RPM_ROOT}/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Archive the current project
echo "Creating source archive..."
tar --exclude='.git' --exclude='build' --exclude='*.rpm' -czf "${RPM_ROOT}/SOURCES/${NAME}-${VERSION}.tar.gz" . --transform "s|^\.|${NAME}-${VERSION}|"

# Copy spec file
cp "${NAME}.spec" "${RPM_ROOT}/SPECS/"

# Check for build dependencies
echo "Checking for build dependencies..."
MISSING_DEPS=""
for dep in meson python3-devel python3-pyside6 python3-soundfile python3-numpy python3-platformdirs; do
    if ! rpm -q $dep > /dev/null 2>&1 && ! rpm -q python3-$dep > /dev/null 2>&1; then
        # Check if the package might be named differently (e.g. meson is just meson)
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ -n "$MISSING_DEPS" ]; then
    echo "Error: Missing build dependencies:$MISSING_DEPS"
    echo "Please install them using:"
    echo "sudo dnf install$MISSING_DEPS"
    echo "Note: python3-pynput might need to be installed via pip if not available in your repos."
    exit 1
fi

# Build the RPM
echo "Building RPM..."
rpmbuild -ba "${RPM_ROOT}/SPECS/${NAME}.spec"

if [ $? -eq 0 ]; then
    echo "RPM built successfully."
    cp ${RPM_ROOT}/RPMS/noarch/${NAME}-${VERSION}-1*.rpm .
    echo "RPM copied to current directory: $(ls ${NAME}-${VERSION}-1*.rpm)"
else
    echo "RPM build failed."
    exit 1
fi
