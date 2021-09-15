echo This script will scan the source of the CTS tests looking for the @CddTest annotation it will then build
echo a spreadsheet that shows the  CDD-CTS mapping built from the content and context of the annotation.
echo This script should be run in the root directory of the CTS source.
echo getting the cdd requirments from  https://source.android.com/compatibility/11/android-11-cdd
echo overwrite with another version if desired.
cdd_version=n
read -p "Do you want to download the requirements? enter version number (n) for no. " cdd_version
if [[ "$cdd_version" != n ]]
  then
    echo getting https://source.android.com/compatibility/"$cdd_version"/android-"$cdd_version-cdd"
    wget -O ./input/cdd.html  https://source.android.com/compatibility/""$cdd_version""/android-"$cdd_version"-cdd

fi

#read -p "Clone the CTS source in this directory? " $clone_cts
#echo value read = $clone_cts
#if [[ $clone_cts == "Y" ]]
#  then
#    git clone https://android.googlesource.com/platform/cts
#    echo Checking out main.
#    git checkout main
# echo verify the tag https://source.android.com/compatibility/cts/downloads
#    git describe --tags --abbrev=0
#     android-cts-11.0_r5
#fi
python3 ./cdd_to_cts/static_data_holder.py

$ctsdir=$CTS_SOURCE_DIR
echo Currently CTS source root dir is "$CTS_SOURCE_DIR"
read -p "Enter the path the the CTS root  (n) for no Note: $CTS_SOURCE_DIR is the current dir, enter n to keep it " ctsdir
if [[ $ctsdir != "n" ]]
  then
      $CTS_SOURCE_DIR=@ctsdir
      echo now the CTS source root dir is CTS_SOURCE_DIR ="$CTS_SOURCE_DIR"
fi

#
# This script should be run in CTS source directory.
echo this is what was entered $ctsdir
#/home/gpoor/aosp_platform_source/cts

echo grep -inr -A 2 "@Test" --include \*.java "$ctsdir"/tests/* > input_scripts/test-files.txt
grep -inr -A 2 "@Test" --include \*.java "$ctsdir"/tests/* > input_scripts/test-files.txt

echo grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/tests/* > input_scripts/testcases-modules.txt
grep -inr "TestCases" --include \AndroidTest.xml "$ctsdir"/tests/* > input_scripts/testcases-modules.txt
