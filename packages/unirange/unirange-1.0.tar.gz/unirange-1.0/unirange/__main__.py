#!/usr/bin/env python3
# coding=utf-8
# SPDX-License-Identifier: MIT
"""CLI for unirange."""
import argparse

import unirange

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=unirange.__version__)
    parser.add_argument("unirange", help="The unirange notation.")

    args = parser.parse_args()

    try:
        for char in sorted(unirange.unirange_to_characters(args.unirange)):
            print(char, end=" ")
        print()
    except unirange.UnirangeError as exc:
        raise exc from None
