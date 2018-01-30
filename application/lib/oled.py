
import re,sys,os

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

class OLED(object):
    def __init__(self):

        # 128x32 self.display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

        # Initialize library.
        self.disp.begin()

        # Clear self.display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.image = Image.new('1', (self.disp.width, self.disp.height))

        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        self.top = padding
        bottom = self.disp.height-padding

        self.font_titan = ImageFont.truetype('static/TITAN2.ttf', 38)
        self.font       = ImageFont.load_default()
        self.fontsize = 8

        self.buffer=['']*4

        self.draw()

    def stats(self):
        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d\' \' -f1"
        self.buffer[0] = subprocess.check_output(cmd, shell = True )
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        self.buffer[1] = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        self.buffer[2] = subprocess.check_output(cmd, shell = True )
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        self.buffer[3] = subprocess.check_output(cmd, shell = True )

    def setline(self, linenum, msg, clearlower=False):
        self.buffer[linenum] = str(msg)
        if clearlower:
            for k in range(linenum+1,4):
                self.buffer[k] = ''

    def draw(self):
        # Draw a black filled box to clear the image.
        self._draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)

        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0

        for k in range(4):
            self._draw.text((x, self.top+k*self.fontsize), str(self.buffer[k]),  font=self.font, fill=255)

        # self.display image.
        self.disp.image(self.image)
        self.disp.display()
