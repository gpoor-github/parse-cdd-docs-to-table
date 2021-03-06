# User home directory
USER_HOME = "~/"

# Point to root of the .md files to parse. For parse_cdd_md
AOSP_ROOT  = USER_HOME + "aosp_cdd"
CDD_MD_ROOT= AOSP_ROOT+"/cdd"

# For mapping or sheet creation from annotation or finding or other operations that need the source code.
CTS_SOURCE_NAME = 'cts'
CTS_SOURCE_PARENT = USER_HOME + "cts-source/"
CTS_SOURCE_ROOT = CTS_SOURCE_PARENT + CTS_SOURCE_NAME
ANNOTATIONS_MAPPING_FOUND_IN_CTS_SOURCE = '../output/annotations_mappings.tsv'
