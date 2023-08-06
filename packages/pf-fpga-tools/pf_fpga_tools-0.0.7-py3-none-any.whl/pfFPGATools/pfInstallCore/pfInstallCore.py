# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import zipfile
import tempfile
import shutil
import contextlib

from pathlib import Path

from distutils.dir_util import copy_tree

from pfFPGATools.__about__ import __version__
from pfFPGATools.utils import Utils


# -- Classes
class pfInstallCore:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            self.name_of_core_to_delete: str = None
            self.volume_name: str = None
            self.zip_filename: str = None
            self.eject_after_install: bool = False

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhver:', ['debug', 'help', 'version', 'eject', 'remove='])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    pfInstallCore.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfInstallCore.printVersion()
                elif o in ('-e', '--eject'):
                    self.eject_after_install = True
                elif o in ('-r', '--remove'):
                    self.name_of_core_to_delete = a

            nb_of_arguments: int = len(arguments)

            if self.name_of_core_to_delete is None:
                if nb_of_arguments != 2:
                    raise RuntimeError('Invalid arguments. Maybe start with `pfInstallCore --help?')

                self.zip_filename = arguments[0]
                self.volume_name = arguments[1]

                components = os.path.splitext(self.zip_filename)
                if len(components) != 2 or components[1] != '.zip':
                    raise RuntimeError('Can only install zipped up core files.')

                if not os.path.exists(self.zip_filename):
                    raise RuntimeError('File \'' + self.zip_filename + '\' does not exist.')
            else:
                if nb_of_arguments != 1:
                    raise RuntimeError('Invalid arguments. Maybe start with \'pfInstallCore --help?\'')

                self.volume_name = arguments[0]

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfInstallCore --help?')
            sys.exit(0)

    def destCoresFolder(self) -> str:
        return os.path.join('/Volumes', self.volume_name, 'Cores')

    def destPlatformsFolder(self) -> str:
        return os.path.join('/Volumes', self.volume_name, 'Platforms')

    def deleteFile(self, filepath) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filepath)

    def deleteCore(self) -> None:
        cores_folder = self.destCoresFolder()
        core_folder = os.path.join(self.destCoresFolder(), self.name_of_core_to_delete)

        if os.path.exists(core_folder):
            print('Deleting ' + core_folder + '...')
            shutil.rmtree(core_folder, ignore_errors=True)

        hidden_core_data = os.path.join(self.destCoresFolder(), '._' + self.name_of_core_to_delete)
        if os.path.exists(hidden_core_data):
            print('Deleting ' + hidden_core_data + '...')
            self.deleteFile(hidden_core_data)

        core_name = pfInstallCore.coreNameFrom(self.name_of_core_to_delete)
        if core_name is None:
            raise RuntimeError('Could not figure out the core name from \'' + self.name_of_core_to_delete + ' \'.')

        for p in Path(cores_folder).rglob('*'):
            if not os.path.isdir(p):
                continue

            if pfInstallCore.coreNameFrom(os.path.basename(p)) == core_name:
                print('Found another implementation of the ' + core_name + ' platform, not deleting any Plaform data for this core.')
                return

        platforms_folder = self.destPlatformsFolder()
        core_name = core_name.lower()
        for p in Path(platforms_folder).rglob('*'):
            if os.path.isdir(p):
                continue

            filename = os.path.basename(p)
            if filename == core_name + '.bin':
                print('Deleting ' + str(p) + '...')
                self.deleteFile(p)
            elif filename == core_name + '.json':
                print('Deleting ' + str(p) + '...')
                self.deleteFile(p)
            elif filename == '._' + core_name + '.bin':
                print('Deleting ' + str(p) + '...')
                self.deleteFile(p)
            elif filename == '._' + core_name + '.json':
                print('Deleting ' + str(p) + '...')
                self.deleteFile(p)

    def installCore(self) -> None:
        # -- In a temporary folder.
        with tempfile.TemporaryDirectory() as tmp_dir:
            # -- Unzip the file.
            with zipfile.ZipFile(self.zip_filename, 'r') as zip_ref:
                zip_ref.extractall(tmp_dir)

            # -- Copy core files
            print('Copying core files...')

            core_src_folder = os.path.join(tmp_dir, 'Cores')
            core_dest_folder = self.destCoresFolder()

            if not os.path.isdir(core_src_folder):
                raise RuntimeError('Cannot find \'' + core_src_folder + '\' in the core release zip file.')

            copy_tree(core_src_folder, core_dest_folder)

            # -- Copy platform files
            print('Copying platforms files...')

            platforms_src_folder = os.path.join(tmp_dir, 'Platforms')
            platforms_dest_folder = self.destPlatformsFolder()

            if not os.path.isdir(platforms_src_folder):
                raise RuntimeError('Cannot find \'' + platforms_src_folder + '\' in the core release zip file.')

            copy_tree(platforms_src_folder, platforms_dest_folder)

        if self.eject_after_install:
            print('Ejecting \'' + self.volume_name + '\'.')
            Utils.shellCommand(['diskutil', 'eject', self.volume_name])

    def main(self) -> None:
        if self.name_of_core_to_delete is not None:
            self.deleteCore()
        else:
            self.installCore()

    @classmethod
    def coreNameFrom(cls, name: str) -> str:
        components = os.path.splitext(name)
        if len(components) != 2:
            return None

        return components[1][1:]

    @classmethod
    def printUsage(cls) -> None:
        pfInstallCore.printVersion()
        print('')
        print('usage: pfInstallCore <options> zip_file dest_volume')
        print('usage: pfInstallCore --delete core_name dest_volume')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h             - Show a help message.')
        print('   --version/-v          - Display the app\'s version.')
        print('   --debug/-d            - Enable extra debugging information.')
        print('   --remove/-r <name>    - Delete a core on the given volume.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfInstallCore v' + __version__ + ' 🛠️')
