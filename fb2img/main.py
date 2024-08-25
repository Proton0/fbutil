import argparse
from PIL import Image
import numpy as np

def framebuffer_to_png(framebuffer_path, png_path, width, height, format="RGB565", stride=None):
    # Determine the number of bytes per pixel based on the format
    if format in ["RGB565"]:
        bytes_per_pixel = 2
    elif format in ["ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"]:
        bytes_per_pixel = 4
    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    # Set stride to width * bytes_per_pixel if not provided
    if stride is None:
        print("No stride provided, output may be glitched.")
        stride = width * bytes_per_pixel

    # Read the framebuffer file
    with open(framebuffer_path, "rb") as f:
        fb_data = f.read()

    # Create a numpy array from the framebuffer data
    fb_arr = np.frombuffer(fb_data, dtype=np.uint8)

    # Initialize an empty array to hold the image data without padding
    img_arr = np.zeros((height, width, bytes_per_pixel), dtype=np.uint8)

    for y in range(height):
        start = y * stride
        end = start + (width * bytes_per_pixel)
        img_arr[y] = fb_arr[start:end].reshape((width, bytes_per_pixel))

    # Handle the different formats
    if format == "RGB565":
        r = (img_arr[:, :, 0] & 0xF8) << 8
        g = (img_arr[:, :, 0] & 0x07) << 5 | (img_arr[:, :, 1] & 0xE0) >> 3
        b = (img_arr[:, :, 1] & 0x1F) << 3
        img_arr = np.stack([r, g, b], axis=-1)
        img_arr = img_arr.astype(np.uint8)

    elif format == "ARGB8888":
        img_arr = img_arr[:, :, [1, 2, 3, 0]]  # Convert ARGB to RGBA

    elif format == "ABGR8888":
        img_arr = img_arr[:, :, [3, 2, 1, 0]]  # Convert ABGR to RGBA

    elif format == "BGRA8888":
        img_arr = img_arr[:, :, [2, 1, 0, 3]]  # Convert BGRA to RGBA

    elif format == "RGBA8888":
        img_arr = img_arr  # Already in RGBA format

    # Convert to Image and save as PNG
    img = Image.fromarray(img_arr, 'RGBA' if bytes_per_pixel == 4 else 'RGB')
    img.save(png_path)
    print(f"PNG image saved to: {png_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert an Android framebuffer to a PNG image")
    parser.add_argument("framebuffer_path", type=str, help="Path to the input framebuffer binary file.")
    parser.add_argument("png_path", type=str, help="Path to the output PNG image.")
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
        "--stride",
        type=int,
        default=None,
        help="Stride (number of bytes per row) (default: width * bytes per pixel).",
    )
    args = parser.parse_args()

    framebuffer_to_png(
        args.framebuffer_path,
        args.png_path,
        args.width,
        args.height,
        args.format,
        args.stride
    )

if __name__ == "__main__":
    main()
