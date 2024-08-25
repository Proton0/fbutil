# fbutil

**DISCLAIMER: Proton0 is not liable for any damage to your device resulting from the use of this software.**

fbutil is a collection of Python scripts designed for manipulating the Android Framebuffer.

![Modified Framebuffer](https://github.com/proton0/fbutil/blob/main/preview.jpg?raw=true)
## Installation

To get started, clone the repository and install the dependencies:
```bash
  git clone https://github.com/proton0/fbutil
  cd fbutil
  pip3 install -r requirements.txt
```

## Uploading the framebuffer

> [!IMPORTANT]
> This script requires `adb` and root access to the device.

Push the `util` folder to your device
```bash
  adb push util /sdcard/util
```

Retrieve your framebuffer's details by running fbinfo:
```bash
  python3 fbinfo/main.py
````

> [!NOTE]
> If you encounter an error or the Framebuffer Location is empty, try running the `create_framebuffer.sh` script:
```bash
  adb shell su -c 'sh /sdcard/util/create_framebuffer.sh'
```

If the image is not visible, try running `enable_surface_update.sh` or simply execute `stop` in a shell.

Execute the following command on your device to apply the framebuffer:
```bash
  su
  cat <modified framebuffer location> > <framebuffer location from fbinfo>
```

> [!NOTE]
> If the image appears distorted (e.g., displaying as solid white), consider using the dd command, which may resolve the issue:

```bash
  su
  dd if=<modified framebuffer location> of=<framebuffer location from fbinfo>
```

## Author
 - [Proton0](https://github.com/proton0)