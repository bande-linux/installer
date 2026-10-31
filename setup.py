#!/usr/bin/env python

from distutils.core import setup

setup(name='bande_firmware',
      version='0.1',
      description='Bande Linux firmware tools',
      author='Bande Linux contributors',

      url='https://github.com/bande-linux/installer/',
      packages=['bande_firmware'],
      entry_points={"console_scripts": ["bande-fwextract = bande_firmware.update:main"]}
     )
