#!/usr/bin/env python

"""
Runs FastQC on a fastq file;
TODO: more documentation

usage: fastqc.py [options]
    -i, --input=i: The fastq input file
    -n, --name=n: The fastq input name
    -c, --contaminants=c: A contaminants file
    -r, --report=r: The html summary report file
    -D, --dir=D: The dir for report files
    -d, --data=d: The data output text file
"""

import optparse, os, shutil, subprocess, sys, tempfile, re, string

def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def __main__():
    #Parse Command Line
    parser = optparse.OptionParser()
    parser.add_option( '-i', '--input', dest='input', help='The sequence input file' )
    parser.add_option( '-f', '--format', dest='format', help='The sequence input file format' )
    parser.add_option( '-n', '--name', dest='name', help='The fastq input name' )
    parser.add_option( '-c', '--contaminants', dest='contaminants', help='A contaminants file' )
    parser.add_option( '-r', '--report', dest='report', help='The HTML report' )
    parser.add_option( '-D', '--dir', dest='outdir', help='The dir for report files' )
    parser.add_option( '-d', '--data', dest='data', help='The output data text file' )
    (options, args) = parser.parse_args()
    if options.input == None:
       stop_err("Misssing option --input")
    params = []
    #params.append('-Xmx250m')
    params.append('-Djava.awt.headless=true')
    name = 'input'
    format = 'fastq'
    if options.outdir != None:
        os.makedirs(options.outdir)
    if options.contaminants != None and options.contaminants != 'None':
        params.append("-c %s" % options.contaminants)
    if options.name != None and options.name != 'None':
       name = re.sub('[^a-zA-Z0-9_.-]','_',options.name)
    if options.format != None and options.format != 'None':
        format = options.format
        params.append("-f %s" % options.format)
    # FastQC relies on the extension to determine file format .sam .bam or .fastq
    if not name.endswith('.'+format):
        name = '.'.join((name,format))
    # make temp directory
    buffsize = 1048576
    tmp_dir = tempfile.mkdtemp()
    params.append("-o %s" % tmp_dir)
    # print("tmp_dir %s" % tmp_dir)
    try:
        # make a link to the input fastq in the tmp_dir
        # FastQC will generate output in the same dir that it finds its input
        fastq = os.path.join(tmp_dir,name) 
        os.symlink( options.input, fastq)
        # generate commandline
        cmd = 'fastqc %s %s' % (' '.join(params),fastq)
        # need to nest try-except in try-finally to handle 2.4
        try:
            try:
                tmp_stderr_name = tempfile.NamedTemporaryFile( dir=tmp_dir,suffix='.err' ).name
                tmp_stderr = open( tmp_stderr_name, 'wb' )
                tmp_stdout_name = tempfile.NamedTemporaryFile( dir=tmp_dir,suffix='.out' ).name
                tmp_stdout = open( tmp_stdout_name, 'wb' )
                proc = subprocess.Popen( args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno(), stdout=tmp_stdout.fileno() )
                returncode = proc.wait()
                tmp_stderr.close()
                # get stderr, allowing for case where it's very large
                tmp_stderr = open( tmp_stderr_name, 'rb' )
                stderr = ''
                try:
                    while True:
                        stderr += tmp_stderr.read( buffsize )
                        if not stderr or len( stderr ) % buffsize != 0:
                            break
                except OverflowError:
                    pass
                tmp_stderr.close()
                if returncode != 0:
                    raise Exception, stderr
            except Exception, e:
                raise Exception, 'Error executing FastQC. ' + str( e )
            # remove the input file symlink so it does get copied
            os.remove(fastq)
            # remove the stdout and stderr files so they do not get copied
            os.remove(tmp_stderr_name)
            os.remove(tmp_stdout_name)
            # array to retrieve results of each test so that it gets displayed in the tool info 
            tests = []
            # move result to outdir 
            # Need to flatten the dir hierachy in order for galaxy to serve the href links
            for root, dirs, files in os.walk(tmp_dir):
                for fname in files:
                    path = os.path.join(root,fname)
                    # print("%s" % fname)
                    if re.match('.+\.zip',fname):
                        pass
                    elif fname == 'fastqc_report.html':
                        if options.outdir != None:
                            fsrc = open(path,'r')
                            # fdst = open(os.path.join(options.outdir,fname),'w')
                            fdst = open(options.report,'w')
                            try:
                                for line in fsrc:
                                    if line.find('footer') > 0:
                                        # add extra links in case someone prefers raw text
                                        fdst.write('<p><a href="summary.txt">FastQC Summary text report</a>')
                                        fdst.write('<p><a href="fastqc_data.txt">FastQC Report Data</a>')
                                    # copy lines removing subdirs from links
                                    fdst.write(re.sub('Icons/|Images/','',line))
                            finally:
                                fsrc.close()
                                fdst.close() 
                    else:
                        if options.outdir != None:
                            shutil.copy(path,options.outdir)
                        if fname == 'summary.txt':
                            # Use the contents of this file to put stdout info into the HistoryDataset panel
                            fsrc = open(path,'r')
                            try:
                                for line in fsrc:
                                    (grade,test,seq) = string.split(line,'	')
                                    tests.append("%s %s" % ('+' if grade == 'PASS' else '-',re.sub('equence','eq',test)))
                            finally:
                                fsrc.close()
                        elif fname == 'fastqc_data.txt':
                            if options.data != None:
                                # copy the fastqc_data.txt file to the dataset data 
                                shutil.copy(path,options.data)
                            cnt = '?'
                            flen = '?'
                            gc = '?'
                            fsrc = open(path,'r')
                            try:
                                for line in fsrc:
                                    m = re.match('^Total Sequences	(\d+)',line)
                                    if m:
                                        cnt = m.groups()[-1]
                                    m =  re.match('^Sequence length	(\d+)',line)
                                    if m:
                                        flen = m.groups()[-1]
                                    m = re.match('^%GC	(\d+)',line)
                                    if m:
                                        gc = m.groups()[-1]
                            finally:
                                fsrc.close()
                            #print to stdout so that this appears in the tool dataset info
                            print("Seqs %s, Len %s, GC %s" %(cnt,flen,gc)) 
            #print to stdout so that this appears in the tool dataset info
            print("%s" % '\n'.join(tests))
        except Exception, e:
            stop_err( 'Fastq failed.\n' + str( e ) )
    finally:
        # clean up temp dir, put in a try block so we don't fail on stale nfs handles
        try: 
            if os.path.exists( tmp_dir ):
                shutil.rmtree( tmp_dir )
        except Exception, e:
            pass

if __name__=="__main__": __main__()
