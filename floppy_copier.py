from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from time import sleep
from datetime import datetime
import subprocess
import os
import glob
import shutil

PLUGIN_TIMEOUT = 60

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)


def status(text, draw):
    draw.rectangle((0, 32, 128, 64), fill="black")
    draw.text((4, 40), text, fill="white")


def header(has_floppy, has_usb, draw):
    draw.rectangle((0, 0, 128, 32), fill="black")
    if has_floppy:
        draw.text((5, 0), "Floppy", fill="white")
    if has_usb:
        draw.text((69, 0), "USB", fill="white")


def progress(state, maximum, draw):
    draw.rectangle((0, 16, int(128./maximum*state), 32), fill="white")


def check_floppy():
    interfaces_to_check = ["/dev/sda", "/dev/sdb"]
    for interface in interfaces_to_check:
        if os.path.exists(interface) and not os.path.exists(interface+"1") and subprocess.run(["sudo", "blkid", interface]).returncode == 0:
            return interface
    return None


def mount_floppy(device):
    return subprocess.run(["sudo", "mount", device, "/media/floppy", "-o", "umask=000"]).returncode == 0


def umount_floppy():
    return subprocess.run(["sudo", "umount", "/media/floppy"]).returncode == 0


def mount_usb(device):
    return subprocess.run(["sudo", "mount", device+"1", "/media/usb", "-o", "umask=000"]).returncode == 0


def umount_usb():
    return subprocess.run(["sudo", "umount", "/media/usb"]).returncode == 0


def check_usb():
    interfaces_to_check = ["/dev/sda", "/dev/sdb"]
    for interface in interfaces_to_check:
        if os.path.exists(interface) and os.path.exists(interface+"1"):
            return interface
    return None


floppy_present = False
usb_present = False
time_without_floppy = 0
while time_without_floppy < PLUGIN_TIMEOUT:
    floppy = check_floppy()
    usb = check_usb()
    # if both Floppy and USB are present and not yet mounted, try to do so
    if not floppy_present and floppy is not None and usb is not None:
        with canvas(device) as draw:
            header(True, True, draw)
            status("Mounting Floppy...", draw)
        floppy_present = mount_floppy(floppy)
    if floppy_present:
        time_without_floppy = 0
        if not usb_present:
            usb_present = mount_usb(usb)
        if not usb_present:
            continue
        # Copy routine goes here
        usb_folder = f"/media/usb/{datetime.today().strftime('%Y-%m-%d')}"
        os.makedirs(usb_folder, exist_ok=True)
        files = glob.glob("/media/floppy/*.JPG")
        for i, file in enumerate(files):
            with canvas(device) as draw:
                header(True, True, draw)
                progress(i, len(files), draw)
                status(f"Copy {os.path.basename(file)}", draw)
            try:
                shutil.move(file, usb_folder, copy_function=shutil.copy)
            except PermissionError:
                pass
        # Unmount stuff
        with canvas(device) as draw:
            header(True, True, draw)
            status("Unmounting...", draw)
        umount_floppy()
        umount_usb()
        usb_present = False
        # Wait for user
        with canvas(device) as draw:
            header(True, True, draw)
            status("Remove Floppy...", draw)
        while True:
            if check_floppy() is None:
                floppy_present = False  
                break
            sleep(1)
    else:
        time_without_floppy += 1
    with canvas(device) as draw:
        header(floppy is not None, usb is not None, draw)
        progress(PLUGIN_TIMEOUT - time_without_floppy, PLUGIN_TIMEOUT, draw)
        status(f"Shutdown in {PLUGIN_TIMEOUT - time_without_floppy}s", draw)
    sleep(1)
