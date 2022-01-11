
Prerequisites:

1. Install git
2. Clone project
3. Install Python3 must be *version 3.6* or greater because of formatting F used. Verify by running:
   - python3 --version    
4. Install requirements: 
   - python -m pip install -r requirements.txt
   
Steps to parse CDD HTML to table:
 1. Get cdd html file:

   - Option a: 
     1. Manually download a version of cdd html from  https://source.android.com/compatibility/ 
        - for example
        - https://source.android.com/compatibility/12/android-12-cdd
        - Download to  <cloned root>/parse-cdd-docs-to-table/input/cdd_12_download.html
        
 2. Change directories to be in <cloned root>/parse-cdd-docs-to-table/cdd_to_cts
 3. python3 parse_cdd_html.py 
 4. python3 check_sheet.py
 5. python3 table_functions_for_release.py 

