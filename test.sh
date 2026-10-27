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

sudo rm -rf /tmp/unbound-install
mkdir -p /tmp/unbound-install

git describe --tags --always --dirty > /tmp/unbound-install/version.tag

cd /tmp/unbound-install
ln -sf "$base/src"/* .
ln -sf "$base/unbound_firmware" .
mkdir -p boot
ln -sf "$base/unboot/build/unboot.bin" boot/unboot.bin
ln -sf "$base/logo.icns" logo.icns
ln -sf "$base/data/installer_data.json" installer_data.json

sudo -E python3 main.py
