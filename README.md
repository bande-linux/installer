# Bande Linux installer
Installs Bande Linux on Apple Silicon Macs. It prepares the disk, sets up the
boot chain (a stub macOS that carries the system firmware, and the unboot
bootloader as the custom boot object), then downloads an OS image and lays it on
disk. It must be run from macOS or recoveryOS.

This repository provides the installer, its bootstrap script, and the
`bande_firmware` Python module, which extracts device firmware from macOS for
the installed OS.

## Building
Run `./build.sh`, which produces an installer tree under `releases/`. By default
it builds unboot from the `unboot/` submodule with chainloading support. Set
`UNBOOT_STAGE1` to use a prebuilt unboot stage 1 binary, and `LOGO` to use a
different icns logo than `logo.icns`. The build fetches its dependencies from the
Internet and caches them under `dl/`; place the files there beforehand to build
offline.

## Bootstrapping
The installer is started by [scripts/bootstrap.sh](scripts/bootstrap.sh), which
downloads and unpacks the installer tree. The variables at its top configure it:

* `VERSION_FLAG`: a URI pointing to the `latest` file within the installer tree
* `INSTALLER_BASE`: a URL pointing to the installer tree
* `INSTALLER_DATA`: a URI pointing to the installer metadata file
* `INSTALLER_DATA_ALT`: optionally, an alternative location for the metadata
  file, for networks that block the primary one
* `REPO_BASE`: a URI pointing to the OS images root; OS packages given as
  relative paths in the metadata file are fetched from its `os/` folder

## First-boot setup
An OS entry in the metadata file with `"setup": true` makes the installer ask for
a username and password, a Wi-Fi network and an SSH public key. They are written
as plain files into `bande/setup/` on the OS's EFI system partition (`user`,
`password`, `wifi-ssid`, `wifi-psk`, `authorized_keys`), next to the installer
data, so the partition needs `"copy_installer_data": true`. The installed OS
applies them on its first boot and deletes them. Until then they are readable by
anyone who can mount that partition.

## License
The Bande Linux installer is distributed under the MIT license. See LICENSE for the
license text.

This installer vendors [python-asn1](https://github.com/andrivet/python-asn1), which
is distributed under the same license.
