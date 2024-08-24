import argparse
from PIL import Image
import numpy as np


def png_to_framebuffer(png_path, framebuffer_path, format="RGB565"):
    # Load the image
    img = Image.open(png_path)

    if format == "RGB565":
        img = img.convert("RGB")
        arr = np.array(img)
        fb_arr = np.zeros((arr.shape[0], arr.shape[1]), dtype=np.uint16)
        for y in range(arr.shape[0]):
            for x in range(arr.shape[1]):
                r = arr[y, x, 0] >> 3
                g = arr[y, x, 1] >> 2
                b = arr[y, x, 2] >> 3
                fb_arr[y, x] = (r << 11) | (g << 5) | b

    elif format == "ARGB8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        fb_arr[:, :, 0] = arr[:, :, 3]  # Alpha
        fb_arr[:, :, 1] = arr[:, :, 0]  # Red
        fb_arr[:, :, 2] = arr[:, :, 1]  # Green
        fb_arr[:, :, 3] = arr[:, :, 2]  # Blue

    elif format == "ABGR8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        fb_arr[:, :, 0] = arr[:, :, 3]  # Alpha
        fb_arr[:, :, 1] = arr[:, :, 2]  # Blue
        fb_arr[:, :, 2] = arr[:, :, 1]  # Green
        fb_arr[:, :, 3] = arr[:, :, 0]  # Red

    elif format == "BGRA8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        fb_arr[:, :, 0] = arr[:, :, 2]  # Blue
        fb_arr[:, :, 1] = arr[:, :, 1]  # Green
        fb_arr[:, :, 2] = arr[:, :, 0]  # Red
        fb_arr[:, :, 3] = arr[:, :, 3]  # Alpha

    elif format == "RGBA8888":
        img = img.convert("RGBA")
        arr = np.array(img)
        fb_arr = arr

    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    # Save the framebuffer data to a file
    fb_arr.tofile(framebuffer_path)
    print("Framebuffer data saved to:", framebuffer_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PNG image to a framebuffer format."
    )
    parser.add_argument("png_path", type=str, help="Path to the input PNG image.")
    parser.add_argument(
        "framebuffer_path", type=str, help="Path to the output framebuffer binary file."
    )
    parser.add_argument(
        "--format",
        type=str,
        default="RGB565",
        choices=["RGB565", "ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"],
        help="Framebuffer format (default: RGB565).",
    )

    args = parser.parse_args()

    png_to_framebuffer(args.png_path, args.framebuffer_path, args.format)


if __name__ == "__main__":
    main()
