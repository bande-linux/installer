#!/bin/sh
set -e

cd "$(dirname "$0")"
base="$PWD"

if [ -e $HOME/.cargo/env ] ; then
    source $HOME/.cargo/env
fi

: "${INSTALLER_BASE:?}"
: "${REPO_BASE:?}"

make -C "unboot" RELEASE=1 CHAINLOADING=1 -j4

sudo rm -rf /tmp/bande-install
mkdir -p /tmp/bande-install

git describe --tags --always --dirty > /tmp/bande-install/version.tag

cd /tmp/bande-install
ln -sf "$base/src"/* .
ln -sf "$base/bande_firmware" .
mkdir -p boot
ln -sf "$base/unboot/build/unboot.bin" boot/unboot.bin
ln -sf "$base/logo.icns" logo.icns
ln -sf "$base/data/installer_data.json" installer_data.json

sudo -E python3 main.py
