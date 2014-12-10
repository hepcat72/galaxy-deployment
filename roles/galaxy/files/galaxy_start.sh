#!/bin/sh
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set GALAXY_RUN_ALL to start all web and handler processes defined
export GALAXY_RUN_ALL=1
PATH="/usr/local/bin:/usr/local/galaxy_dependencies/bedtools/2.16.2/bin:${PATH}"

# Start Galaxy web and handler processes
/bin/sh "${DIR}/run.sh" --daemon

# Set 503 to outage (should not be displayed unless there is a problem)
# TODO wait for server to start before this
ln -sf "${DIR}/../www/html/error-documents/503_outage.html" "${DIR}/../www/html/error-documents/503.html"

# Start Galaxy Reports web application
/bin/sh "${DIR}/run_reports.sh" --daemon
