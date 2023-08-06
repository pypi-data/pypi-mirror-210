#!/usr/bin/env python3

"""
▶︎▶︎ ToDoDescribeThePurpose
▶︎▶︎ Replace param0 or delete

Copyright by SuperUdo3000, #MONTH #YEAR
Version = 0.1            (cccc-type-1)
"""


import os
import time

_AUTOTEST = False


def main(filename=None):
    """
    ▶︎▶︎ToDoDescribeWhatItDoes
    :param param0: DemoParameter
    :return:
    :raises:
    """

    print('This script is located in', os.path.abspath(__file__))

    return


def autotest():
    """
    Testing this script / module with all its methods / functions.

    :return:        0: no errors
                    1: with errors
    :raises:        AssertionError
    """

    print('[  ]  starting autotest()', end='\r', flush=True)

    global _AUTOTEST
    _AUTOTEST = True
    no_errors = True

    time.sleep(4)

    # assert(main(None) == None) # ▶︎▶︎ add your own

    if no_errors:
        print('[ok]  completed autotest() without errors.')
        return 0
    else:
        print('[XX]  completed autotest() with errors.')
        return 1


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description=sys.modules['__main__'].__doc__,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-autotest', action='store_true', help='For testing prior to release, no user interaction.')
    parser.add_argument('filename', nargs='?', default=None, help='filename/path to work on')
    args = parser.parse_args()

    if args.autotest:
        exit(autotest())

    main(args.filename)

else:
    print('[ok]  loading completed.')


