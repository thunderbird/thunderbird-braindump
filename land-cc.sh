#!/usr/bin/env bash
# Land multiple Phab revisions with single command.
#
# Each argument is a Phab revision followed by the reviewer separated by a dash
# Example:
#    land-cc.sh D12345-darktrojan D12346-aleca,freaktechnik

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 Dnnnnn-REVIEWER ..."
  exit 1
fi

while [[ -n "$1" ]]; do
  DX="${1%%-*}"
  REVIEWER="${1##*-}"
  echo "Landing $DX..."
  moz-phab patch "$DX" --no-bookmark --skip-dependencies --apply-to .
  COMMIT=$(hg log -r . --template "{desc}" | sed -E "1,1s/rs?=.*$/r=$REVIEWER/")
  hg metaedit --date now -l - <<_EOF_
$COMMIT
_EOF_
  shift
done

