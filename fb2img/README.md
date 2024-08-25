# fb2img
Converts a framebuffer to an image.
# Usage

Use `fbinfo` to get the details of the framebuffer
If the output is glitched try to change formats or the stride but depending on your vendor it might still not work or be glitched
```bash
 python3 main.py <framebuffer> <output png> <width> <height> --format <format> --stride <stride>
```