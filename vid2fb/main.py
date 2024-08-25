import argparse
import os
from PIL import Image
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed


def calculate_stride(width, format):
    bytes_per_pixel = {
        "RGB565": 2,
        "ARGB8888": 4,
        "ABGR8888": 4,
        "BGRA8888": 4,
        "RGBA8888": 4,
    }
    return width * bytes_per_pixel[format]


def png_to_framebuffer(arr, width, height, stride, format, force_alpha):
    if format == "RGB565":
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
        fb_arr = arr.reshape((height, width * 4))  # Reshape to match the output format

    else:
        raise ValueError(f"Unsupported framebuffer format: {format}")

    return fb_arr


def process_frame(
    frame_index, frame, width, height, stride, format, force_alpha, output_folder
):
    # Convert frame to the desired format if necessary
    if format in ["RGB565", "ARGB8888", "ABGR8888", "BGRA8888", "RGBA8888"]:
        if format == "RGB565":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif format == "ARGB8888":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        elif format == "ABGR8888":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        elif format == "BGRA8888":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        elif format == "RGBA8888":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    img = Image.fromarray(frame)
    img = img.resize((width, height))  # Resize image to the specified dimensions
    arr = np.array(img)

    if stride is None:
        stride = calculate_stride(width, format)

    fb_arr = png_to_framebuffer(arr, width, height, stride, format, force_alpha)
    output_path = os.path.join(output_folder, f"{frame_index}.bin")
    fb_arr.tofile(output_path)
    print(f"Saved framebuffer for frame {frame_index} to {output_path}")


def video_to_framebuffer(
    video_path,
    output_folder,
    width,
    height,
    stride=None,
    format="RGB565",
    force_alpha=False,
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    frame_index = 0
    futures = []

    with ThreadPoolExecutor(max_workers=24) as executor:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            future = executor.submit(
                process_frame,
                frame_index,
                frame,
                width,
                height,
                stride,
                format,
                force_alpha,
                output_folder,
            )
            futures.append(future)
            frame_index += 1

        # Wait for all threads to complete
        for future in as_completed(futures):
            future.result()

    cap.release()


def main():
    parser = argparse.ArgumentParser(
        description="Convert each frame of a video to Android framebuffers"
    )
    parser.add_argument("video_path", type=str, help="Path to the input video file.")
    parser.add_argument(
        "output_folder", type=str, help="Folder to save the framebuffer files."
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
        "--force-alpha",
        action="store_true",
        help="Force the alpha value to be 255.",
    )
    args = parser.parse_args()

    video_to_framebuffer(
        args.video_path,
        args.output_folder,
        args.width,
        args.height,
        args.stride,
        args.format,
        args.force_alpha,
    )


if __name__ == "__main__":
    main()
