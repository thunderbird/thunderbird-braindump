#!/bin/bash

set -e

UPSTREAM_REPO="$1"
# START_TAG="FIREFOX_101_0b1_BUILD1"
START_TAG="$2"
# END_TAG="FIREFOX_101_0b5_RELEASE"
END_TAG="$3"

# cd $HOME/moz/m-b
# Current dir must be a mozilla-unified clone. comm/ subdirectory must exist.
# firefoxtree extension must be installed!

function usage() {
  echo "Usage: $(basename "$0")  beta|esr91|esr102 START_TAG END_TAG"
  echo "START_TAG and END_TAG can be any valid mercurial tag, bookmark, or revision."
  exit 0
}

function inArray() {
    # $1 is your needle
    # $2 is your haystack
    # Returns $TRUE or $FALSE
    # Usage: inArray "needle" "${HAYSTACK[@]}"
    local hay needle="$1"
    shift
    for hay; do
      [[ "$hay" == "$needle" ]] && return 0
    done
    return 1
}

function die() {
    # $1 is message to print
    # Usage: die "message"
    local message="$1"
    echo "$message"
    exit 1
}

inArray "--help" "$@" || inArray "-h" "$@" && usage

inArray "$UPSTREAM_REPO" beta esr102 esr115 || die "UPSTREAM_REPO ($UPSTREAM_REPO) is invalid"

[[ -f .hg/hgrc ]] || die "Current directory does not look like a Mercurial repo!"
[[ -f comm/.hg/hgrc ]] || die "comm/ subdirectory not found!"

[[ -n "$START_TAG" ]] || die "START_TAG not provided"
[[ -n "$END_TAG" ]] || die "END_TAG not provided"


hg pull "$UPSTREAM_REPO"
hg up "$UPSTREAM_REPO"

M_BUGS=($(hg log -r "${START_TAG}:${END_TAG} and ancestors($END_TAG)" -T '{bug}\n' | sort -u))

cd comm || die "Unable to chdir to comm/ - If this happens something is very wrong!"
hg pull comm
hg up comm

echo ""
echo "Bugs to port will print the first line of the commit message."
echo ""
BUGS_4_REV=$(echo ${M_BUGS[*]} | sed -e 's/ /|/g')
hg log -T '{desc|firstline}\n' -r "grep(r'[Pp]ort [Bb]ug $BUGS_4_REV')"

#for BUGNO in ${M_BUGS[*]}; do
#  echo "$BUGNO"
#  hg log -T '{desc|firstline}  ' -r "keyword(\"ort bug $BUGNO\")"
#done

