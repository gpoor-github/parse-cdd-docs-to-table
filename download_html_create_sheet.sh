
echo Downloads the cdd requirments from  https://source.android.com/compatibility/
echo Enter the android version you want to generate a table of when prompted.
cdd_version=n
cd ./cdd_to_cts
python3 parse_cdd_html.py $cdd_version