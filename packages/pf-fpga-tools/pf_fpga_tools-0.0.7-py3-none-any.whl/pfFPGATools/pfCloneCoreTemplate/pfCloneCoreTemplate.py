# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import shutil

from pfFPGATools.__about__ import __version__
from pfFPGATools.utils import Utils
from pfFPGATools.exceptions import ArgumentError


# -- Classes
class pfCloneCoreTemplate:
    """A tool to clone the Github core template."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            self.branch_name = None
            self.tag_name = None

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhvb:t:', ['debug', 'help', 'version', 'branch=', 'tag='])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    pfCloneCoreTemplate.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfCloneCoreTemplate.printVersion()
                    sys.exit(0)
                elif o in ('-b', '--branch'):
                    if self.tag_name is not None:
                        raise ArgumentError('Cannot specificy both a branch and a tag on the command line.')

                    self.branch_name = a
                elif o in ('-t', '--tag'):
                    if self.branch_name is not None:
                        raise ArgumentError('Cannot specificy both a branch and a tag on the command line.')

                    self.tag_name = a

            nb_of_arguments: int = len(arguments)
            if nb_of_arguments != 1:
                raise ArgumentError('Invalid arguments. Maybe start with `pfCloneCoreTemplate --help?')

            self.destination_folder: str = arguments[0]

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfCloneCoreTemplate --help?')
            sys.exit(0)

    def main(self) -> None:
        if Utils.commandExists('git') is False:
            raise RuntimeError('You must have git installed on your machine to continue.')

        repo_folder = os.path.join(self.destination_folder, 'pfCoreTemplate')
        if os.path.exists(repo_folder):
            shutil.rmtree(repo_folder)

        print('Cloning core template in \'' + repo_folder + '\'.')

        command_line = ['git', 'clone', '--depth', '1']

        if self.branch_name is not None:
            command_line.append('--branch')
            command_line.append(self.branch_name)
        elif self.tag_name is not None:
            command_line.append('--branch')
            command_line.append(self.tag_name)

        command_line.append('https://github.com/DidierMalenfant/pfCoreTemplate.git')

        Utils.shellCommand(command_line, from_dir=self.destination_folder, silent_mode=True)

        git_folder = os.path.join(repo_folder, '.git')
        if os.path.exists(git_folder):
            shutil.rmtree(git_folder)

    @classmethod
    def printUsage(cls) -> None:
        pfCloneCoreTemplate.printVersion()
        print('')
        print('usage: pfCloneCoreTemplate <options> destination_folder')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h          - Show a help message.')
        print('   --version/-v       - Display the app\'s version.')
        print('   --debug/-d         - Enable extra debugging information.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfCloneCoreTemplate v' + __version__ + ' 🛠️')
