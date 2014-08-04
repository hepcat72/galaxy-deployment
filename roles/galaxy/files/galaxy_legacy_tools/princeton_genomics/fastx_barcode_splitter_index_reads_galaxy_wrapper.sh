#!/bin/bash

#    FASTX-toolkit - FASTA/FASTQ preprocessing tools.
#    Copyright (C) 2009  A. Gordon (gordon@cshl.edu)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  Modified by Lance Parsons (lparsons@princeton.edu)
#	2011-03-15	Adapt for use with index read files
#
#This is a shell script wrapper for 'fastx_barcode_splitter_index_reads.py'
#
# 1. Output files are saved at the dataset's files_path directory.
#    
# 2. 'fastx_barcode_splitter.pl' outputs a textual table.
#    This script turns it into pretty HTML with working URL
#    (so lazy users can just click on the URLs and get their files)

BARCODE_FILE="$1"
FASTQ_FILE="$2"
INDEX_FILE="$3"
LIBNAME="$4"
OUTPUT_PATH="$5"
shift 5
# The rest of the parameters are passed to the split program

if [ "$OUTPUT_PATH" == "" ]; then
	echo "Usage: $0 [BARCODE FILE] [FASTQ FILE] [INDEX_FILE] [LIBRARY_NAME] [OUTPUT_PATH]" >&2
	exit 1
fi

#Sanitize library name, make sure we can create a file with this name
LIBNAME=${LIBNAME//\.gz/}
LIBNAME=${LIBNAME//\.txt/}
LIBNAME=${LIBNAME//[^[:alnum:]]/_}

if [ ! -r "$FASTQ_FILE" ]; then
	echo "Error: Input file ($FASTQ_FILE) not found!" >&2
	exit 1
fi
if [ ! -r "$INDEX_FILE" ]; then
	echo "Error: Input file ($INDEX_FILE) not found!" >&2
	exit 1
fi
if [ ! -r "$BARCODE_FILE" ]; then
	echo "Error: barcode file ($BARCODE_FILE) not found!" >&2
	exit 1
fi
mkdir -p "$OUTPUT_PATH"
if [ ! -d "$OUTPUT_PATH" ]; then
	echo "Error: failed to create output path '$OUTPUT_PATH'" >&2
	exit 1
fi

PUBLICURL=""
BASEPATH="$OUTPUT_PATH/"
#PREFIX="$BASEPATH"`date "+%Y-%m-%d_%H%M__"`"${LIBNAME}__"
PREFIX="$BASEPATH""${LIBNAME}_"
SUFFIX="_visible_fastq"
DIRECTORY=$(cd `dirname $0` && pwd)

RESULTS=`$DIRECTORY/fastx_barcode_splitter_index_reads.py --readsfile "$FASTQ_FILE" --idxfile "$INDEX_FILE" --bcfile "$BARCODE_FILE" --prefix "$PREFIX" --suffix "$SUFFIX" "$@"`
if [ $? != 0 ]; then
	echo "error"
fi

#
# Convert the textual tab-separated table into simple HTML table,
# with the local path replaces with a valid URL
#HTMLSUMMARY=${PREFIX}stats_visible_html
echo "<html><body><table border=1>" 
echo "$RESULTS" | sed -r "s|$BASEPATH(.*)|\\1|" | sed '
i<tr><td>
s|\t|</td><td>|g
a<\/td><\/tr>
' 
echo "<p>" 
echo "</table></body></html>" 
