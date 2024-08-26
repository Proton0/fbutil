import subprocess
import re
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

adb_mode = True


def run_command(command, as_root=False):
    if adb_mode:
        if as_root:
            command = ["adb", "shell", "su", "-c", " ".join(command)]
        else:
            command = ["adb", "shell"] + command
    else:
        if as_root:
            command = ["su", "-c", " ".join(command)]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    logging.debug(f"Running command: {' '.join(command)}")
    logging.debug(f"Command output: {result.stdout}")
    logging.debug(f"Command error: {result.stderr}")
    return result


def get_framebuffer_id_and_driver():
    command = ["cat", "/proc/fb"]
    result = run_command(command, as_root=True)

    if result.returncode != 0:
        logging.error(f"Error accessing /proc/fb: {result.stderr}")
        return None, None

    framebuffer_info = result.stdout.strip()
    framebuffer_lines = framebuffer_info.split("\n")
    if not framebuffer_lines:
        logging.error("No framebuffer devices found")
        return None, None

    match = re.match(r"(\d+)\s+(\w+)", framebuffer_lines[0])
    if not match:
        logging.error("Unable to parse framebuffer information")
        return None, None

    framebuffer_id = match.group(1)
    framebuffer_driver = match.group(2)

    return framebuffer_id, framebuffer_driver


def getFBDevice(framebuffer_id=0):
    # [ -e /dev/graphics/fb{framebuffer_id} ] && echo 1 || echo 0
    command = run_command(
        [
            "[",
            "-e",
            f"/dev/graphics/fb{framebuffer_id}",
            "]",
            "&&",
            "echo 1",
            "||",
            "echo 0",
        ],
        True,
    )
    if command.stdout.strip() == "1":
        return f"/dev/graphics/fb{framebuffer_id}"
    else:
        command = run_command(
            [
                "[",
                "-e",
                f"/dev/fb{framebuffer_id}",
                "]",
                "&&",
                "echo 1",
                "||",
                "echo 0",
            ],
            True,
        )
        if command.stdout.strip() == "1":
            return f"/dev/fb{framebuffer_id}"
        else:
            return "Unknown"


def get_framebuffer_info(framebuffer_id):
    fb_dir = f"/sys/class/graphics/fb{framebuffer_id}/"

    info_files = ["bits_per_pixel", "virtual_size", "stride", "mode"]
    framebuffer_info = {}

    for info_file in info_files:
        file_path = f"{fb_dir}{info_file}"
        command = ["cat", file_path]
        result = run_command(command, as_root=True)

        if result.returncode != 0:
            logging.error(f"Error accessing {info_file}: {result.stderr} (stdout: {result.stdout})")
            continue

        framebuffer_info[info_file] = result.stdout.strip()

    framebuffer_info["fb_location"] = getFBDevice(framebuffer_id)

    return framebuffer_info


def parse_virtual_size(virtual_size_str):
    # Attempt to handle different formats
    virtual_size_str = virtual_size_str.replace(",", " ").strip()
    dimensions = virtual_size_str.split()

    if len(dimensions) == 2:
        try:
            width = int(dimensions[0])
            height = int(dimensions[1])
            return width, height
        except ValueError:
            logging.error("Error parsing virtual size dimensions")
            return 0, 0
    else:
        logging.error("Unexpected virtual size format")
        return 0, 0


def get_physical_size():
    command = ["wm", "size"]
    result = run_command(command)

    if result.returncode != 0:
        logging.error(f"Error accessing wm size: {result.stderr}")
        return None

    match = re.match(r"Physical size: (\d+)x(\d+)", result.stdout.strip())
    if not match:
        logging.error("Unable to parse wm size information")
        return None

    width = match.group(1)
    height = match.group(2)

    return width, height


def parse_and_display_info(framebuffer_info, physical_size):
    try:
        bits_per_pixel = int(framebuffer_info.get("bits_per_pixel", 0))
        virtual_size_str = framebuffer_info.get("virtual_size", "0 0")
        stride = int(framebuffer_info.get("stride", 0))
        mode = framebuffer_info.get("mode", "Unknown")
        fb_location = framebuffer_info.get("fb_location", "Unknown")

        width, height = parse_virtual_size(virtual_size_str)

        if bits_per_pixel == 32:
            pixel_format = "ARGB8888"
        elif bits_per_pixel == 24:
            pixel_format = "RGB888"
        elif bits_per_pixel == 16:
            pixel_format = "RGB565"
        elif bits_per_pixel == 15:
            pixel_format = "ARGB1555"  # 1-bit alpha
        elif bits_per_pixel == 12:
            pixel_format = "RGB444"  # 4 bits per channel
        elif bits_per_pixel == 8:
            pixel_format = "RGB332"  # 3 bits red, 3 bits green, 2 bits blue
        else:
            pixel_format = "Unknown"

        logging.info(f"Framebuffer Width: {width}")
        logging.info(f"Framebuffer Height: {height}")
        logging.info(f"Framebuffer Location: {fb_location}")
        logging.info(f"Bits per Pixel: {bits_per_pixel}")
        logging.info(f"Stride: {stride}")
        logging.info(f"Mode: {mode}")
        logging.info(f"Pixel Format: {pixel_format}")

        if physical_size:
            logging.info(f"Physical Size: {physical_size[0]}x{physical_size[1]}")

    except Exception as e:
        logging.error(f"Error parsing framebuffer information: {str(e)}")


def main():
    global adb_mode
    parser = argparse.ArgumentParser(
        description="Gets the device's framebuffer information"
    )
    parser.add_argument(
        "-l",
        "--local",
        type=bool,
        default=False,
        help="Use local device instead of adb",
    )
    args = parser.parse_args()
    if args.local:
        adb_mode = False
    framebuffer_id, framebuffer_driver = get_framebuffer_id_and_driver()
    if framebuffer_id is None:
        return

    logging.info(f"Framebuffer ID: {framebuffer_id}")
    logging.info(f"Framebuffer Driver: {framebuffer_driver}")

    framebuffer_info = get_framebuffer_info(framebuffer_id)
    if framebuffer_info:
        logging.debug(f"Framebuffer info: {framebuffer_info}")
        physical_size = get_physical_size()
        parse_and_display_info(framebuffer_info, physical_size)
    else:
        logging.error("Error getting framebuffer info")


if __name__ == "__main__":
    main()
