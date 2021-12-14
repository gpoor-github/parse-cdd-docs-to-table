#  Block to comment

TEST_LEVEL = "Test Level"
SHORTEND = "Shortened"
AREA = "Area"
CDD_BUG_ID = "CDD Bug Id"
CTS_BUG_ID = "CTS Bug Id"
COMMENT_INTERNAL = "Comment(internal) e.g. why a test is not possible"
NEW_CTS_FOR_S_ = "New CTS for S?"
NEW_REQ_FOR_S_ = "New Req for S?"
ANNOTATION_ = "Annotation?"
USER_HOME = "/home/gpoor/"
CTS_SOURCE_PARENT = USER_HOME + "cts-12-source/"
CTS_SOURCE_NAME = 'cts'
CTS_SOURCE_ROOT = CTS_SOURCE_PARENT + CTS_SOURCE_NAME
WORKING_ROOT = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source"
AOSP_ROOT  ="/home/gpoor/aosp_cdd"
CDD_MD_ROOT= AOSP_ROOT+"/cdd"
TEST_FILES_TXT = "input_data_from_cts/test-files.txt"
TEST_CASE_MODULES = "input_data_from_cts/testcases-modules.txt"
req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
section_id_re_str = "[\[>][\d+\.]+\d+"
full_key_string_for_re = section_id_re_str+'/' + req_id_re_str
METHOD_RE = '(\w+?)\(\)'
SECTION_ID_RE_STR = "(?:(\d{1,2}\.)+(\d{1,2})?)"
HEADER_KEY = 'header_key'
ROW = 'row'
SEARCH_RESULT = 'search_result'
SECTION = 'Section'
DEFAULT_SECTION_INDEX = 0
SECTION_ID = 'section_id'
DEFAULT_SECTION_ID_INDEX = 1
REQ_ID = 'req_id'
DEFAULT_REQ_ID_INDEX = 2
FULL_KEY = 'full_key'
DEFAULT_FULL_KEY_INDEX = 3
REQUIREMENT = 'requirement'
KEY_AS_NUMBER = 'key_as_number'
TEST_AVAILABILITY = 'Test Availability'
FILE_NAME = 'file_name'
METHOD_TEXT = 'method_text'
MODULES = 'modules'
MODULE = 'module'
METHOD = 'method'
CLASS_DEF = 'class_def'
cdd_12_full_header_for_ref_part_1 = [SECTION, SECTION_ID, REQ_ID]
cdd_12_full_header_for_ref_part_2 = [TEST_AVAILABILITY, ANNOTATION_,  NEW_REQ_FOR_S_,
                              NEW_CTS_FOR_S_, CLASS_DEF, METHOD, MODULE, COMMENT_INTERNAL, "Comment (external)", "New vs Updated(Q)",
                              CTS_BUG_ID, CDD_BUG_ID, "CDD CL", AREA, SHORTEND, TEST_LEVEL, "", "external version", "", "", ""]
cdd_12_full_header_for_ref = cdd_12_full_header_for_ref_part_1 + cdd_12_full_header_for_ref_part_2
ccd_12_subset_target_field_header = [ANNOTATION_, NEW_REQ_FOR_S_, NEW_CTS_FOR_S_, COMMENT_INTERNAL, CTS_BUG_ID, CDD_BUG_ID,
                                     AREA, SHORTEND, TEST_LEVEL]
cdd_info_only_header: [] = (
    [SECTION, SECTION_ID, REQ_ID, KEY_AS_NUMBER, FULL_KEY, REQUIREMENT, '', '', '', '', '', '', '', '', '',
     '', ''])
update_release_header: [] = ([TEST_AVAILABILITY, CLASS_DEF, METHOD, MODULE,COMMENT_INTERNAL,CTS_BUG_ID])
table_delimiter = '\t'
table_dialect = 'excel-tab'
table_newline = ''
table_encoding = 'UTF-8'
table_lineterminator = table_newline