#!/usr/bin/env python

from distutils.core import setup

setup(name='unbound_firmware',
      version='0.1',
      description='Unbound Linux firmware tools',
      author='Unbound Linux contributors',

      url='https://github.com/unbound-linux/installer/',
      packages=['unbound_firmware'],
      entry_points={"console_scripts": ["unbound-fwextract = unbound_firmware.update:main"]}
     )
