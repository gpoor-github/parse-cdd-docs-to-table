#
# Block to comment
#

read -p "Do you want to download the requirements? enter version number (n) for no. " cdd_version
if [[ "$cdd_version" != n ]]
  then
    echo getting https://source.android.com/compatibility/"$cdd_version"/android-"$cdd_version-cdd"
    wget -O ./input/cdd_""$cdd_version""_download.html  https://source.android.com/compatibility/""$cdd_version""/android-"$cdd_version"-cdd

fi