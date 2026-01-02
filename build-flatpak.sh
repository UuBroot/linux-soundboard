#!/bin/bash

echo "This script requires sudo for certain commands. Please authenticate:"
sudo -v

flatpak install --user flathub org.kde.Sdk//6.9 -y

curl https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/refs/heads/master/pip/flatpak-pip-generator.py -o flatpak-pip-generator.py

python3 flatpak-pip-generator.py \
  --runtime="org.kde.Sdk//6.9" \
  --requirements-file=requirements-flatpak.txt \
  packaging \
  -o python-deps

flatpak-builder --user --force-clean --install --install-deps-from=flathub --disable-rofiles-fuse build-dir com.uubroot.Soundboard.yml

flatpak build-export repo build-dir

flatpak build-bundle repo soundboard.flatpak com.uubroot.Soundboard
#---

echo "Cleaning up ..."

echo "removing pip generator"
rm flatpak-pip-generator.py
rm python-deps.json
sudo rm -rf build-dir .flatpak-builder

