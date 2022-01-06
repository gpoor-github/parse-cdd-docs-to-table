
echo Downloads the cdd requirments from  https://source.android.com/compatibility/
echo Enter the android version you want to generate a table of when prompted.
cdd_version=n
./download_requirements.sh
python3 ./cdd_to_cts/parse_cdd_html.py