#!/bin/bash

source_libjfxbash="source $(dirname $0)/libjfxbash"
${source_libjfxbash}

EXPECTED="107.0a1"

ALL_PRODUCT=("Thunderbird-nightly-latest"
	     "Thunderbird-nightly-latest-SSL"
	     "Thunderbird-nightly-latest-l10n"
	     "Thunderbird-nightly-latest-l10n-ssl")
WIN_PRODUCT=("Thunderbird-nightly-msi-latest-SSL"
	     "Thunderbird-nightly-msi-latest-l10n-SSL")
OSX_PRODUCT=("Thunderbird-nightly-pkg-latest-SSL"
	     "Thunderbird-nightly-pkg-latest-l10n-SSL")

PLAT_LINUX=("linux" "linux64")
PLAT_WIN=("win" "win64")
PLAT_OSX=("osx")

build_url() {
  _product="$1"
  _platform="$2"
  _lang="en-US"

  _url="https://download.mozilla.org/?product=${_product}&os=${_platform}&lang=${_lang}"
  echo $_url
}

get_version() {
  sed -e 's/.*thunderbird-//' -e 's/\.en-US..*$//'
}

ck_version() {
  _expected="$1"
  _url="$2"

  _version=$(curl -s "${_url}" | get_version)

  if [[ "${_version}" != "${_expected}" ]]; then
    echo "${_version}"
    return 1
  fi
  return 0
}

ck_exists() {
  _url="$1"

  if ! curl -s -I -L -f "${_url}"; then
    print_RED "FAIL! ${_url}"
  fi
}



for p in ${ALL_PRODUCT[*]}; do
  for o in ${PLAT_LINUX[*]} ${PLAT_WIN[*]} ${PLAT_OSX[*]}; do
    _p_url=$(build_url $p $o)
    echo "Checking ${p} ${o}..."
    ck_exists "${_p_url}"
#    if ! v=$(ck_version "${EXPECTED}" "${_p_url}"); then
#       print_RED "FAIL: ${p}-${o} ${v} is not ${EXPECTED}"
#    else
#       print_GREEN "OK!"
#    fi
    echo ""
  done
done

for p in ${WIN_PRODUCT[*]}; do
  for o in ${PLAT_WIN[*]}; do
    _p_url=$(build_url $p $o)
    echo "Checking ${p} ${o}..."
    ck_exists "${_p_url}"    
#   if ! v=$(ck_version "${EXPECTED}" "${_p_url}"); then
#       print_RED "FAIL: ${p}-${o} is not ${EXPECTED}"
#    else
#       print_GREEN "OK!"
#    fi
    echo ""
  done
done

for p in ${OSX_PRODUCT[*]}; do
  for o in ${PLAT_OSX[*]}; do
    _p_url=$(build_url $p $o)
    echo "Checking ${p} ${o}..."
    ck_exists "${_p_url}"    
#   if ! v=$(ck_version "${EXPECTED}" "${_p_url}"); then
#       print_RED "FAIL: ${p}-${o} is not ${EXPECTED}"
#    else
#       print_GREEN "OK!"
#    fi
#    echo ""
  done
done
