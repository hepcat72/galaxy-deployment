#!/usr/bin/env bash

psql -U galaxy -p 5431 -c "select email from galaxy_user where deleted = 'f';" -t | grep -v "igv_display\|ucsc_browser_display@example.org\|remote_display_server@princeton.edu"
