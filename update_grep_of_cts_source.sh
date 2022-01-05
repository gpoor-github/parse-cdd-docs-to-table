
ctsdir=$CTS_SOURCE_DIR
echo Currently CTS source root dir is  ["$CTS_SOURCE_DIR"] running script to update environment variable
python3 ./cdd_to_cts/static_data.py
echo Now CTS source root dir is ["$CTS_SOURCE_DIR"]
#/home/gpoor/cts-source/cts
#/home/gpoor/cts-12-source
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

