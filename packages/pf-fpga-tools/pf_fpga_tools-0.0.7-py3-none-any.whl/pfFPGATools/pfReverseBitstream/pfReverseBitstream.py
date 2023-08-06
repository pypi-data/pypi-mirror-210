# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt

from pfFPGATools.__about__ import __version__


# -- Classes
class pfReverseBitstream:
    """A tool to reverse the bitstream of an rbf file for an Analog Pocket core."""

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
                    pfReverseBitstream.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfReverseBitstream.printVersion()
                    sys.exit(0)

            nb_of_arguments: int = len(arguments)
            if nb_of_arguments != 2:
                raise RuntimeError('Invalid arguments.Maybe start with `pfReverseBitstream --help?')

            self.rbf_filename: str = arguments[0]
            self.rbf_r_filename: str = arguments[1]

            components = os.path.splitext(self.rbf_filename)
            if len(components) != 2 or components[1] != '.rbf':
                raise RuntimeError('Can only reverse .rbf files.')

            if not os.path.exists(self.rbf_filename):
                raise RuntimeError('File \'' + self.rbf_filename + '\' does not exist.')

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfReverseBitstream --help?')
            sys.exit(0)

    def main(self) -> None:
        print('Reading \'' + self.rbf_filename + '\'.')
        input_file = open(self.rbf_filename, 'rb')
        input_data = input_file.read()
        input_file.close()

        reversed_data = []
        print('Reversing ' + str(len(input_data)) + ' bytes.')
        for byte in input_data:
            reversed_byte = ((byte & 1) << 7) | ((byte & 2) << 5) | ((byte & 4) << 3) | ((byte & 8) << 1) | ((byte & 16) >> 1) | ((byte & 32) >> 3) | ((byte & 64) >> 5) | ((byte & 128) >> 7)
            reversed_data.append(reversed_byte)

        print('Writing \'' + self.rbf_r_filename + '\'.')
        output_file = open(self.rbf_r_filename, 'wb')
        output_file.write(bytearray(reversed_data))
        output_file.close()

    @classmethod
    def printUsage(cls) -> None:
        pfReverseBitstream.printVersion()
        print('')
        print('usage: pfReverseBitstream <options> src_filename dest_filename')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h          - Show a help message.')
        print('   --version/-v       - Display the app\'s version.')
        print('   --debug/-d         - Enable extra debugging information.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfReverseBitstream v' + __version__ + ' 🛠️')
