
# img2fb

`img2fb` is a simple tool to convert images to Android's framebuffer format


## Run Locally

Clone the project

```bash
  git clone https://github.com/proton0/fbutil
```

Go to the project directory

```bash
  cd fbutil
```

Install dependencies

```bash
  pip3 install -r requirements.txt
```

Push `utils` to your Android Device

```bash
  adb push utils /sdcard/utils
```

Get the location of your framebuffer
```bash
  adb shell sh /sdcard/utils/framebuffer_locator.sh
```

Run the script
> [!IMPORTANT]  
> Run `fbinfo/main.py` for the required details
```bash
  cd img2fb
  python3 main.py <image> <output framebuffer> --format <optional format>
```

Push the framebuffer to your Device
```bash
  adb push framebuffer.bin /sdcard/framebuffer.bin
```

> [!NOTE]  
> If you dont see the image then try to run `enable_surface_update.sh` or `stop` using a shell and try to put it on a `while true` loop
Run this script on your device
```bash
  cat /sdcard/framebuffer > <Framebuffer Location>
```