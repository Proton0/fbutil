import argparse
from PIL import Image, ImageDraw, ImageFont
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


def text_to_framebuffer(
    text,
    framebuffer_path,
    width,
    height,
    stride=None,
    format="RGB565",
    font_path=None,
    font_size=8,
    text_x=0,
    text_y=0,
    force_alpha=False,
):
    if stride is None:
        stride = calculate_stride(width, format)
    print(f"Calculated stride: {stride}")

    # Create a blank image with the specified width and height
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load the font
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

    # Draw the text on the image at the specified position
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

    arr = np.array(img)

    if format == "RGB565":
        img = img.convert("RGB")
        arr = np.array(img)
        fb_arr = np.zeros((height, stride // 2), dtype=np.uint16)
        for y in range(height):
            for x in range(width):
                r = (arr[y, x, 0] >> 3) & 0x1F
                g = (arr[y, x, 1] >> 2) & 0x3F
                b = (arr[y, x, 2] >> 3) & 0x1F
                fb_arr[y, x] = (r << 11) | (g << 5) | b

        fb_arr = fb_arr.byteswap()  # Convert to little endian if necessary

    elif format == "ARGB8888":
        fb_arr = np.zeros((height, stride), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha
        fb_arr[:, 1::4] = arr[:, :, 0]  # Red
        fb_arr[:, 2::4] = arr[:, :, 1]  # Green
        fb_arr[:, 3::4] = arr[:, :, 2]  # Blue

    elif format == "ABGR8888":
        fb_arr = np.zeros((height, stride), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha
        fb_arr[:, 1::4] = arr[:, :, 2]  # Blue
        fb_arr[:, 2::4] = arr[:, :, 1]  # Green
        fb_arr[:, 3::4] = arr[:, :, 0]  # Red

    elif format == "BGRA8888":
        fb_arr = np.zeros((height, stride), dtype=np.uint8)
        fb_arr[:, 0::4] = arr[:, :, 2]  # Blue
        fb_arr[:, 1::4] = arr[:, :, 1]  # Green
        fb_arr[:, 2::4] = arr[:, :, 0]  # Red
        fb_arr[:, 3::4] = arr[:, :, 3] if not force_alpha else 255  # Alpha

    elif format == "RGBA8888":
        fb_arr = np.zeros((height, stride), dtype=np.uint8)
        fb_arr[:, 0:width * 4] = arr.reshape((height, width * 4))  # Flatten the array correctly

    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    # Save the framebuffer data to a file
    fb_arr.tofile(framebuffer_path)
    print("Framebuffer data saved to:", framebuffer_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to an Android framebuffer"
    )
    parser.add_argument("text", type=str, help="Text to render.")
    parser.add_argument(
        "framebuffer_path", type=str, help="Path to the output framebuffer binary file."
    )
    parser.add_argument("width", type=int, help="Width of the screen.")
    parser.add_argument("height", type=int, help="Height of the screen.")
    parser.add_argument(
        "--stride", type=int, help="Stride of the framebuffer (optional)."
    )
    parser.add_argument(
        "--format",
        type=str,
        default="RGB565",
        choices=["RGB565", "ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"],
        help="Framebuffer format (default: RGB565).",
    )
    parser.add_argument(
        "--font-path", type=str, help="Path to the font file (optional)."
    )
    parser.add_argument(
        "--font-size", type=int, default=8, help="Font size (default: 8)."
    )
    parser.add_argument(
        "--text-x", type=int, default=0, help="X position of the text (default: 0)."
    )
    parser.add_argument(
        "--text-y", type=int, default=0, help="Y position of the text (default: 0)."
    )
    parser.add_argument(
        "--force-alpha",
        action="store_true",
        help="Force the alpha value to be 255.",
    )
    args = parser.parse_args()
    print(f"Using format: {args.format}")
    print(f"Force alpha: {args.force_alpha}")

    text_to_framebuffer(
        args.text,
        args.framebuffer_path,
        args.width,
        args.height,
        args.stride,
        args.format,
        args.font_path,
        args.font_size,
        args.text_x,
        args.text_y,
        args.force_alpha,
    )


if __name__ == "__main__":
    main()
