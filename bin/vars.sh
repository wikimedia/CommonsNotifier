#!/bin/bash

# This file sets up some common variables for other scripts in this directory

set -e

USER=s53689
DB=${USER}__commonsbot
DIR=$(dirname "$(dirname "$(test -L "$0" && readlink "$0" || echo "$0")")")
BIN="${DIR}/virtualenv/bin"
TIMESTAMP=$(date '+%Y%m%d%H%M%S')
