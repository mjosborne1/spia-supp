import argparse
import os
import lighter
import logging
from helpers import path_exists
from datetime import datetime

def main():
    homedir=os.environ['HOME']
    parser = argparse.ArgumentParser()
    infiledefault=os.path.join(homedir,"data","spia","in","RCPA SPIA Requesting Pathology Terminology Reference Set June 2025.txt")
    outdirdefault=os.path.join(homedir,"data","spia","out")
    logsdir = os.path.join('.','logs')
    path_exists(logsdir)
    #endpoint_default="https://r4.ontoserver.csiro.au/fhir"
    endpoint_default = None
    endpoint_default="http://localhost:8080/fhir"
    template_default = os.path.join(".","templates","CodeSystemSupplement-template.json")
    logger = logging.getLogger(__name__)
    parser.add_argument("-i", "--infile", help="SPIA spreadsheet file", default=infiledefault)
    parser.add_argument("-o", "--outdir", help="output dir for artefacts", default=outdirdefault)
    parser.add_argument("-t", "--template", help="CS Supplement template file", default=template_default)
    parser.add_argument("-p", "--publish", help="fhir endpoint to publish to or `None`", default=endpoint_default)
    parser.add_argument("-e", "--encoding", help="infile encoding, default is 'latin-1'", default='latin-1')
    args = parser.parse_args()
    now = datetime.now() # current date and time
    ts = now.strftime("%Y%m%d-%H%M%S")
    FORMAT='%(asctime)s %(lineno)d : %(message)s'
    logging.basicConfig(format=FORMAT, filename=os.path.join(logsdir,f'spia-supp-{ts}.log'),level=logging.INFO)
    logger.info('Started')
    lighter.run_main(args.infile, args.outdir, args.publish, args.template, args.encoding)
    logger.info("Finished")
    
if __name__ == '__main__':
    main()