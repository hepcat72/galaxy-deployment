#!/usr/bin/env bash

psql -U galaxy -p 5431 -c "select * from galaxy_user;" -t > user_data.txt


