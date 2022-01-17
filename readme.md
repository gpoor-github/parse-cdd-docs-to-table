
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

**Steps to parse CDD HTML (MD file instructions below) to table:**
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
   4. Clone the desired version of the CTS tests to the above directory. 
      - git clone https://android.googlesource.com/platform/cts
2. Change directories to be in our cdd python project's root:
   - ~/_your_project_root_/parse-cdd-docs-to-table 
3. Run the following shell script to update grep for annotations and run the python script to generate a table that maps requirements to cts test by finding annotations and building the tests. A table in the output directory: ..\output\annotations_mappings.tsv 
   - Run the shell script in the parent directory
   - ./do_annotations_mapping.sh
   - When prompted hit enter if the default CTS source directory is correct, otherwise type it in. 

**Steps to parse CDD MD files to table:**

1. **_Prerequisite:_ Confirm you have the .md files at the correct version in an accessible directory** and copy the directory name:  
   -- For example, through source control:
   1. **Clone CTS source (If not cloned earlier)**:
      1. Create a directory "~/aosp_cdd/" 
      2. Go into that directory.
      3. Copy the path to that directory + "/cdd" to pass as a parameter later.
      4. Clone the desired version of the CDD subset of AOSP tests the above directory. 
         - git clone https://android.googlesource.com/platform/compatibility/cdd
   2. **Sync the version you want to parse:** Git has a rich set of command to find and get versions please refer to your documentation and tools. 
      - _Optional see available versions:_ List branches: _git branch sort=-committerdate_ 
        - Or list tags: _git tag --list 'android-12*'_
      - Confirm the current version is the version you want and remember the name:
        - git describe
      - If the current version isn't correct use appropriate git commands to get the version you want.
   3. **Confirm this is the version you want and remember the name**:
   - _git describe_
   - The script will use "git describe" (see above) to name the file so that it corresponds the version. 
   - Now we have the correct version of .md files and know where they are:
2. **Change directories to be in our cdd project's python files sub folder**:
   - ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts
3. **run the parse_cdd_md.py file**, you may pass it the path to the aosp_cdd git root, or run without arguments to be prompted:
   - python3 parse_cdd_md.py ~/aosp_cdd/cdd
4. A table file will be created, you should see the name in the output, go to the output directory to find it.