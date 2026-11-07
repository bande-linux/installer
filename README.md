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
downloads and unpacks the installer tree. The variables it exports configure it
(they point at `http://localhost:5000` for local testing):

* `VERSION_FLAG`: a URI pointing to the `latest` file within the installer tree
* `INSTALLER_BASE`: a URL pointing to the installer tree
* `INSTALLER_DATA`: a URI pointing to the installer metadata file
* `REPO_BASE`: a URI pointing to the OS images root; OS packages given as
  relative paths in the metadata file are fetched from its `os/` folder

## First start
The installer asks for no account, password or Wi-Fi network. The OS's first-run assistant asks for
them on the first start, and nothing secret is written to the EFI system partition. A partition
with `"recovery": true` receives the recovery image, and the installer writes its partition UUID
into `loader/entries/recovery.conf` on the EFI system partition, replacing `@RECOVERY_PARTUUID@`.
The EFI partition must come first in the metadata file.

## License
The Bande Linux installer is distributed under the MIT license. See LICENSE for the
license text.

This installer vendors [python-asn1](https://github.com/andrivet/python-asn1), which
is distributed under the same license.
