import subprocess
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def run_command(command, as_root=False):
    if as_root:
        command = ["adb", "shell", "su", "-c", " ".join(command)]
    else:
        command = ["adb", "shell"] + command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    logging.debug(f"Running command: {' '.join(command)}")
    logging.debug(f"Command output: {result.stdout}")
    logging.debug(f"Command error: {result.stderr}")
    return result


def check_root_access():
    command = ["id", "-u"]
    result = run_command(command, as_root=True)
    return result.returncode == 0 and result.stdout.strip() == "0"


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


def get_framebuffer_info(framebuffer_id):
    fb_dir = f"/sys/class/graphics/fb{framebuffer_id}/"

    info_files = ["bits_per_pixel", "virtual_size", "stride", "mode"]
    framebuffer_info = {}

    for info_file in info_files:
        file_path = f"{fb_dir}{info_file}"
        command = ["cat", file_path]
        result = run_command(command, as_root=True)

        if result.returncode != 0:
            logging.error(f"Error accessing {info_file}: {result.stderr}")
            continue

        framebuffer_info[info_file] = result.stdout.strip()

    return framebuffer_info


def parse_virtual_size(virtual_size_str):
    # Attempt to handle different formats
    virtual_size_str = virtual_size_str.replace(',', ' ').strip()
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

        width, height = parse_virtual_size(virtual_size_str)

        if bits_per_pixel == 32:
            pixel_format = "ARGB8888"
        elif bits_per_pixel == 16:
            pixel_format = "RGB565"
        else:
            pixel_format = "Unknown"

        logging.info(f"Framebuffer Width: {width}")
        logging.info(f"Framebuffer Height: {height}")
        logging.info(f"Bits per Pixel: {bits_per_pixel}")
        logging.info(f"Stride: {stride}")
        logging.info(f"Mode: {mode}")
        logging.info(f"Pixel Format: {pixel_format}")

        if physical_size:
            logging.info(f"Physical Size: {physical_size[0]}x{physical_size[1]}")

    except Exception as e:
        logging.error(f"Error parsing framebuffer information: {str(e)}")


def main():
    if not check_root_access():
        logging.warning("Not running as root. Attempting to switch to root...")
        command = ["adb", "shell", "su", "-c", f"python3 {sys.argv[0]}"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logging.error(f"Error gaining root access: {result.stderr}")
            return
        return

    framebuffer_id, framebuffer_driver = get_framebuffer_id_and_driver()
    if framebuffer_id is None:
        return

    logging.info(f"Framebuffer ID: {framebuffer_id}")
    logging.info(f"Framebuffer Driver: {framebuffer_driver}")

    framebuffer_info = get_framebuffer_info(framebuffer_id)
    if framebuffer_info:
        logging.info(f"Framebuffer info: {framebuffer_info}")
        physical_size = get_physical_size()
        parse_and_display_info(framebuffer_info, physical_size)


if __name__ == "__main__":
    main()
