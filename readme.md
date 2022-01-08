Steps to parse CDD HTML to table

Prerequisites:

1. Install Python3 must be version 3.9 because of type features used. 
2. Install requirements: 
-- python -m pip install -r requirements.txt
3. Get cdd html file:
   - Option a: Install wget to use script download_html_create_sheet.sh
   - Option b: manually download a version of cdd html from  https://source.android.com/compatibility/ for example
   - https://source.android.com/compatibility/12/android-12-cdd
   
4. cd into <my_project_root>/cdd_to_cts
5. python3 parse_cdd_html.py
6. python3 check_sheet.py
7. python3 table_functions_for_release.py 

