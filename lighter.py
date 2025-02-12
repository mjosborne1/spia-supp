"""
   fhir lighter library for building the fhir artefacts from the TSV input file 
"""

import json
import re
import urllib
import numpy as np
import pandas as pd
import logging
from fhirclient.models import valueset,conceptmap,codesystem,coding
from fhirclient import client
from fhirpathpy import evaluate
from requests import get, put


from helpers import path_exists 
import os

logger = logging.getLogger(__name__)

## check_numeric
#    return true if the pandas frame is numeric and not a float else return false
def is_numeric(value):
    if pd.isna(value):
        return False
    elif isinstance(value, np.float64):
        print("value is a float {0}".format(value))
        return False
    else:
        return True
    

def create_client(endpoint):
    settings = {
        'app_id': 'spia-supp',
        'api_base': endpoint
    }
    logger.info(f'created smart client to {endpoint}')
    smart = client.FHIRClient(settings=settings)
    return smart


def validate_concept(endpoint, code, display=None):
  """Check that the code is a Valid member of the ValueSet and return an array [ result (boolean), display (string) ]
     Where result is True if the code is valid, else False and an empty string.
  """
  valstr='/CodeSystem/$validate-code'
  system="http://snomed.info/sct"
  query=f'{endpoint}{valstr}?url={system}&code={code}'
  if display != None:
      display = urllib.parse.quote(display,safe='')
      query += f'&display={display}'
  #print(query)
  headers = {'Accept': 'application/fhir+json'}
  response = get(query, headers=headers) 
  data =  response.json()
  result = evaluate(data,"parameter.where(name = 'result').valueBoolean")
  if result[0] == True:
    display = evaluate(data,"parameter.where(name = 'display').valueString")
    return [ result[0], display[0] ]
  return [ result[0], "" ]


def clean_string(s):
    if isinstance(s, float):
        s = str(s)
    if isinstance(s, str):
        # Remove non-ASCII characters
        s = s.encode('ascii', errors='ignore').decode('ascii')
        s = s.strip()
    return s


def get_all_terms(df):
    snomed_dict = {}
    for index, row in df.iterrows():
        # Extract relevant columns
        synonyms = row['RCPA Synonyms']
        snomed_expression = row['Terminology binding (SNOMED CT-AU)']
        rcpa_preferred_term = row['RCPA Preferred term']
        if rcpa_preferred_term == '' or rcpa_preferred_term == 'nan':
            continue
        if snomed_expression == '' or snomed_expression == 'nan':
            continue
        # Split the SNOMED code and term
        snomed_code_split = snomed_expression.split('|')
        if len(snomed_code_split) > 1:
            snomed_code = snomed_code_split[0].strip()
            snomed_term = snomed_code_split[1].strip()
        else:
            snomed_code = snomed_expression
            snomed_term = ''
        
        # Create a list of terms and synonyms
        terms_and_synonyms = [rcpa_preferred_term]
        if pd.notna(synonyms):
            terms_and_synonyms.extend([syn.strip() for syn in synonyms.split(';')])
        
        # Add to the dictionary
        if snomed_code not in snomed_dict:
            snomed_dict[snomed_code] = {
                'snomed_term': snomed_term,
                'synonyms': terms_and_synonyms
            }
        else:
            snomed_dict[snomed_code]['synonyms'].extend(terms_and_synonyms)
    return snomed_dict


def create_or_update_smart_client(cs, endpoint):
    smart=None
    if endpoint != None and endpoint != '':
        smart = create_client(endpoint)
    if smart != None:
        if cs.id:
            response = cs.update(smart.server)
        else:
            response = cs.create(smart.server)
        if response:
            return 201
        else:
            return 500
    else:
        return 200
    
     
