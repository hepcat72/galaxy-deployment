#!/bin/bash
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set GALAXY_RUN_ALL to start all web and handler processes defined
export GALAXY_RUN_ALL=1

# Start Galaxy web and handler processes
/bin/sh "${DIR}/run.sh" --stop-daemon

# Start Galaxy Reports web application
/bin/sh "${DIR}/run_reports.sh" --stop-daemon
