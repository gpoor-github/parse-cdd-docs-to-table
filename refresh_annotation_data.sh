
ctsdir_default="~/cts-12-source/"
ctsdir=$ctsdir_default
read -p "Enter the path the the CTS root  (n) for no Note: $ctsdir is the current dir, enter n to keep it :" ctsdir
if [ $ctsdir != "n" ]
  then
      ctsdir = $ctsdir_default
      echo now the CTS source root dir is "$ctsdir"
fi

if [$ctsdir == ""]
  then
    ctsdir = $ctsdir_default
fi
expr length $ctsdir
echo length

# android-cts-11.0_r5
# #android-cts-12.0_r1
# This script should be run in CTS source directory.
echo Current value of ctsdir = $ctsdir
if [ -d $ctsdir ]
then
    echo "Directory $ctsdir exists."

    echo grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt
    grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input_data_from_cts/testcases-modules.txt


    echo Will grep -inr -A 2 "@CddTest" --include \*.java "$ctsdir/*"

    grep -inr -A 2 "@CddTest" --include \*.java $ctsdir/* > input_data_from_cts/cdd_annotations_found.txt

    # Not used but good for additional information for mapping finds ccd in comments not java files etc.
    grep -inr -A 2 "[^.^/d]CDD " --include \*.java $ctsdir/* > input_data_from_cts/cdd_number.txt

else
    echo "Error: Directory $ctsdir does not exists."
fi