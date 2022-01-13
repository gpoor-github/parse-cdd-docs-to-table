
Prerequisites:
1. Install git
2. Clone project
3. Install Python3 must be *version 3.7* or greater because of formatting F used. Verify by running:
   - python3 --version    
4. Install requirements: 
   - python -m pip install -r requirements.txt

Steps to parse CDD HTML to table:
1. Change directories to be in <cloned root>/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script which should prompt you for an Android CDD version. It will then download 
 the appropriate html file, parse it and generate a table, cdd_versionXX_generated_html.tsv, in the ../output directory.
--python3 parse_cdd_html.py

Steps to compare versions 12 vs 11 and generate a table 
Hard coded for now, but just change the numbers to any available version in the file  diff_cdd_from_html_version("12", "11")

1. Change directories to be in <cloned root>/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script it will compare 2 versions. It needed it will download the html and parse them.
The comparison results will be visible in the console. A table with the differences will be created in the output directory. ..\output\diff_12_vs_11.tsv
--python3 check_sheet.py

Steps to generate the annotation mapping:
1. Clone the desired version of the CTS tests to a directory. 
2. 
3. Change directories to be in <cloned root>/parse-cdd-docs-to-table/cdd_to_cts 
4. Run the following to start the python script to generate a table that maps requirements to cts test by finding annotations and building the tests.A table with the differences will be created in the output directory. ..\output\diff_12_vs_11.tsv 
 process_annotations_references.py