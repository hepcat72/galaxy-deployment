#!/usr/bin/env python
"""
SYNOPSIS

    fastx_barcode_splitter_index_reads --readsfile FILE --idxfile FILE
        --bcfile FILE --prefix PREFIX [--suffix SUFFIX] [--mismatches N] 
        [--exact] [--partial N] [--quiet] [--debug]
        [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    Wrapper to fastx_barcode_splitter that allows one to use separate index reads.
    Prepends reads with barcode read from separate index read fastq file.

EXAMPLES

    fastx_barcode_splitter_index_reads -r reads.fq -i index_reads.fq 
        --bcfile barcodes.txt --prefix /tmp/foo_ --suffix ".txt"


EXIT STATUS

    TODO: List exit codes

AUTHOR

    Lance Parsons <lparsons@princeton.edu>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.

VERSION

    $Id$
"""

#This Python script requires Biopython 1.51 or later
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from subprocess import Popen, PIPE
import itertools
import optparse
import os
import re
import sys
import time
import traceback
#from pexpect import run, spawn


def main ():

    global options, args
    count = 0
    
    r_iter = FastqGeneralIterator(open(options.readsfile, "rU"))
    i_iter = FastqGeneralIterator(open(options.idxfile, "rU"))
    search = re.compile(r"(.*)(/[12])")
    replace = r"\1"
    
    args = ['fastx_barcode_splitter.pl', '--bcfile', options.bcfile, \
               '--prefix', options.prefix, '--bol', \
               '--mismatches', str(options.mismatches)]
    if (options.suffix): args.extend(['--suffix', options.suffix])
    if (options.exact): args.append('--exact')
    if (options.partial): args.extend(['--partial', str(options.partial)])
    if (options.quiet): args.append('--quiet')
    if (options.debug): args.append('--debug')
    if options.verbose: print "\nUsing args: %s\n" % args
    p = Popen(args, stdout=PIPE, stdin=PIPE)
    for (r_id, r_seq, r_q), (i_id, i_seq, i_q) \
    in itertools.izip(r_iter, i_iter):
        r_id_strip = re.sub(search, replace, r_id)
        i_id_strip = re.sub(search, replace, i_id)
        assert r_id_strip == i_id_strip
        count += 1
        
        #Write out both reads with "/1+2" suffix on ID
        p.stdin.write("@%s/1+2\n%s%s\n+\n%s%s\n" \
                 % (r_id_strip, i_seq, r_seq, i_q, r_q))
#        print("@%s/1+2\n%s%s\n+\n%s%s\n" \
#                 % (r_id_strip, i_seq, r_seq, i_q, r_q))
    output = p.communicate()[0]
    print output


if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='$Id$')
        parser.add_option ('-r', '--readsfile', action='store', type="string", dest="readsfile", metavar="FILE", help='Fastq file containing reads to be sorted.')
        parser.add_option ('-i', '--idxfile', action='store', type="string", dest="idxfile", metavar="FILE", help='Fastq file containing index reads (barcodes).')
        parser.add_option ('-b', '--bcfile', action='store', type="string", dest="bcfile", metavar="FILE", help='Tab delimited file with identifiers and barcode sequences.')
        parser.add_option ('-p', '--prefix', action='store', type="string", dest="prefix", metavar="PREFIX", help='File prefix. Will be added to the output files. Can be used to specify output directories.')
        parser.add_option ('-s', '--suffix', action='store', type="string", dest="suffix", metavar="SUFFIX", help='File suffix (optional). Can be used to specify file extensions.')
        parser.add_option ('-m', '--mismatches', action='store', type="int", dest="mismatches", metavar="N", default=1, help='Max. number of mismatches allowed. default is 1.')
        parser.add_option ('-e', '--exact', action='store_true', dest="exact", default=False, help="Same as '--mismatches 0'. If both --exact and --mismatches are specified, '--exact' takes precedence.")
        parser.add_option ('-t', '--partial', action='store', type="int", dest="partial", metavar="N", help='Allow partial overlap of barcodes. (see explanation below.) (Default is not partial matching)')
        parser.add_option ('-q', '--quiet', action='store_true', default=False, help="Don't print counts and summary at the end of the run. (Default is to print.)")
        parser.add_option ('-d', '--debug', action='store_true', default=False, help='Print lots of useless debug information to STDERR.')
        parser.add_option ('-v', '--verbose', action='store_true', default=False, help='verbose output')
        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
        if options.verbose: print time.asctime()
        main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)

