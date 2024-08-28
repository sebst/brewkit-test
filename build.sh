#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

export BREWROOT="$HOME/.local/share/brewkit"

readonly PACKAGE=$1
readonly VERSION=$2
readonly ARCH=`uname -m`

pkgx bk build ${PACKAGE}=v${VERSION}
# pkgx bk test ${PACKAGE}=v${VERSION}


# Normalize ARCH to "x86-64" or "aarch64"
if [ "$ARCH" = "x86_64" ]; then
    BK_ARCH="x86-64"
elif [ "$ARCH" = "aarch64" ]; then
    BK_ARCH="aarch64"
fi


readonly PACKAGE_DIR="/home/vscode/.pkgx/${PACKAGE}/v${VERSION}/"
readonly PACKAGE_DST="/mnt/"
readonly PACKAGE_TAR_BALL_NAME="${PACKAGE}-${VERSION}_${ARCH}.tar.gz"

# Create a .tar.gz file from PACKAGE_DIR and store it to PACKAGE_DST/PACKAGE_TAR_BALL_NAME
tar -czf "${PACKAGE_DST}/${PACKAGE_TAR_BALL_NAME}" -C "${PACKAGE_DIR}" .

