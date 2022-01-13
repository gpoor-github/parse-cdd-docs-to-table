
ctsdir="~/cts-12-source/"
read -p "Enter the path the the CTS root  (n) for no Note: $CTS_SOURCE_DIR is the current dir, enter n to keep it " ctsdir
if [[ $ctsdir != "n" ]]
  then
      CTS_SOURCE_DIR=$ctsdir
      echo now the CTS source root dir is CTS_SOURCE_DIR ="$CTS_SOURCE_DIR"
fi
# android-cts-11.0_r5
# #android-cts-12.0_r1
# This script should be run in CTS source directory.
echo this is what was entered $ctsdir

echo grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt
grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt


echo Will grep -inr -A 2 "@CddTest" --include \*.java "$ctsdir/*"

grep -inr -A 2 "@CddTest" --include \*.java $ctsdir/* > input_data_from_cts/cdd_annotations_found.txt

# Not used but good for additional information for mapping finds ccd in comments not java files etc.
grep -inr -A 2 "[^.^/d]CDD " --include \*.java $ctsdir/* > input_data_from_cts/cdd_number.txt

cd ./cdd_to_cts
python3 process_annotations_references.py