
ctsdir_default="~/cts-12-source/"
ctsdir=$ctsdir_default
read -p "Enter the full path the the CTS root Note: $ctsdir is the current dir, enter n to keep it :" ctsdir
if [ "$ctsdir" = "n" ]; then
    echo "Entered $ctsdir"
fi
expr cts_length $ctsdir

echo cts length is $cts_length

# android-cts-11.0_r5
# #android-cts-12.0_r1
# This script should be run in CTS source directory.
echo Current value of ctsdir = $ctsdir

echo "Directory $ctsdir exists."

echo grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt
grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt


echo Will grep -inr -A 2 "@CddTest" --include \*.java "$ctsdir/*"

grep -inr -A 2 "@CddTest" --include \*.java $ctsdir/* > input_data_from_cts/cdd_annotations_found.txt

# Not used but good for additional information for mapping finds ccd in comments not java files etc.
grep -inr "[^.^/d]CDD " --include \*.java $ctsdir/* > input_data_from_cts/cdd_refference_in_comments.txt
# Not used, but provides a very conservative number of tests, all these should have bugs filed if no @CddTest.
grep -inr  -A 3 "@Test"  --include \*.java $ctsdir/* > input_data_from_cts/list_of_tests_in_cts.txt
