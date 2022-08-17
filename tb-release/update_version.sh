#!/bin/bash

if [[ ! -f mail/config/version.txt ]]; then
  echo "Doesn't look like a comm repository. $(pwd)"
  exit 1
fi

if [[ -n "$1" ]]; then
  echo "$1" > mail/config/version.txt
  echo "$1" > mail/config/version_display.txt

  hg commit mail/config/version.txt mail/config/version_display.txt -m "No bug - Set version ${1} for release. r+a=release"
else
  echo "No version given."
  exit 2
fi

