#!/usr/bin/env python
""" Append genome info to loc files using genome_build_info.txt files
"""

__version__ = "0.2"
__author__ = "Lance Parsons"
__author_email__ = "lparsons@princeton.edu"
__copyright__ = "Copyright 2011, Lance Parsons"
__license__ = "Public Domain"


import sys
import os
import optparse
import glob
import csv
import re
from string import Template


def read_genome_info(genome_info_file):
    ''' Read Genome Info File and return dictionary '''
    genome_info = {}
    genomeInfoReader = csv.reader(open(genome_info_file, 'rb'), delimiter='\t')
    for line in genomeInfoReader:
        genome_info[line[0]] = line[1]
    genome_file_abs_path = os.path.abspath(genome_info_file)
    genome_abs_path = os.path.dirname(genome_file_abs_path)
    genome_info['genome_directory'] = genome_abs_path
    return genome_info


def igenome_info(genome_dir, builds_file):
    ''' Determine genome info from igenome directory and return dictionary '''
    genome_info = {}
    genome_abs_path = os.path.abspath(genome_dir)
    genome_info['genome_directory'] = genome_abs_path
    if os.path.exists(os.path.join(genome_abs_path, 'Sequence')):
        print("Attempting to parse as iGenome directory")

        genome_info['type'] = 'iGenome'

        genome_info['organism'] = os.path.basename(
            os.path.abspath(os.path.join(genome_abs_path, '..', '..')))
        organism = raw_input('Organism [%s] ' % genome_info['organism'])
        if organism != '':
            genome_info['organism'] = organism

        genome_info['version'] = os.path.basename(genome_abs_path)
        version = raw_input('Version [%s] ' % genome_info['version'])
        if version != '':
            genome_info['version'] = version

        genome_info['dbkey'] = os.path.basename(genome_abs_path)
        dbkey = raw_input('Galaxy DBKey [%s] ' % genome_info['dbkey'])
        if dbkey != '':
            genome_info['dbkey'] = dbkey

        genome_info['source'] = os.path.basename(
            os.path.abspath(os.path.join(genome_abs_path, '..')))
        source = raw_input('Source [%s] ' % genome_info['source'])
        if source != '':
            genome_info['source'] = source

        build_info = dbkey_in_locfile(genome_info['dbkey'], builds_file)
        if build_info:
            genome_info['display_name'] = build_info[1]
        else:
            genome_info['display_name'] = ('%s (%s) (%s)' %
                                           (genome_info['organism'],
                                            genome_info['source'],
                                            genome_info['dbkey']))
        display_name = raw_input('Display Name [%s] ' %
                                 genome_info['display_name'])
        if display_name != '':
            genome_info['display_name'] = display_name

    return genome_info


def data_locations(genome_info):
    if ('type' in genome_info) and (genome_info['type'] == 'iGenome'):
        data_locations = {
            'BOWTIE': os.path.join(genome_info['genome_directory'],
                                   'Sequence', 'BowtieIndex'),
            'BOWTIE2': os.path.join(genome_info['genome_directory'],
                                    'Sequence', 'Bowtie2Index'),
            'BWA': os.path.join(genome_info['genome_directory'], 'Sequence',
                                'BWAIndex', 'version0.5.x'),
            'SAM_FA': os.path.join(genome_info['genome_directory'],
                                   'Sequence', 'WholeGenomeFasta'),
            'ALL_FASTA': os.path.join(genome_info['genome_directory'],
                                      'Sequence', 'WholeGenomeFasta'),
            'FASTA_INDEXES': os.path.join(genome_info['genome_directory'],
                                          'Sequence', 'WholeGenomeFasta'),
            'CODING_SNPS': None,
            'SRMA_INDEX': os.path.join(genome_info['genome_directory'],
                                       'Sequence', 'WholeGenomeFasta'),
            'PICARD_INDEX': os.path.join(genome_info['genome_directory'],
                                         'Sequence', 'WholeGenomeFasta'),
            'GATK_SORTED_PICARD_INDEX':
                os.path.join(genome_info['genome_directory'],
                             'Sequence', 'WholeGenomeFasta'),
            'MANUAL_BUILD': os.path.join(genome_info['genome_directory'],
                                         'Sequence', 'WholeGenomeFasta')}
    else:
        base_dir = os.path.basename(genome_info['genome_directory'])
        base_dir = os.path.join(genome_info['genome_directory'], base_dir)
        data_locations = {
            'BOWTIE': '%s_BOWTIE' % base_dir,
            'BOWTIE2': '%s_BOWTIE2' % base_dir,
            'BWA': '%s_BWA' % base_dir,
            'SAM_FA': '%s_FASTA' % base_dir,
            'ALL_FASTA': '%s_FASTA' % base_dir,
            'FASTA_INDEXES': '%s_FASTA' % base_dir,
            'CODING_SNPS': '%s_2BIT' % base_dir,
            'SRMA_INDEX': '%s_FASTA' % base_dir,
            'PICARD_INDEX': '%s_FASTA' % base_dir,
            'GATK_SORTED_PICARD_INDEX': '%s_FASTA' % base_dir,
            'MANUAL_BUILD': '%s_FASTA' % base_dir}

    return data_locations


