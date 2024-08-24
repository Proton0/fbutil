
# fbutil

A bunch of python scripts used to manipulate the Android Framebuffer

## Run Locally

> [!IMPORTANT]  
> Make sure to install ADB and to install Magisk (or any other root providers)

Clone the project

```bash
  git clone https://github.com/proton0/fbutil
```

In order to "push" the modified framebuffer to the device, you need to have ADB installed and the device must be connected to the computer.

> [!IMPORTANT]  
> If you cant see the image, try to run `enable_surface_update.sh` or simply `stop` on a shell (this is due to SurfaceFlinger and Zygote doing weird stuff with the framebuffer)

Run this script on your device
```bash
  cat /sdcard/framebuffer > <Framebuffer Location>
```

> [!IMPORTANT]  
> If the image seems VERY VERY distorted (like its just white) then try to use `dd` (this fixed my issues for me)
```bash
  dd if=/sdcard/framebuffer of=<Framebuffer Location>
```

## Authors

- [@proton0](https://www.github.com/proton0)

