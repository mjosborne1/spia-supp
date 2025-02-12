### Installation Requirements
- Python3 and the ability to install modules using pip. This will be automatic through the requirements file.
- A file path for the output of the process, on Windows this might be C:\data\spia\ 
  on Mac/Linux it will be `/home/user/data/spia` or similar where `user` is your account name


### How to install this script 
   * `git clone https://github.com/mjosborne1/spia-supp.git`
   * `cd spia-supp`
   * `virtualenv .venv`
   * `source ./.venv/bin/activate`
   * `pip install -r requirements.txt`

### How to create the data folder and add the SPIA Terminology file
   * `python main.py` will create any required folders and fail silently
   * Save a copy of the latest RCPA resources and extract the file called `RCPA SPIA Requesting Pathology Terminology Reference Set July 2024.xlsx` or whatever the latest version is called.
   * Open the xlsx file in Excel and save it as a tab separated file e.g. `RCPA SPIA Requesting Pathology Terminology December 2024.txt`  in the `in` folder e.g. `/home/user/data/spia/in`


### How to run the script   
   * ensure the virtual environment is set
      * Mac/Linux/WSL: `source ./.venv/bin/activate`
      * Windows CMD/Powershell: `.\.venv\Scripts\activate`
   * `python main.py --infile your_data_folder/in/YourSPIATerminologyTSV.txt` 
      e.g. `python main.py -i "/home/user/data/spia/in/RCPA SPIA Requesting Pathology Terminology December 2024.txt"` 
   * Note: The script will attempt to publish by default to a local instance of ontoserver running on http://localhost:8080 so be sure to change to your own instance or the R4 public sandbox.
   * Adjust the templates so that the url of the CodeSystem Supplements and ValueSets match your usage. They default to example urls.     
   ```
        usage: main.py [-h] [-i INFILE] [-o OUTDIR] [-t TEMPLATE] [-p PUBLISH] [-e ENCODING]

         options:
         -h, --help            show this help message and exit
         -i INFILE, --infile INFILE
                                 SPIA spreadsheet file
         -o OUTDIR, --outdir OUTDIR
                                 output dir for artefacts
         -t TEMPLATE, --template TEMPLATE
                                 CS Supplement template file
         -p PUBLISH, --publish PUBLISH
                                 fhir endpoint to publish to or `None`
         -e ENCODING, --encoding ENCODING
                                 infile encoding, default is 'latin-1'
   ```    

### Output
   * CodeSystem Supplement outputs to `your_data_folder/out/SPIARequestingCodeSystemSupplement.json` by default.

### Testing
   * To see the results of applying the CS Supplement to a ValueSet of all members of the SPIA Requesting Ref Set use this query in Postman:  `{{url}}/ValueSet/$expand?url=http://erequestingexample.org.au/fhir/ValueSet/rcpa-spia-valueset-with-supplemental-terms&includeDesignations=true` where url is a variable for your ontoserver endpoint.