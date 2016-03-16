from galaxy.jobs import JobDestination
import ast


def bowtie2_dynamic_destination(job):
    '''
    Send bowtie2 jobs to long queue based on reporting options
    If `-a` is specified or `-k` >= 40, send to long queue, else normal queue
    '''
    normal_queue = 'cetus_multicore_mediummem'
    long_queue = 'cetus_multicore_highmem_1wk'
    queue = normal_queue
    for jp in job.get_parameters():
        if jp.name == "analysis_type":
            jpv = ast.literal_eval(jp.value)
            ro = jpv.get("reporting_options")
            if ro is not None:
                ros = ro.get("reporting_options_selector")
                if ros == "a":
                    queue = long_queue
                if ros == "k":
                    k = ro.get("k")
                    try:
                        kval = int(k)
                        if kval >= 40:
                            queue = long_queue
                    except ValueError:
                        pass
    return queue
