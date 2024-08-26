# Utilities
Bash scripts for various task that will be ran in your device

## Scripts

### create_framebuffer.sh
> [!INFO]
> You do not need to do this when your framebuffer is already exposed. Run `fbinfo` to check if it is exposed


Attempts to expose the framebuffer device to `/dev/fb0`

Note that depending on your kernel and vendor, this script may not work. If it doesn't, you can try to manually expose the framebuffer device
Sometimes your kernel may not have the drivers required to expose the framebuffer device, in that case you will need to compile a custom kernel

### enable_surface_update.sh
This shell script will enable the `Show Surface Updates` option in developer options

Depending on your device's operating system, you may need to run this script due to SurfaceFlinger doing weird stuff the framebuffer and not allowing the custom framebuffer to show up on your device

### disable_surface_update.sh
This shell script will disable the `Show Surface Updates` option in developer options

### vid2fb_play.sh

This script will loop through a directory with your vid2fb output and `dd` it to your framebuffer