echo This script will scan the source of the CTS tests looking for the @CddTest annotation it will then build
echo a spreadsheet that shows the  CDD-CTS mapping built from the content and context of the annotation.
echo This script should be run in the root directory of the CTS source.

#read -p "Clone the CTS source in this directory? " $clone_cts
#echo value read = $clone_cts
#if [[ $clone_cts == "Y" ]]
#  then
#    git clone https://android.googlesource.com/platform/cts
#    echo Checking out main.
#    git checkout main
#fi
ctsdir='/home/gpoor/cts-source'
if [[ $clone_cts != "Y" ]]
  then
      read -p "Enter the path the the CTS root ( . for current dir )" $ctsdir
fi
#
# This script should be run in CTS source directory.
echo this is what was entered $ctsdir
#/home/gpoor/cts-source/

echo Will grep -inr -A 2 "@Test" --include \*.java "$ctsdir/*"
grep -inr -A 2 "@Test" --include \*.java $ctsdir/* > test-files.txt

grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/* > input/testcases-modules.txt
#python3 augment_sheet_with_cdd_html_info.py
