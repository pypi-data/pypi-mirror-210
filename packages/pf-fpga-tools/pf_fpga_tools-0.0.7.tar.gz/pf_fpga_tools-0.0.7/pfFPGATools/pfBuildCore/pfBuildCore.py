# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getopt
import shutil
import traceback

from pfFPGATools.__about__ import __version__
from pfFPGATools.utils import Utils

from datetime import date
from pathlib import Path
from typing import List
from typing import Dict

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# -- Classes
class pfBuildCore:
    """A tool to build an analog pocket core"""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        self.short_name: str = None

        try:
            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhv', ['debug', 'help', 'version', 'corefilename', 'bitstreamfile'])

            print_core_filename: bool = False
            print_bitstream_file: bool = False

            for o, a in opts:
                if o in ('-d', '--debug'):
                    # -- We ignore this argument because it was already dealt with in the calling main() code.
                    continue
                elif o in ('-h', '--help'):
                    pfBuildCore.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfBuildCore.printVersion()
                    sys.exit(0)
                elif o in ('--corefilename'):
                    print_core_filename = True
                elif o in ('--bitstreamfile'):
                    print_bitstream_file = True

            nb_of_arguments: int = len(arguments)
            if print_core_filename is False and print_bitstream_file is False and nb_of_arguments != 2:
                raise RuntimeError('Invalid arguments. Maybe start with `pfBuildCore --help?')

            self.config_filename: str = arguments[0]

            components = os.path.splitext(self.config_filename)
            if len(components) != 2 or components[1] != '.toml':
                raise RuntimeError('Config file needs to be a toml file.')

            if not os.path.exists(self.config_filename):
                raise RuntimeError('File \'' + self.config_filename + '\' does not exist.')

            self.config_file_folder = os.path.dirname(self.config_filename)

            with open(self.config_filename, mode="rb") as fp:
                self.config = tomllib.load(fp)

            self.today = str(date.today())

            if print_core_filename is True:
                print(self.packagedFilename())
                sys.exit(0)
            elif print_bitstream_file is True:
                print(self.bitstreamFile())
                sys.exit(0)

            self.destination_folder: str = arguments[1]
            self.core_folder = os.path.join(self.destination_folder, '_core')

            self.dependency_count = 0

        except getopt.GetoptError:
            print('Unknown option or argument. Maybe start with `pfBuildCore --help?')
            sys.exit(0)

    def getConfigParam(self, section_name: str, param_name: str) -> str:
        section: Dict = self.config.get(section_name, None)

        if section is None:
            raise RuntimeError('Can\'t find section named %s in config file.' % (section_name))

        param: str = section.get(param_name, None)
        if param is None:
            raise RuntimeError('Can\'t find parameter %s in sectior %s config file.' % (param_name, section_name))

        return param

    def getShortName(self) -> str:
        if self.short_name is None:
            self.short_name = self.getConfigParam('Platform', 'short_name')

            for c in self.short_name:
                if (c.isalnum() is False) or c.isupper():
                    raise RuntimeError('Platform short name should be lower-case and can only contain a-z, 0-9 or _.')

        return self.short_name

    def generateDefinitionFiles(self, cores_folder, platforms_folder) -> None:
        output_filename = os.path.join(cores_folder, 'audio.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "audio": {\n')
            out_file.write('    "magic": "APF_VER_1"\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'data.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "data": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "data_slots": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'input.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "input": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "controllers": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'variants.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "variants": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variant_list": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'interact.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "interact": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variables": [],\n')
            out_file.write('    "messages": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'video.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "video": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "scaler_modes": [\n')
            out_file.write('      {\n')
            out_file.write('        "width": %d,\n' % (self.getConfigParam('Video', 'width')))
            out_file.write('        "height": %d,\n' % (self.getConfigParam('Video', 'height')))
            out_file.write('        "aspect_w": %d,\n' % (self.getConfigParam('Video', 'aspect_w')))
            out_file.write('        "aspect_h": %d,\n' % (self.getConfigParam('Video', 'aspect_h')))
            out_file.write('        "rotation": %d,\n' % (self.getConfigParam('Video', 'rotation')))
            out_file.write('        "mirror": %d\n' % (self.getConfigParam('Video', 'mirror')))
            out_file.write('      }\n')
            out_file.write('    ]\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(platforms_folder, '%s.json' % (self.getShortName()))
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "platform": {\n')
            out_file.write('    "category": "%s",\n' % (self.getConfigParam('Platform', 'category')))
            out_file.write('    "name": "%s",\n' % (self.getConfigParam('Platform', 'name')))
            out_file.write('    "year": %s,\n' % (self.today.split('-')[0]))
            out_file.write('    "manufacturer": "%s"\n' % (self.getConfigParam('Author', 'name')))
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(cores_folder, 'core.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "core": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "metadata": {\n')
            out_file.write('      "platform_ids": ["%s"],\n' % (self.getShortName()))
            out_file.write('      "shortname": "%s",\n' % (self.getShortName()))
            out_file.write('      "description": "%s",\n' % (self.getConfigParam('Platform', 'description')))
            out_file.write('      "author": "%s",\n' % (self.getConfigParam('Author', 'name')))
            out_file.write('      "url": "%s",\n' % (self.getConfigParam('Author', 'url')))
            out_file.write('      "version": "%s",\n' % (self.getConfigParam('Build', 'version')))
            out_file.write('      "date_release": "%s"\n' % (self.today))
            out_file.write('    },\n')
            out_file.write('    "framework": {\n')
            out_file.write('      "target_product": "Analogue Pocket",\n')
            out_file.write('      "version_required": "1.1",\n')
            out_file.write('      "sleep_supported": false,\n')
            out_file.write('      "dock": {\n')
            out_file.write('        "supported": true,\n')
            out_file.write('        "analog_output": false\n')
            out_file.write('      },\n')
            out_file.write('      "hardware": {\n')
            out_file.write('        "link_port": false,\n')
            out_file.write('        "cartridge_adapter": -1\n')
            out_file.write('      }\n')
            out_file.write('    },\n')
            out_file.write('    "cores": [\n')
            out_file.write('      {\n')
            out_file.write('        "name": "default",\n')
            out_file.write('        "id": 0,\n')
            out_file.write('        "filename": "%s.rbf_r"\n' % (self.getShortName()))
            out_file.write('      }\n')
            out_file.write('    ]\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def convertImages(self, cores_folder, platforms_image_folder, dep_file) -> None:
        convert_image_command = 'pfConvertImage'

        src_image_file = os.path.join(self.config_file_folder, self.getConfigParam('Platform', 'image'))
        dest_bin_file = os.path.join(platforms_image_folder, '%s.bin' % (self.getShortName()))
        Utils.shellCommand([convert_image_command, src_image_file, dest_bin_file])
        self.addDependency(dep_file, src_image_file)

        src_image_file = os.path.join(self.config_file_folder, self.getConfigParam('Author', 'icon'))
        dest_bin_file = os.path.join(cores_folder, 'icon.bin')
        Utils.shellCommand([convert_image_command, src_image_file, dest_bin_file])
        self.addDependency(dep_file, src_image_file)

    def outputFilename(self):
        return os.path.join(self.destination_folder, self.packagedFilename())

    def packageCore(self):
        deps = []
        packaged_filename = os.path.abspath(os.path.join(self.destination_folder, self.packagedFilename()))
        if os.path.exists(packaged_filename):
            os.remove(packaged_filename)

        arguments: List[str] = ['zip', '-r', packaged_filename]
        for p in Path(self.core_folder).rglob('*'):
            if os.path.isdir(p):
                continue

            arguments.append(str(p.relative_to(self.core_folder)))
            deps.append(str(p))

        Utils.shellCommand(arguments, from_dir=self.core_folder)

    def addDependency(self, dep_file, dep):
        if self.dependency_count == 0:
            output_filename = os.path.join(self.destination_folder, self.packagedFilename())
            dep_file.write('%s: %s' % (output_filename.replace(' ', '\\ '), self.config_filename))

        dep_file.write(' \\\n %s' % (dep))

        self.dependency_count += 1

    def fullPlatformName(self) -> str:
        return '%s.%s' % (self.getConfigParam('Author', 'name'), self.getShortName())

    def packagedFilename(self) -> str:
        return '%s-%s-%s.zip' % (self.fullPlatformName(), self.getConfigParam('Build', 'version'), self.today)

    def bitstreamFile(self) -> str:
        return os.path.expandvars(self.getConfigParam('Bitstream', 'source'))

    def main(self) -> None:
        # -- We delete the core build folder in case stale files are in there (for example after changing the core config file)
        if os.path.exists(self.core_folder):
            shutil.rmtree(self.core_folder)

        os.makedirs(self.core_folder)

        full_platform_name = self.fullPlatformName()
        cores_folder = os.path.join(self.core_folder, 'Cores', full_platform_name)
        os.makedirs(cores_folder, exist_ok=True)

        platforms_folder = os.path.join(self.core_folder, 'Platforms')
        os.makedirs(platforms_folder, exist_ok=True)

        platforms_image_folder = os.path.join(platforms_folder, '_images')
        os.makedirs(platforms_image_folder, exist_ok=True)

        dependency_filename = os.path.join(self.destination_folder, 'deps.d')
        with open(dependency_filename, 'w') as dep_file:
            print('Reversing bitstream file...')
            bitstream_source = self.bitstreamFile()
            bitstream_dest = os.path.join(cores_folder, '%s.rbf_r' % self.getShortName())
            Utils.shellCommand(['pfReverseBitstream', bitstream_source, bitstream_dest])

            self.addDependency(dep_file, bitstream_source)

            print('Generating definitions files...')
            self.generateDefinitionFiles(cores_folder, platforms_folder)

            print('Converting images...')
            self.convertImages(cores_folder, platforms_image_folder, dep_file)

            platform_config = self.config.get('Platform', None)
            if platform_config is not None:
                info_file = platform_config.get('info', None)
                if info_file is not None:
                    src_info = os.path.join(self.config_file_folder, info_file)
                dest_info = os.path.join(cores_folder, 'info.txt')
                shutil.copyfile(src_info, dest_info)

                self.addDependency(dep_file, src_info)

            dep_file.write('\n')

            print('Packaging core...')
            self.packageCore()

    @classmethod
    def printUsage(cls) -> None:
        pfBuildCore.printVersion()
        print('')
        print('usage: pfBuildCore <options> config_file destination_folder')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h          - Show a help message.')
        print('   --version/-v       - Display the app\'s version.')
        print('   --debug/-d         - Enable extra debugging information.')
        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('🛠️  pfBuildCore v' + __version__ + ' 🛠️')
