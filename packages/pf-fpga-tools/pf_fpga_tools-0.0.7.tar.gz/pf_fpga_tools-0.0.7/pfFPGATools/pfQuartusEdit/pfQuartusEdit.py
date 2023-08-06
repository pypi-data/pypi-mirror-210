# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import tempfile
import shutil
import filecmp
import multiprocessing

from typing import List
from enum import Enum

from pfFPGATools.__about__ import __version__
from pfFPGATools.exceptions import ArgumentError


# -- Classes
class EditingState(Enum):
    BEFORE_EDIT = 1
    DURING_EDIT = 2
    AFTER_EDIT = 3


class pfQuartusEdit:
    """A tool to edit Quartus project files."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            self.qsf_file: str = None
            self.verilog_files: List[str] = []
            self.number_of_cpus: int = 0

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhvq:n:', ['debug', 'help', 'version', 'qsf=', 'numcpus='])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    pfQuartusEdit.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfQuartusEdit.printVersion()
                    sys.exit(0)
                elif o in ('-q', '--qsf'):
                    self.qsf_file = a

                    if not self.qsf_file.endswith('.qsf'):
                        raise ArgumentError('Invalid file type for --qsf argument.')
                elif o in ('-n', '--numcpus'):
                    if a == 'max':
                        self.number_of_cpus = multiprocessing.cpu_count()
                    else:
                        self.number_of_cpus = int(a)

            if self.qsf_file is None:
                raise ArgumentError('Missing QSF file to edit on the command line.')

            if len(arguments) == 0:
                raise ArgumentError('Invalid arguments.Maybe start with `pfQuartusEdit --help?')

            for arg in arguments:
                self.verilog_files.append(arg)

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfQuartusEdit --help?')
            sys.exit(0)

    def writeAdditions(self, dest_file, editing_wrappers: List[str]) -> None:
        dest_file.write(editing_wrappers[0])
        dest_file.write('# ---------------------------\n')

        if self.number_of_cpus != 0:
            dest_file.write('set_global_assignment -name NUM_PARALLEL_PROCESSORS ' + str(self.number_of_cpus) + '\n')

        for file in self.verilog_files:
            dest_file.write('set_global_assignment -name ')

            if file.endswith('.v'):
                dest_file.write('VERILOG_FILE ')
            elif file.endswith('.sv'):
                dest_file.write('SYSTEMVERILOG_FILE ')
            else:
                raise ArgumentError('Unknown file type for \'' + file + '\'.')

            dest_file.write(file + '\n')

        dest_file.write('\n' + editing_wrappers[1])

    def main(self) -> None:
        editing_wrappers: List[str] = ['# Additions made by pfQuartusEdit\n',
                                       '# End of additions made by pfQuartusEdit\n']

        # -- In a temporary folder.
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file: str = os.path.join(tmp_dir, 'temp.qsf')

            src_file = open(self.qsf_file, 'r')
            dest_file = open(tmp_file, 'w')

            editing_state = EditingState.BEFORE_EDIT
            last_line = None

            for line in src_file.readlines():
                last_line = line

                match editing_state:
                    case EditingState.BEFORE_EDIT:
                        if line == editing_wrappers[0]:
                            self.writeAdditions(dest_file, editing_wrappers)

                            editing_state = EditingState.DURING_EDIT
                        else:
                            dest_file.write(line)
                    case EditingState.DURING_EDIT:
                        if line == editing_wrappers[1]:
                            editing_state = EditingState.AFTER_EDIT
                    case EditingState.AFTER_EDIT:
                        dest_file.write(line)

            if editing_state == EditingState.BEFORE_EDIT:
                if not last_line.endswith('\n'):
                    dest_file.write('\n')

                if last_line != '\n':
                    dest_file.write('\n')

                self.writeAdditions(dest_file, editing_wrappers)

            src_file.close()
            dest_file.close()

            if filecmp.cmp(tmp_file, self.qsf_file) is False:
                print('Updating QSF file...')
                shutil.copyfile(tmp_file, self.qsf_file)

    @classmethod
    def printUsage(cls) -> None:
        pfQuartusEdit.printVersion()
        print('')
        print('usage: pfQuartusEdit <options> project_files')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h             - Show a help message.')
        print('   --version/-v          - Display the app\'s version.')
        print('   --debug/-d            - Enable extra debugging information.')
        print('   --qsf/-q <file>       - Name of the QSF file to edit.')
        print('   --numcpus/-n <num>    - Number of CPU cores to use, or \'max\' to use all of them.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfQuartusEdit v' + __version__ + ' 🛠️')