def dbkey_in_locfile(dbkey, locfile):
    '''Return true if dbkey exists in locfile'''
    locfileReader = csv.reader(open(locfile, 'rb'), delimiter='\t')
    for line in locfileReader:
        if len(line) > 0 and line[0][0] != '#':
            if dbkey in line:
                return line
    return False


def update_manual_builds_file(manual_builds_file, builds_file, genome_info):
    ''' Append info to manual builds file if dbkey is new
    arguments:
        manual_builds_file - full path and filename to builds file
        genome_directory - base directory for genome info
        '''

    try:
        build_line = build_manual_build_string(genome_info)

        if (build_line is None):
            print ("Skipping update of %s, could not build genome info line" %
                   os.path.basename(manual_builds_file))
        else:
            print build_line.rstrip()

            if dbkey_in_locfile(genome_info['dbkey'], manual_builds_file):
                print("Skipping, found %s in %s" % (genome_info['dbkey'],
                      os.path.basename(manual_builds_file)))
            elif dbkey_in_locfile(genome_info['dbkey'], builds_file):
                print("Skipping, found %s in %s" % (genome_info['dbkey'],
                      os.path.basename(builds_file)))
            else:
                print("Appending %s to %s" % (genome_info['dbkey'],
                      os.path.basename(manual_builds_file)))
                build_file_obj = open(manual_builds_file, 'ab')
                build_file_obj .write(build_line)
                GALAXY_HOME = os.path.abspath(os.path.join(
                    os.path.realpath(__file__), '..', '..', '..'))
                add_builds_command = Template(
                    "cd ${GALAXY_HOME}\n\tpython cron/add_manual_builds.py "
                    "tool-data/shared/ucsc/manual_builds.txt "
                    "tool-data/shared/ucsc/builds.txt "
                    "tool-data/shared/ucsc/chrom/").substitute(
                    dict(GALAXY_HOME=GALAXY_HOME))
                print("\nYou should now run the following command to add the "
                      "manual builds:\n\t%s" % add_builds_command)
                print("\nAlternatively, you can update the list of builds "
                      "from ucsc and incorporate the manual builds with:\n"
                      "\tcron/updateucsc.sh")

    except IOError as e:
        print("Skipping update of %s:" %
              os.path.basename(manual_builds_file), e)


def build_manual_build_string(genome_info):
    ''' Return string for manual builds file for specified genome info
    arguments:
        genome_info - dictionary with values for
            organism, version, dbkey, source,
        '''
    # <dbkey>   <display_name>  <chrom_len_list>
    result = None
    fasta_dir = data_locations(genome_info)['ALL_FASTA']
    # genome_directory = genome_info['genome_directory']
    # base_dir = os.path.basename(genome_directory)
    # fasta_dir = os.path.join(genome_directory, '%s_FASTA' % base_dir)

    # Get FAI file
    glob_text = os.path.join(fasta_dir, '*.fai')
    files = glob.glob(glob_text)
    if len(files) != 1:
        raise IOError("Unable to find .fai file, searched for %s" % glob_text)
    chrom_list = build_chrom_string(files[0])
    p = re.compile(r" \("+genome_info['dbkey']+r"\)")
    short_display_name = p.sub('', genome_info['display_name'])
    result = "%s\t%s\t%s\n" % (genome_info['dbkey'],
                               short_display_name,
                               chrom_list)
    return result


def build_chrom_string(fai_file):
    '''Build string of name=len,name=len,etc.'''
    chrom_list = []
    faiReader = csv.reader(open(fai_file, 'rb'), delimiter='\t')
    for line in faiReader:
        chrom_list.append("%s=%s" % (line[0], line[1]))
    chrom_string = ','.join(chrom_list)
    return chrom_string


