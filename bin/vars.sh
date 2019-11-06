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
EMAIL_USER="commtech-commons"
EMAIL_MAILBOX="alerts"
EMAIL_SERVER="tools.wmflabs.org"
ERROR_EMAIL="${EMAIL_USER}.${EMAIL_MAILBOX}@${EMAIL_SERVER}"
ERROR_LINES=30


handle_error() {
    echo "Cronjob ${TIMESTAMP} failed at $(date)"
    echo "Emailing the maintainers"
    jsub -quiet -once ${DIR}/bin/report-error
    exit 1
}

trap "handle_error" ERR
