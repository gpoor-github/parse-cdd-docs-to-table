
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

**Run any method or python function**
1. Change directories to be in  ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the target function as supported by the python language. For example to compare to files:
   - python3 -c 'import check_sheet; f1="../output/cdd_12_generated_html.tsv";  f2="../output/cdd_11_generated_html.tsv";check_sheet.diff_tables_files(f1,f2)'
   
**HTML files parsed (MD file instructions below) to table:**
1. Change directories to be in  ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script which takes an HTML input file and a name for an output table. If not given it will prompt. 
   - python3 parse_cdd_html_to_file.py OPTIONAL_CDD_HTML_DOWNLOADED.html OPTIONAL_OUTPUT_TABLE_FILE.tsv

**From Android Version download CDD HTML and parse to table:**
1. Change directories to be in  ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script which should prompt you for an Android CDD version. It will then download 
 the appropriate html file, parse it and generate a table, cdd_versionXX_generated_html.tsv, in the ../output directory.
   - python3 parse_cdd_html.py

**Versions Compare and generate comparison table:** 
Will take two numbers as parameters as Android version. If the numbers are missing it will prompt. The script takes version numbers and will try and download a public version and build tables and compare them.
1. Change directories to be in ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts
2. Run the following to start the python script it will compare 2 versions passed to it or entered. It needed it will download the html and parse them.
The comparison results will be visible in the console. A table with the differences will be created in the output directory. ..\output\diff_12_vs_11.tsv
   - python3 check_sheet.py 11 12

**File Compare and generate comparison table:** 
Will take two files as parameters. If the files are missing it will prompt. The script takes files and compares them.
1. Change directories to be in ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts
2. Run the following to start the python script and compare 2 files passed to it or entered.
The comparison results will be visible in the console. A table with the differences will be created in the output directory. ..\output\diff_FILE_1_vs_FILE_2.tsv
   - python3 compare_files.py ../output/cdd_12_generated_html.tsv ../output/cdd_11_generated_html.tsv

**Generate CDD-CTS mapping table from Annotations in CTS Source Code :**
1. _Prerequisite:_ Clone CTS source: 
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

**Annotation Injection To CTS Source Code from a CDD-CTS mapping table:**
1. _Prerequisite (same as above):_ Clone CTS source 
   1. Create a directory "~/cts-12-source/" 
   2. Go into that directory.
   3. Copy the path to that directory to pass as a parameter later.
   4. Clone the desired version of the CTS tests to the above directory. 
      - git clone https://android.googlesource.com/platform/cts
2. Change directories to be in our cdd python project's root:
   - ~/_your_project_root_/parse-cdd-docs-to-table 
3. Run the following shell script to update grep for annotations and the creation of the list of Test Modules:
   - ./refresh_annotation_data.sh
   - When prompted hit enter if the default CTS source directory is correct, otherwise type it in. 
**Run Annotation Injection, Warning this will change your source code in your cts-source directory**
1. Change directories to be in  ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts 
2. Run the following to start the python script which should prompt you for a table file with the mappings you wish to inject.
- python3 inject_annotations_into_cts.py your_cts_source_directory True_False-modify-code your-cdd-to-cts-annotation-mappings-to-inject-to-cts-source.tsv your_desired_file_for_found_requirements.tsv (optional)
- Sample:
- python3 inject_annotations_into_cts.py ~/cts-12-source/ False ../input/cdd-12-new-cts-mapping.tsv ../output/sample_requirements_injected.tsv
6. Do a git commit on the cts source to see changed files 


**MD CDD files parse to table:**

1. **_Prerequisite:_ Confirm you have the .md files at the correct version in an accessible directory** and copy the directory name:  
   -- For example, through source control:
   1. **Clone CTS source (If not cloned earlier)**:
      1. Create a directory "~/aosp_cdd/" 
      2. Go into that directory:
         - cd aosp_cdd
      3. Clone the desired version of the CDD subset of AOSP tests the above directory. 
         - git clone https://android.googlesource.com/platform/compatibility/cdd
      4. Go into the newly cloned "cdd" directory confirm it has the directories with md files and copy the path to use as a parameter later:
         - cd cdd 
         - ls
         - pwd
2. **Sync the version you want to parse:** Git has a rich set of command to find and get versions please refer to your documentation and tools. 
   - _Optional see available versions:_ List branches: 
     - _git branch sort=-committerdate_ 
     - Or list tags: _git tag --list 'android-12*'_
   - Confirm the current version is the version you want and remember the output it will be your filename:
     - git describe
   - If the current version isn't correct use appropriate git commands to get the version you want.
   3. **Confirm this is the version you want and remember the name**:
   - _git describe_
   - The script will use "git describe" (see above) to name the file so that it corresponds the version. 
   - Now we have the correct version of .md files and know where they are:
3. **Change directories to be in our cdd project's python files sub folder**:
   - ~/_your_project_root_/parse-cdd-docs-to-table/cdd_to_cts
4. **run the parse_cdd_md.py file**, you may pass it the path to the aosp_cdd git root and/or file_name, or run without arguments to be prompted:
   - python3 parse_cdd_md.py ~/aosp_cdd/cdd  optional_filename.tsv
5. A table file will be created, you should see the name in the output, go to the output directory to find it.