def update_locfile(locfile, genome_info, type):
    ''' Append Info To Locfile if dbkey is new
    arguments:
        locfile - full path and filename to locfile to append to
        genome_directory - base directory for genome info
        type - type of locfile (bowtie, bwa, fasta, etc.)
        '''

    try:
        genome_directory = genome_info['genome_directory']

        locfile_line = build_locfile_string(genome_info, genome_directory,
                                            type)
        if (locfile_line is None):
            print ("Skipping update of %s, could not build genome info line" %
                   os.path.basename(locfile))
        else:
            print locfile_line.rstrip()

            if dbkey_in_locfile(genome_info['dbkey'], locfile):
                print("Skipping, found %s in %s" %
                      (genome_info['dbkey'], os.path.basename(locfile)))
            else:
                print("Appending %s to %s" % (genome_info['dbkey'],
                                              os.path.basename(locfile)))
                locfile_obj = open(locfile, 'ab')
                locfile_obj.write(locfile_line)
    except IOError as e:
        print "Skipping update of %s:" % os.path.basename(locfile), e


def build_picard_index_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['PICARD_INDEX']
    # base_dir = "%s_FASTA" % base_dir
    glob_text = os.path.join(base_dir, '*.dict')
    files = glob.glob(glob_text)
    result = None
    if len(files) != 1:
        raise IOError("Could not find dict file (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(files[0])[0]
        fasta_file = "%s.fasta" % file_base_path
        if (not os.path.exists(fasta_file)):
            fasta_file = "%s.fa" % file_base_path
        if (os.path.exists(fasta_file)):
            result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                           genome_info['dbkey'],
                                           genome_info['display_name'],
                                           fasta_file)
        else:
            result = None
    return result


def build_coding_snps_locfile_string(genome_info, base_dir):
    # <build>        <file_path>
    base_dir = data_locations(genome_info)['CODING_SNPS']
    # base_dir = "%s_2BIT" % base_dir
    result = None
    if base_dir:
        glob_text = os.path.join(base_dir, '*.2bit')
        files = glob.glob(glob_text)
        if len(files) != 1:
            raise IOError("Could not find 2bit file (searching for '%s' "
                          "returned %s results)" % (glob_text, len(files)))
        else:
            file_base_path = files[0]
            result = "%s\t%s\n" % (genome_info['dbkey'], file_base_path)
    return result


def build_all_fasta_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['ALL_FASTA']
    # base_dir = "%s_FASTA" % base_dir
    glob_text = os.path.join(base_dir, '*.fai')
    files = glob.glob(glob_text)
    result = None
    if len(files) != 1:
        raise IOError("Could not find fai file (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(files[0])[0]
        result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                       genome_info['dbkey'],
                                       genome_info['display_name'],
                                       file_base_path)
    return result


def build_fasta_indexes_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['FASTA_INDEXES']
    glob_text = os.path.join(base_dir, '*.fai')
    files = glob.glob(glob_text)
    result = None
    if len(files) != 1:
        raise IOError("Could not find fai file (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(files[0])[0]
        result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                       genome_info['dbkey'],
                                       genome_info['display_name'],
                                       file_base_path)
    return result


