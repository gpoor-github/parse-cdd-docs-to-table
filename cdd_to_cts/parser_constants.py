#  Column names for Headers
TEST_LEVEL = "Test Level"
SHORTENED = "Shortened"
AREA = "Area"
CDD_BUG_ID = "CDD Bug Id"
CTS_BUG_ID = "CTS Bug Id"
COMMENT_INTERNAL = "Comment(internal) e.g. why a test is not possible"
NEW_CTS_FOR_S_ = "New CTS for S?"
NEW_REQ_FOR_S_ = "New Req for S?"
ANNOTATION_ = "Annotation?"
TEST_FILES_TXT = "input_data_from_cts/test-files.txt"
TEST_CASE_MODULES = "input_data_from_cts/testcases-modules.txt"
HEADER_KEY = 'header_key'
ROW = 'row'
SEARCH_RESULT = 'search_result'
SECTION = 'Section'
SECTION_ID = 'section_id'
REQ_ID = 'req_id'
FULL_KEY = 'full_key'
REQUIREMENT = 'requirement'
KEY_AS_NUMBER = 'key_as_number'
TEST_AVAILABILITY = 'Test Availability'
FILE_NAME = 'file_name'
METHOD_TEXT = 'method_text'
MODULES = 'modules'
MODULE = 'module'
METHOD = 'method'
CLASS_DEF = 'class_def'

# Default positions of named column
DEFAULT_SECTION_INDEX = 0
DEFAULT_SECTION_ID_INDEX = 1
DEFAULT_REQ_ID_INDEX = 2
DEFAULT_FULL_KEY_INDEX = 3

# Set of columns for table headers required to build table with consistent names
cdd_12_full_header_for_ref_part_1 = [SECTION, SECTION_ID, REQ_ID]
cdd_12_full_header_for_ref_part_2 = [TEST_AVAILABILITY, ANNOTATION_, NEW_REQ_FOR_S_,
                                     NEW_CTS_FOR_S_, CLASS_DEF, METHOD, MODULE, COMMENT_INTERNAL, "Comment (external)", "New vs Updated(Q)",
                                     CTS_BUG_ID, CDD_BUG_ID, "CDD CL", AREA, SHORTENED, TEST_LEVEL, "", "external version", "", "", ""]
cdd_12_full_header_for_ref = cdd_12_full_header_for_ref_part_1 + cdd_12_full_header_for_ref_part_2
cdd_12_subset_target_field_header = [ANNOTATION_, NEW_REQ_FOR_S_, NEW_CTS_FOR_S_, COMMENT_INTERNAL, CTS_BUG_ID, CDD_BUG_ID,
                                     AREA, SHORTENED, TEST_LEVEL]
cdd_info_only_header= (
    [SECTION, SECTION_ID, REQ_ID, KEY_AS_NUMBER, FULL_KEY, REQUIREMENT, '', '', '', '', '', '', '', '', '',
     '', ''])
update_release_header = ([TEST_AVAILABILITY, CLASS_DEF, METHOD, MODULE,COMMENT_INTERNAL,CTS_BUG_ID])
table_delimiter = '\t'
table_dialect = 'excel-tab'
table_newline = ''
table_encoding = 'UTF-8'
table_line_terminator = table_newline

# Regular expressions:
req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
section_id_re_str = "[\[>][\d+\.]+\d+"
full_key_string_for_re = section_id_re_str+'/' + req_id_re_str
METHOD_RE = '(\w+?)\(\)'
SECTION_ID_RE_STR = "(?:(\d{1,2}\.)+(\d{1,2})?)"
DOWNLOAD_HTML = "../input/cdd_{0}_download.html"
GENERATED_HTML_TSV = "../output/cdd_{0}_generated_html.tsv"