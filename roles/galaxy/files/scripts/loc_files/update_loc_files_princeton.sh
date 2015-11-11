#!/bin/bash

# Run update_loc_file_princeton.py for each reference genome that contains a
# genome_build_info.txt file
##############################################################################


usage() { echo "Usage: $0 [-v] REFERENCE_DIRECTORY"; exit 1; }

options=""
while getopts ":v" opt; do
    case $opt in
        v)
            options="$options --verbose"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

shift $((OPTIND-1))

while [ "${1+defined}" ]; do
    REF_DIR=$1
    shift
done
if [ ! -d "$REF_DIR" ]; then
    echo "Reference directory required"
    usage
fi


# Get directory of script
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run process_reference_fasta.pl on each existing genome_build_info.txt file
file_list=()
while IFS= read -d $'\0' -r file ; do
    file_list=("${file_list[@]}" "$file")
done < <(find "$REF_DIR" -not \( -path "$REF_DIR/.snapshot" -prune \) -name "genome_build_info.txt" -print0)

for file in "${file_list[@]}"; do
    directory="$(dirname "$file")"
    cmd="python \"$DIR/update_loc_files_princeton.py\"$options \"$directory\""
    echo "$cmd"
    eval "$cmd"
    if [ $? -ne 0 ]; then
        printf "\nUnexpected error occured processing '%s'\n" "$directory"
        read -r -p "Press [Enter] key to continue..."
    fi
done

printf "\nUpdating manual builds\n"
GALAXY_DIR="$(dirname "$(dirname "$DIR")")"
update_manual_builds_cmd="python \"$GALAXY_DIR/cron/add_manual_builds.py\" \"$GALAXY_DIR/tool-data/shared/ucsc/manual_builds.txt\" \"$GALAXY_DIR/tool-data/shared/ucsc/builds.txt\" \"$GALAXY_DIR/tool-data/shared/ucsc/chrom/\""
echo "$update_manual_builds_cmd"
eval "$update_manual_builds_cmd"
