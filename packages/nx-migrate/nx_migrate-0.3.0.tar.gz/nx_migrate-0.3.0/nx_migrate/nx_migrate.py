#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Wei Sun"
__copyright__ = "Copyright (C) 2019 GFLoan Co. LTD"
__license__ = "Private"
__version__ = "1.0"


import os
import subprocess
import sys
import argparse


def nx_migrate(user_dir):
    # Check if the directory exists
    if not os.path.isdir(user_dir):
        print(f"The directory {user_dir} does not exist")
        sys.exit()

    # Store the current location
    current_location = os.getcwd()

    try:
        # Change the current location to the directory
        os.chdir(user_dir)

        # Execute the nx migrate command
        subprocess.check_call(["nx", "migrate", "latest"])
    finally:
        # Regardless of what happens, restore the location
        os.chdir(current_location)


def main():
    parser = argparse.ArgumentParser(description="Migrate nx project")
    parser.add_argument(
        "-u", "--user_dir", help="User directory to switch to", required=True
    )
    args = parser.parse_args()
    nx_migrate(args.user_dir)


if __name__ == "__main__":
    main()
