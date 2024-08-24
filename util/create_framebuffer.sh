#!/bin/bash
echo "WARNING: This tool is not really supported and may cause issues with your system"
echo "This script will expose the framebuffer device in /dev/fb0 and requires root access"
echo "Press any key to continue or CTRL+C to cancel"
read -n 1 -s
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

echo "Checking if the framebuffer is already exposed"
if [ -e /dev/graphics/fb0 ]; then
  echo "Framebuffer (/dev/graphics/fb0) already exposed"
  exit
fi

if [ -e /dev/fb0 ]; then
  echo "Framebuffer (/dev/fb0) already exposed"
  exit
fi
echo "Checking if the device kernel is compiled with the framebuffer driver"

if grep -q "29 fb" /proc/devices; then
  echo "Framebuffer driver found"
else
  echo "Framebuffer driver not found. Your vendor is not exposing the framebuffer device and it cant be exposed without recompiling your kernel!"
  exit
fi

mknod /dev/fb0 c 29 0
echo "Framebuffer exposed at /dev/fb0 successfully. Note that this is not a permanent change and depending on your vendor may not even work"