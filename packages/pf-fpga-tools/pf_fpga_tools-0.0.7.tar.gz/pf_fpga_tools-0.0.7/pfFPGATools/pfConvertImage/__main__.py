# SPDX-FileCopyrightText: 2023-present Didier Malenfant
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import traceback

from .pfConvertImage import pfConvertImage
from pfFPGATools.exceptions import ArgumentError

# -- This enables more debugging information for exceptions.
_debug_on: bool = False


def main():
    global _debug_on

    try:
        if '--debug' in sys.argv:
            print('Enabling debugging information.')
            _debug_on = True

        # -- Remove the first argument (which is the script filename)
        pfConvertImage(sys.argv[1:]).main()
    except ArgumentError as e:
        print(str(e))
    except Exception as e:
        if _debug_on is True:
            print(traceback.format_exc())
        else:
            print(e)

        sys.exit(1)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        pass


if __name__ == '__main__':
    main()
