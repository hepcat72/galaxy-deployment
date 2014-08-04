#!/usr/bin/env bash

psql -U galaxy -p 5431 -c "select email from galaxy_user where deleted = 'f';" -t | sed 's/@princeton.edu//'
