#!/bin/sh
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set 503 to maintenance
ln -sf "${DIR}/../www/html/error-documents/503_scheduled_maintenance.html" "${DIR}/../www/html/error-documents/503.html"

# Set GALAXY_RUN_ALL to start all web and handler processes defined
export GALAXY_RUN_ALL=1

# Start Galaxy web and handler processes
/bin/sh "${DIR}/run.sh" --stop-daemon

# Start Galaxy Reports web application
/bin/sh "${DIR}/run_reports.sh" --stop-daemon
