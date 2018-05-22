#!/bin/bash

# This file sets up some common variables for other scripts in this directory

set -e

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

USER=s53689
DB=${USER}__commonsbot
DIR=$(dirname "$(dirname "$(test -L "$0" && readlink "$0" || echo "$0")")")
BIN="${DIR}/virtualenv/bin"
TIMESTAMP=$(date '+%Y%m%d%H%M%S')
