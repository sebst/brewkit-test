#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset


readonly PANTRY_TGZ_URL="https://dist.pkgx.dev/pantry.tgz"
readonly DATE_NOW=$(date +"%Y%m%d")

readonly SCRIPT_DIR=$(dirname $(realpath $0))
readonly PANTRY_DIR="${SCRIPT_DIR}/pantry"
readonly PANTRY_DIR_PKGX="${PANTRY_DIR}/pkgx.dev"

echo "PANTRY_DIR_PKGX: ${PANTRY_DIR_PKGX}"

rm -rf "${PANTRY_DIR_PKGX}"
mkdir -p "${PANTRY_DIR_PKGX}"


# Download PANTRY_TGZ_URL and extract everything under projects/ in the tgx to PANTRY_DIR_PKGX
curl -sL "$PANTRY_TGZ_URL" | tar -xz -C "$PANTRY_DIR_PKGX" --strip-components=1 --wildcards '*/projects/*'
