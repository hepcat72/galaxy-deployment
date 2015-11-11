#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Verify env.sh paths are valid
# Usage: find . -name "env.sh" -exec ~/verify_paths.py {} \;

import argparse
import re
import os


env_var_re = re.compile('\w+=(/[^;:]+).*')
env_sh_re = re.compile('.+-f (.+) ].+')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    fh = open(args.file, mode='rb')
    for line in fh:
        line = line.strip()
        m = env_var_re.search(line)
        if not m:
            m = env_sh_re.search(line)
        if m:
            pathref = m.group(1)
            if not os.path.exists(pathref):
                print "%s: MISSING %s" % (args.file, pathref)

if __name__ == "__main__":
    main()
