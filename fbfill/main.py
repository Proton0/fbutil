import argparse
import struct
import numpy as np

def calculate_stride(width, format):
    bytes_per_pixel = {
        "RGB565": 2,
        "ARGB8888": 4,
        "ABGR8888": 4,
        "BGRA8888": 4,
        "RGBA8888": 4,
    }
    return width * bytes_per_pixel[format]

def fill_framebuffer(hex_color, width, height, stride, framebuffer, format):
    # Convert hex color to RGB
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    r, g, b = struct.unpack("BBB", bytes.fromhex(hex_color))

    # Handle different framebuffer formats
    if format == "RGB565":
        fb_arr = np.zeros((height, stride // 2), dtype=np.uint16)
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        fb_arr[:, :width] = rgb565
        fb_data = fb_arr.tobytes()

    elif format == "ARGB8888":
        fb_arr = np.zeros((height, stride // 4, 4), dtype=np.uint8)
        fb_arr[:, :width, 0] = 255  # Alpha
        fb_arr[:, :width, 1] = r  # Red
        fb_arr[:, :width, 2] = g  # Green
        fb_arr[:, :width, 3] = b  # Blue
        fb_data = fb_arr.tobytes()

    elif format == "ABGR8888":
        fb_arr = np.zeros((height, stride // 4, 4), dtype=np.uint8)
        fb_arr[:, :width, 0] = 255  # Alpha
        fb_arr[:, :width, 1] = b  # Blue
        fb_arr[:, :width, 2] = g  # Green
        fb_arr[:, :width, 3] = r  # Red
        fb_data = fb_arr.tobytes()

    elif format == "BGRA8888":
        fb_arr = np.zeros((height, stride // 4, 4), dtype=np.uint8)
        fb_arr[:, :width, 0] = b  # Blue
        fb_arr[:, :width, 1] = g  # Green
        fb_arr[:, :width, 2] = r  # Red
        fb_arr[:, :width, 3] = 255  # Alpha
        fb_data = fb_arr.tobytes()

    elif format == "RGBA8888":
        fb_arr = np.zeros((height, stride // 4, 4), dtype=np.uint8)
        fb_arr[:, :width, 0] = r  # Red
        fb_arr[:, :width, 1] = g  # Green
        fb_arr[:, :width, 2] = b  # Blue
        fb_arr[:, :width, 3] = 255  # Alpha
        fb_data = fb_arr.tobytes()

    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    # Write the buffer to the framebuffer
    with open(framebuffer, "wb") as fb:
        fb.write(fb_data)

    print(
        f"Created framebuffer {framebuffer} with hex color {hex_color} (width: {width}, height: {height}, stride: {stride}) in format {format}"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Creates an Android Framebuffer with a solid color"
    )
    parser.add_argument(
        "--color", type=str, required=True, help="Hex color code (e.g., #FF5733)"
    )
    parser.add_argument(
        "--width", type=int, required=True, help="Screen width in pixels"
    )
    parser.add_argument(
        "--height", type=int, required=True, help="Screen height in pixels"
    )
    parser.add_argument(
        "--stride", type=int, help="Framebuffer stride in bytes (calculated if not provided)"
    )
    parser.add_argument(
        "--framebuffer",
        required=True,
        help="Output Framebuffer",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=["RGB565", "ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"],
        help="Framebuffer format",
    )

    args = parser.parse_args()

    if args.stride is None:
        args.stride = calculate_stride(args.width, args.format)

    fill_framebuffer(args.color, args.width, args.height, args.stride, args.framebuffer, args.format)

if __name__ == "__main__":
    main()
