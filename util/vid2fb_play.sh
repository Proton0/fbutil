#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Prompt for framebuffer device
echo "Enter the path to the framebuffer device (e.g., /dev/graphics/fb0):"
read framebuffer_device

# Prompt for folder containing framebuffer files
echo "Enter the path to the folder containing framebuffer files (e.g., /sdcard/fb_frames):"
read framebuffer_folder

# Check if the framebuffer device exists
if [ ! -e "$framebuffer_device" ]; then
    echo "Error: Framebuffer device $framebuffer_device does not exist."
    exit 1
fi

# Check if the framebuffer folder exists
if [ ! -d "$framebuffer_folder" ]; then
    echo "Error: Framebuffer folder $framebuffer_folder does not exist."
    exit 1
fi

# Iterate over framebuffer files and write them to the framebuffer device
index=0
while true; do
    framebuffer_file="$framebuffer_folder/$index.bin"

    # Check if the framebuffer file exists
    if [ ! -e "$framebuffer_file" ]; then
        echo "No more framebuffer files to process. Looping"
        index=0
    fi

    # Use dd to write the framebuffer file to the framebuffer device
    echo "Writing $framebuffer_file to $framebuffer_device..."
    dd if="$framebuffer_file" of="$framebuffer_device"

    # Increment index for the next file
    index=$((index + 1))
done

echo "Video played"
