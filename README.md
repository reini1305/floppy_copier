# USB Floppy Copier
Using a Raspberry Pi to build an autonomous USB-Floppy Disk to USB-Stick copier (e.g. for Mavica photographers)


## BOM
* Raspberry Pi (3 or higher)
* 128x64 px I2C OLED with SSD1306 driver
* SD card for Raspi OS Lite (min. 8GB)
* USB Stick to hold images
* USB Floppy drive
* optional Powerbank, capably of supplying 5V 3A to run the Raspberry Pi

## Installation

Install the current version of Raspi Lite (Version without desktop environment) according to the [official documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system).

Follow the [excellent tutorial](https://peppe8o.com/ssd1306-raspberry-pi-oled-display/) of peppe8o to connect the OLED display to the Raspberry Pi.

The script which runs the floppy copier assumes that it and the virtual environment reside inside the user home directory. Modifiying the guide above install the virtual environment as

~~~
python3 -m venv floppy --system-site-packages
source floppy/bin/activate
pip3 install luma.oled
~~~

After following the rest of the tutorial, copy `floppy_copier.py` and `floppy_copier.sh` to your home folder and launch it for testing purposes
~~~
source floppy/bin/activate  # only once
python3 floppy_copier.py
~~~

### Autostart

It will make sense to run the `floppy_copier.sh` on every boot. A possible way to set this up is using `systemd`:

~~~
sudo nano /etc/systemd/system/floppy_copier.service
~~~

Create a file with the following content (adapt your user name):
~~~
[Unit]
Description=USB Floppy Copier

[Service]
User=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/floppy_copier.sh

[Install]
WantedBy=multi-user.target

~~~