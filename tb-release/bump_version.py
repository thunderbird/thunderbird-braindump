#!/usr/bin/python
"""
Silly script to do version bumping.

Usage:
    bump_version.py [--minor] filename ..

Bumping patch-level or later is not supported as the use case
for this script is to bump Thunderbird ESR minor versions. Not
much else really gets bumped manually.

Note that if you specify multiple files, they all get the same
content! This is because version.txt is the same as version_display.txt
on comm-esr* repositories.

Seriously, ESR minor version bumping is all this is meant to do!
"""

import argparse
from packaging.version import parse

def main(version_files, bump_minor=False):
    print("Upgrading version in files {}".format(" ".join(version_files)))
    with open(version_files[0], 'r') as f:
        ver = parse(f.read())

    print('Initial version: %s' % ver)

    # Bump the major or minor version.
    ind = 0
    if bump_minor:
        ind += 1

    # `release` attribute is a tuple (i.e. immutable).
    ver_parts = list(ver.release)
    ver_parts[ind] += 1

    # Reset values after the bumped part to zero (eg. 102.1.2 -> 102.2.0)
    for _j in range(ind+1, len(ver_parts)):
        ver_parts[_j] = 0

    ver = parse(".".join([str(p) for p in ver_parts]))
    print('New version: %s' % ver)

    for _file in version_files:
        with open(_file, 'w') as f:
            f.write(str(ver))
            f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bump a major or minor version number.')
    parser.add_argument('--minor', action='store_true',
                        help='Bump the minor version instead of the major version.')
    parser.add_argument('version_files', nargs="+", help='Version files to bump.')

    options = parser.parse_args()

    main(options.version_files, options.minor)
