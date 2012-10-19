'''
Created on Oct 17, 2012

@author: georgianadinu
'''
'''
Created on Oct 17, 2012

@author: georgianadinu
'''

'''
Created on Jun 12, 2012

@author: thenghia.pham
'''


import sys
import getopt
import os
from ConfigParser import ConfigParser
from composes.utils import scoring_utils
from composes.utils import log_utils

import logging
logger = logging.getLogger("test vector space construction pipeline")



def usage(errno=0):
    print >>sys.stderr,\
    """Usage:
    python compute_similarities.py [options] [config_file]

    Options:
    -i --input <file>: input file.
    --in_dir: <dir>: input directory, all files that pass the --filter are tested.
                -i value is ignored. Optional.
    --filter: <string>: when --in_dir, it acts as a filter on the files to be tested:
                only files containing this substring are tested. Optional, 
                default all files in in_dir are tested.
    -m --correlation_measures <list(string)>: comma-separated correlation measures
    -c --columns <(int,int)>: pair of columns, indicating which columns contain 
            the words to be compared
    -l --log <file>: log file. Optional, default ./build_core_space.log
    -h --help : help
    
    Arguments:
    config_file: <file>, used as default values for configuration options above.
            If you don't specify these options in [options] the value from the 
            config_file will be used.
    
    Example:
    """
    sys.exit(errno)

def assert_option_not_none(option, message):
    if option is None:
        print message
        usage(1)
        

def evaluate_sim(in_file, columns, corr_measures):
    
    if not len(columns) == 2:
        raise ValueError("Column description unrecognized!") 
    
    gold = []
    prediction = []
    with open(in_file) as in_stream:
        for line in in_stream:
            if not line.strip() == "":
                elems = line.strip().split()
                gold.append(float(elems[columns[0]]))
                prediction.append(float(elems[columns[1]]))
    
    for corr_measure in corr_measures:
        print "CORELATION:%s" % corr_measure                    
        corr = scoring_utils.score(gold, prediction, corr_measure)
        print "\t%f" % corr  

        
def evaluate_sim_batch(in_dir, columns, corr_measures, filter_=""):
    
    if not os.path.exists(in_dir):
        raise ValueError("Input directory not found: %s" % in_dir)
    
    if not in_dir.endswith("/"):
        in_dir = in_dir + "/"
        
    for file_ in os.listdir(in_dir):
        if file_.find(filter_) != -1:
            print file_
            evaluate_sim(in_dir + file_, columns, corr_measures)


def main(sys_argv):
    try:
        opts, argv = getopt.getopt(sys_argv[1:], "hi:m:c:l:", 
                                   ["help", "input=", "correlation_measures=",
                                    "columns=", "log=", "in_dir=", "filter="])
        
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    in_file = None
    in_dir = None
    filter_ = ""
    corr_measures = None
    columns = None
    log_file = None

    if (len(argv) == 1):
        config_file = argv[0]
        config = ConfigParser()
        config.read(config_file)
        in_file = config.get("input") if config.has_option("input") else None
        in_dir = config.get("in_dir") if config.has_option("in_dir") else None
        filter_ = config.get("filter") if config.has_option("filter") else ""
        corr_measures = config.get("correlation_measures").split(",") if config.has_option("correlation_measures") else None
        columns = config.get("columns").split(",") if config.has_option("columns") else None
        log_file = config.get("log") if config.has_option("log") else None
    
    for opt, val in opts:
        if opt in ("-i", "--input"):
            in_file = val 
        elif opt in ("-m", "--correlation_measures"):
            corr_measures = val.split(",") 
        elif opt in ("-c", "--columns"):
            columns = val.split(",")
            if len(columns) != 2:
                raise ValueError("Columns (-c) field should contain two comma-separated integers (e.g. -c 3,4)")
            columns = [int(columns[0]), int(columns[1])]
        elif opt == "--in_dir":
            in_dir = val
        elif opt == "--filter":
            filter_ = val    
        elif opt in ("-l", "--log"):
            log_file = val 
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        else:
            usage(1)
            
    log_utils.config_logging(log_file)
    
    assert_option_not_none(corr_measures, "Correlation measures required")
    assert_option_not_none(columns, "Columns to be read from input file required")
    
    if not in_dir is None:
        evaluate_sim_batch(in_dir, columns, corr_measures, filter_)
    else:
        assert_option_not_none(in_file, "Input file required")
        evaluate_sim(in_file, columns, corr_measures)
   
if __name__ == '__main__':
    main(sys.argv)
    