def build_sam_fa_locfile_string(genome_info, base_dir):
    # index  <seq>   <location>
    base_dir = data_locations(genome_info)['ALL_FASTA']
    # base_dir = "%s_FASTA" % base_dir
    glob_text = os.path.join(base_dir, '*.fai')
    files = glob.glob(glob_text)
    result = None
    if len(files) != 1:
        raise IOError("Could not find fai file (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(files[0])[0]
        result = "index\t%s\t%s\n" % (genome_info['dbkey'],
                                      file_base_path)
    return result


def build_bwa_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['BWA']
    # base_dir = "%s_BWA" % base_dir
    glob_text = os.path.join(base_dir, '*.bwt')
    files = glob.glob(glob_text)
    result = None
    if len(files) < 1:
        raise IOError("Could not find bwt files (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(files[0])[0]
        result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                       genome_info['dbkey'],
                                       genome_info['display_name'],
                                       file_base_path)
    return result


def build_bowtie_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['BOWTIE']
    # base_dir = "%s_BOWTIE" % base_dir
    glob_text = os.path.join(base_dir, '*.1.ebwt')
    files = glob.glob(glob_text)
    result = None
    if len(files) < 1:
        raise IOError("Could not find ebwt files (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(os.path.splitext(files[0])[0])[0]
        result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                       genome_info['dbkey'],
                                       genome_info['display_name'],
                                       file_base_path)
    return result


def build_bowtie2_locfile_string(genome_info, base_dir):
    # <unique_build_id>   <dbkey>   <display_name>   <file_base_path>
    base_dir = data_locations(genome_info)['BOWTIE2']
    # base_dir = "%s_BOWTIE2" % base_dir
    glob_text = os.path.join(base_dir, '*.1.bt2')
    files = glob.glob(glob_text)
    result = None
    if len(files) < 1:
        raise IOError("Could not find bt2 files (searching for '%s' returned "
                      "%s results)" % (glob_text, len(files)))
    else:
        file_base_path = os.path.splitext(os.path.splitext(files[0])[0])[0]
        result = "%s\t%s\t%s\t%s\n" % (genome_info['dbkey'],
                                       genome_info['dbkey'],
                                       genome_info['display_name'],
                                       file_base_path)
    return result


def build_locfile_string(genome_info, directory, type):
    ''' Return string for given locfile type

    arguments:
        genome_info - dictionary with values for
            organism, version, dbkey, source, and display_name
        type - type of locfile (bowtie, bwa, fasta, etc.)
        '''
    result = None
    base_dir = os.path.basename(directory)
    base_dir = os.path.join(directory, base_dir)
    type = type.lower()
    if type == 'bowtie':
        result = build_bowtie_locfile_string(genome_info, base_dir)
    elif type == 'bowtie2':
        result = build_bowtie2_locfile_string(genome_info, base_dir)
    elif type == 'bwa':
        result = build_bwa_locfile_string(genome_info, base_dir)
    elif type == 'sam_fa':
        result = build_sam_fa_locfile_string(genome_info, base_dir)
    elif type == 'all_fasta':
        result = build_all_fasta_locfile_string(genome_info, base_dir)
    elif type == 'fasta_indexes':
        result = build_fasta_indexes_locfile_string(genome_info, base_dir)
    elif type == 'coding_snps':
        result = build_coding_snps_locfile_string(genome_info, base_dir)
    elif type == 'srma_index':
        result = build_picard_index_locfile_string(genome_info, base_dir)
    elif type == 'picard_index':
        result = build_picard_index_locfile_string(genome_info, base_dir)
    elif type == 'gatk_sorted_picard_index':
        result = build_picard_index_locfile_string(genome_info, base_dir)
    else:
        raise Exception("Unknown loc file type: %s" % type)
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv

    usage = "Usage: %prog [options] genome_directory"
    parser = optparse.OptionParser(usage=usage, version='%prog version ' +
                                   globals()['__version__'],
                                   description=globals()['__doc__'])
    parser.add_option('--tooldatadir',
                      default=os.path.abspath(os.path.join(
                          os.path.realpath(__file__),
                          '..', '..', '..', 'tool-data')),
                      help='Galaxy Tool Data Directory')
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      help='verbose output')
    try:
        (options, args) = parser.parse_args(argv[1:])
        if len(args) < 1:
            parser.error('Genome Directory Not Specified')
    except SystemExit:  # Prevent exit when calling as function
        return 2

    genome_directory = os.path.abspath(args[0])
    genome_info_file = os.path.join(genome_directory, 'genome_build_info.txt')
    manual_builds_file_relpath = os.path.join("shared", "ucsc",
                                              "manual_builds.txt")
    manual_builds_file = os.path.join(os.path.abspath(options.tooldatadir),
                                      manual_builds_file_relpath)
    builds_file_relpath = os.path.join("shared", "ucsc", "builds.txt")
    builds_file = os.path.join(os.path.abspath(options.tooldatadir),
                               builds_file_relpath)
    try:
        genome_info = read_genome_info(genome_info_file)
        print "\nGenome Info:\n%s" % genome_info
    except IOError as e:
        print("Unable to read genome info from %s\n%s\n" %
              (genome_info_file, e))
        genome_info = igenome_info(genome_directory, builds_file)
        print genome_info
        if 'organism' not in genome_info:
            print "Does not appear to be an iGenome directory"
            return(2)

    # List of loc files and corresponding directory suffix
    loc_files = {'BOWTIE': 'bowtie_indices.loc',
                 'BOWTIE2': 'bowtie2_indices.loc',
                 'BWA': 'bwa_index.loc',
                 'SAM_FA': 'sam_fa_indices.loc',
                 'ALL_FASTA': 'all_fasta.loc',
                 'FASTA_INDEXES': 'fasta_indexes.loc',
                 'CODING_SNPS': 'codingSnps.loc',
                 'SRMA_INDEX': 'srma_index.loc',
                 'PICARD_INDEX': 'picard_index.loc',
                 'GATK_SORTED_PICARD_INDEX': 'gatk_sorted_picard_index.loc'}
    # Update individual loc files
    for type, loc_file in loc_files.iteritems():
        print "\n%s" % loc_file
        loc_file_fullpath = os.path.join(os.path.abspath(options.tooldatadir),
                                         loc_file)
        update_locfile(loc_file_fullpath, genome_info, type)

    # Update manual_builds.txt file
    print "\n%s" % manual_builds_file_relpath
    update_manual_builds_file(manual_builds_file, builds_file, genome_info)

    return 1


if __name__ == '__main__':
    sys.exit(main())