def build_codesystem_supplement(infile,outdir,endpoint,templates_path,encoding):
    """
    Build a SNOMED CT codesystem supplement of designations for the RCPA Requesting Ref Set
    """
    print(f'...Building CodeSystem Supplement')
    cs_sup_file = os.path.join(outdir,"SPIARequestingCodeSystemSupplement.json")
    
    # Read the TSV file
    df = pd.read_csv(infile, skipinitialspace=True, sep='\t',dtype={'RCPA Preferred term':str,'RCPA Synonyms':str,'Terminology binding (SNOMED CT-AU)':str,'SNOMED CT Fully Specified':str}, encoding=encoding)

    # Apply the cleaning function to each cell in the DataFrame
    df_cleaned = df.map(lambda x: clean_string(x))

    # Read the FHIR ConceptMap JSON file into a Python dictionary
    template =  templates_path
    print(f"Processing CodeSystem Supplement template...{template}")

    snomed_dict = get_all_terms(df_cleaned)   
    with open(template) as f:
        meta = json.load(f)
        cs = codesystem.CodeSystem()
        cs.id = meta.get("id")
        cs.status = meta.get('status')
        cs.name = meta.get('name')
        cs.title = meta.get('title')
        cs.description = meta.get('description')
        cs.publisher = meta.get('publisher')
        cs.version = meta.get('version')
        cs.url = meta.get('url')
        cs.copyright = meta.get('copyright')
        cs.experimental = meta.get('experimental')
        cs.content = meta.get('content')
        cs.supplements = meta.get('supplements')
        cs.concept = []        
       
        for code, details in snomed_dict.items():
            if not is_numeric(code):
                continue
            logger.info(f'details: {details}')
            concept = codesystem.CodeSystemConcept()
            concept.code = code   
            display_name = validate_concept(endpoint, code, display=None)[1]
            if display_name == "":
                logger.info(f'{code} is not in SNOMED CT, skipping')
                continue
            concept.designation = [] 
            if details and details['synonyms']:
                for pseudonym in details['synonyms']:
                    if pseudonym and pseudonym != "" and pseudonym != "nan":
                        # Check if the pseudonym is already a Valid display in SCT Ignore it if it is valid
                        valResult = validate_concept(endpoint=endpoint, code=code, display=pseudonym)
                        if valResult[0]:
                            logger.info(f'{code} {pseudonym} is valid, so skipping')
                            continue
                        logger.info(f'{code} {pseudonym} is not in terminology, add it to the supplement')
                        designation = codesystem.CodeSystemConceptDesignation()
                        designation.language = "en"
                        designation.value = pseudonym
                        use = coding.Coding() 
                        use.system = "http://snomed.info/sct"
                        use.code =  "900000000000013009"
                        use.display = "Synonym"                    
                        designation.use = use
                        concept.designation.append(designation)                       
                cs.concept.append(concept)
        # Dump the CodeSystem Supplement to json file for manual review
        with open(cs_sup_file, "w") as f:
            json.dump(cs.as_json(), f, indent=2)
        
        st = create_or_update_smart_client(cs, endpoint)
        return st

def create_spia_valueset(endpoint):
    smart=None
    if endpoint != None and endpoint != '':
        smart = create_client(endpoint)
    with open('./templates/SPIARequestingValueSet-template.json', 'r') as file:
        vs_data = json.load(file)
    # Instantiate the ValueSet object
    vs = valueset.ValueSet(vs_data)    
    if smart != None:
        if vs.id:
            response = vs.update(smart.server)
        else:
            response = vs.create(smart.server)
        if response:
            return 201
        else:
            return 500
    else:
        return 200       

## Mainline
## Output the Valuesets and Conceptmap built from the RRS file    
def run_main(infile,outdir,endpoint,template,encoding):
    ## build_codesystem_supplement 
    csupp = build_codesystem_supplement(infile,outdir,endpoint,template,encoding)    
    logger.info(f'Built CodeSystem Supplement, returned {csupp}')
    vs_status = create_spia_valueset(endpoint)
    logger.info(f'Built SPIA ValueSet, returned {csupp}')
