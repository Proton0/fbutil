import argparse
from PIL import Image
import numpy as np
# python3 main.py test.jpeg framebuffer.bin --format ARGB8888 736 460
#  python3 main.py test.jpeg framebuffer.bin --format BGRA8888 736 460

def png_to_framebuffer(
    png_path, framebuffer_path, width, height, format="RGB565", force_alpha=False
):
    # Load the image
    img = Image.open(png_path)
    img = img.resize((width, height))  # Resize image to the specified dimensions
    arr = np.array(img)

    if format == "RGB565":
        img = img.convert("RGB")
        arr = np.array(img)
        fb_arr = np.zeros((height, width), dtype=np.uint16)
        for y in range(height):
            for x in range(width):
                r = (arr[y, x, 0] >> 3) & 0x1F
                g = (arr[y, x, 1] >> 2) & 0x3F
                b = (arr[y, x, 2] >> 3) & 0x1F
                fb_arr[y, x] = (r << 11) | (g << 5) | b

        fb_arr = fb_arr.byteswap()  # Convert to little endian if necessary

    elif format == "ARGB8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((arr.shape[0], arr.shape[1] * 4), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha
        fb_arr[:, 1::4] = arr[:, :, 0]  # Red
        fb_arr[:, 2::4] = arr[:, :, 1]  # Green
        fb_arr[:, 3::4] = arr[:, :, 2]  # Blue

    elif format == "ABGR8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((height, width * 4), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha
        fb_arr[:, 1::4] = arr[:, :, 2]  # Blue
        fb_arr[:, 2::4] = arr[:, :, 1]  # Green
        fb_arr[:, 3::4] = arr[:, :, 0]  # Red

    elif format == "BGRA8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((height, width * 4), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 2]  # Blue
        fb_arr[:, 1::4] = arr[:, :, 1]  # Green
        fb_arr[:, 2::4] = arr[:, :, 0]  # Red
        fb_arr[:, 3::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha

    elif format == "RGBA8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((height, width * 4), dtype=np.uint8)
        fb_arr = arr.reshape((height, width * 4))  # Reshape to match the output format

    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    # Save the framebuffer data to a file
    fb_arr.tofile(framebuffer_path)
    print("Framebuffer data saved to:", framebuffer_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PNG image to an Android framebuffer"
    )
    parser.add_argument("png_path", type=str, help="Path to the input PNG image.")
    parser.add_argument(
        "framebuffer_path", type=str, help="Path to the output framebuffer binary file."
    )
    parser.add_argument("width", type=int, help="Width of the screen.")
    parser.add_argument("height", type=int, help="Height of the screen.")
    parser.add_argument(
        "--format",
        type=str,
        default="RGB565",
        choices=["RGB565", "ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"],
        help="Framebuffer format (default: RGB565).",
    )
    parser.add_argument(
        "--force-alpha",
        action="store_true",
        help="Force the alpha value to be 255.",
    )
    args = parser.parse_args()
    print(f"Using format: {args.format}")
    print(f"Force alpha: {args.force_alpha}")

    png_to_framebuffer(
        args.png_path,
        args.framebuffer_path,
        args.width,
        args.height,
        args.format,
        args.force_alpha,
    )


if __name__ == "__main__":
    main()
