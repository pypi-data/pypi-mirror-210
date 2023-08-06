# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import traceback

from pfFPGATools.__about__ import __version__
from pfFPGATools.utils import Utils

from PIL import Image


# -- Classes
class pfConvertImage:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhv', ['debug', 'help', 'version'])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    pfConvertImage.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfConvertImage.printVersion()
                    sys.exit(0)

            nb_of_arguments: int = len(arguments)
            if nb_of_arguments != 2:
                raise RuntimeError('Invalid arguments. Maybe start with `pfConvertImage --help?')

            self.img_filename: str = arguments[0]
            self.bin_filename: str = arguments[1]

            if not os.path.exists(self.img_filename):
                raise RuntimeError('File \'' + self.img_filename + '\' does not exist.')

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfConvertImage --help?')
            sys.exit(0)

    def main(self) -> None:
        # -- We need brew to potentially install other things
        Utils.requireCommand('convert')

        print('Reading \'' + self.img_filename + '\'.')
        img = Image.open(self.img_filename).convert("RGB")

        print('Image size is %dx%d pixels.' % (img.width, img.height))

        pixels = img.load()

        byte_data = []
        warned_against_greyscale = False

        # -- Analog Pocket Image Format is 16-bit monochrome stored rotated 90 degrees counter-clockwise.
        for x in range(img.width - 1, -1, -1):
            for y in range(0, img.height):
                # print('  %dx%d : %s' % (x, y, pixels[x, y]))

                pixel = pixels[x, y]
                if warned_against_greyscale is False and ((pixel[0] != pixel[1]) or (pixel[0] != pixel[2])):
                    print('WARNING: Image is not greyscale, results may be incorrect.')
                    warned_against_greyscale = True

                # -- Each pixel is 16 bits. The brightness is stored in the upper 8 bits.
                # -- A fully on pixel value is 0xFF00. A fully off pixel value is 0x0000.
                # -- Source image should be greyscale but in case it isn't, we average RBB here to convert it.
                byte_data.append(int((pixel[0] + pixel[1] + pixel[2]) / 3))
                byte_data.append(0x00)

        print('Writing \'' + self.bin_filename + '\'.')
        output_file = open(self.bin_filename, 'wb')
        output_file.write(bytearray(byte_data))
        output_file.close()

    @classmethod
    def printUsage(cls) -> None:
        pfConvertImage.printVersion()
        print('')
        print('usage: pfConvertImage <options> src_filename dest_filename')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h          - Show a help message.')
        print('   --version/-v       - Display the app\'s version.')
        print('   --debug/-d         - Enable extra debugging information.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfConvertImage v' + __version__ + ' 🛠️')
