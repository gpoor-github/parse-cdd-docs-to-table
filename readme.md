
Prerequisites:
1. Install git
2. Clone project
3. Install Python3 must be *version 3.7* or greater because of formatting F used. Verify by running:
   - python3 --version    
4. Install requirements: 
   - python -m pip install -r requirements.txt
   
Steps to parse CDD HTML to table:
 1. Change directories to be in <cloned root>/parse-cdd-docs-to-table/cdd_to_cts 
 2. Run the following to start the python program which should prompt you for an Android CDD version. It will then download 
 the appropriate html file, parse it and generate a table, cdd_versionXX_generated_html.tsv, in the ../output directory.
--python3 parse_cdd_html.py


