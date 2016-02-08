#!/bin/bash
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set GALAXY_RUN_ALL to start all web and handler processes defined
export GALAXY_RUN_ALL=1
PATH="/usr/local/bin:/usr/local/galaxy_dependencies/bedtools/2.16.2/bin:${PATH}"

# Set Python Egg Cache directory to one writable by the cluster nodes
export PYTHON_EGG_CACHE=/tmp/.python-eggs

# Set TMPDIR
if [ -d /scratch/tmp ];
then
    export TMPDIR="/scratch/tmp";
fi

# Start Galaxy web and handler processes
/bin/sh "${DIR}/run.sh" --daemon

# Start Galaxy Reports web application
/bin/sh "${DIR}/run_reports.sh" --daemon
