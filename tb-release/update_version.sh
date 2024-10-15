#!/bin/bash

if [[ ! -f mail/config/version.txt ]]; then
  echo "Doesn't look like a comm repository. $(pwd)"
  exit 1
fi

VD="$1"
V="${1%%esr}"

if [[ -n "$1" ]]; then
  echo "$V" > mail/config/version.txt
  echo "$VD" > mail/config/version_display.txt

  hg commit mail/config/version.txt mail/config/version_display.txt -m "No bug - Set version ${VD} for release. r+a=release"
else
  echo "No version given."
  exit 2
fi

