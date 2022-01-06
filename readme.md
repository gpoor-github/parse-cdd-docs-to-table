Steps to parse CDD HTML to table

Prerequisites:

1. Install Python3
2. Install requirements. pip requirements.txt
3. Get cdd html file:
   - Option a: Install wget to use script download_html_create_sheet.sh
   - Option b: manually download a version of cdd html from  https://source.android.com/compatibility/ for example
   - https://source.android.com/compatibility/12/android-12-cdd
   
4. run python3 -m cdd_to_cts.parse_cdd_html
