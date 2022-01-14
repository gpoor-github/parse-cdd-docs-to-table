
**Prerequisites:**
1. Install git
2. Clone project 
3. Install Python3 must be *version 3.7* or greater because of formatting F used. Verify by running:
   - python3 --version    
4. Install requirements: 
   - python -m pip install -r requirements.txt
5. On MacOS there is a Python bug to work around:
   1. Navigate to /Applications/Python3.x
   2. run "Install Certificates.command"
   3. Note you may do this in Finder by:
      1. Select menu Go|Go to Folder
      2. Type /Applications/Python3.x
      3. Double click "Install Certificates.command"

**Update and overwrite local changes**
1. From the project git root run 
2. git reset --hard
3. git pull
4. Confirm that git pull had no errors by looking at the log.

**Steps to parse CDD HTML to table:**
1. Change directories to be in  ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script which should prompt you for an Android CDD version. It will then download 
 the appropriate html file, parse it and generate a table, cdd_versionXX_generated_html.tsv, in the ../output directory.
   - python3 parse_cdd_html.py

**Steps to Compare Versions 12 vs 11 and generate a table:** 
Hard coded for now, but just change the numbers to any available version in the file  diff_cdd_from_html_version("12", "11")
1. Change directories to be in ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts
2. Run the following to start the python script it will compare 2 versions. It needed it will download the html and parse them.
The comparison results will be visible in the console. A table with the differences will be created in the output directory. ..\output\diff_12_vs_11.tsv
   - python3 check_sheet.py

**Steps to generate the Annotation Mapping:**
1. Clone CTS source: 
   1. Create a directory "~/cts-12-source/" 
   2. Go into that directory.
   3. Copy the path to that directory to pass as a parameter later.
   4. Clone the desired version of the CTS tests to a directory. 
      - git clone https://android.googlesource.com/platform/cts
2. Change directories to be in our cdd python project's root:
   - ~/_your_project_root_/parse-cdd-docs-to-table 
3. Run the following shell script to update grep for annotations and run the python script to generate a table that maps requirements to cts test by finding annotations and building the tests. A table in the output directory: ..\output\annotations_mappings.tsv 
   - Run the shell script in the parent directory
   - ./do_annotations_mapping.sh
   - When prompted hit enter if the default CTS source directory is correct, otherwise type it in. 
