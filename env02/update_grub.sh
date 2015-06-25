#!/bin/bash

sed -i '/hiddenmenu/a title soft reinstall\n \troot (hd0,1)\n \tkernel /boot/bzImage.3212\n \tinitrd /boot/image_new.cpio.gz' grub.conf
