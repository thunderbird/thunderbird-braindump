#!/bin/bash

set -e

if [[ ! -f mail/config/version.txt ]]; then
  echo "Doesn't look like a comm repository. $(pwd)"
  exit 1
fi

bump_version.py --minor "mail/config/version.txt" "mail/config/version_display.txt"

newv=$(cat mail/config/version.txt)

hg commit mail/config/version.txt mail/config/version_display.txt -m "No bug - Set version ${newv} for release. r+a=release"

