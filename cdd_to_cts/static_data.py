import os
import time

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
# os.getcwd().replace("cdd_to_cts","")
AOSP_ROOT  ="/home/gpoor/aosp_cdd"
CDD_MD_ROOT= AOSP_ROOT+"/cdd"
# Remember these 2 files must exit before the program is run
CDD_REQUIREMENTS_FROM_HTML_FILE = 'input/cdd.html'
FILTER_KEYS_DOWNLOADED_TABLE = 'input/FILTER_KEYS_DOWNLOADED_TABLE.tsv'

# These 2 are generated
DATA_SOURCES_CSV_FROM_HTML_1st = "output/DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
DATA_SOURCES_UPDATED_CSV_2nd = "output/DATA_SOURCES_UPDATED_CSV_2nd.tsv"

FILTERED_TABLE_TO_SEARCH = "output/FILTERED_TABLE_TO_SEARCH.tsv"
RX_WORKING_OUTPUT_TABLE_TO_EDIT = "output/RX_WORKING_OUTPUT_TABLE_TO_EDIT.tsv"

INPUT_TABLE_FILE_NAME_RX = "output/table_file_for_react_filtered.tsv"

TEST_FILES_TXT = "input_data_from_cts/test-files.txt"
TEST_CASE_MODULES = "input_data_from_cts/testcases-modules.txt"
INPUT_DEPENDENCIES_FOR_CTS_TXT = 'input_data_from_cts/cts-deps-from-static_code_analysis.txt'
req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
section_id_re_str = "[\[>][\d+\.]+\d+"
full_key_string_for_re = section_id_re_str+'/' + req_id_re_str
# FULL_KEY_RE_WITH_ANCHOR = '>(?:[0-9]{1,3}(</a>)?.)' + req_id_re_str
METHOD_RE = '(\w+?)\(\)'
SECTION_ID_RE_STR = "(?:(\d{1,2}\.)+\d)"

java_methods_re_str = '(?:[a-zA-Z]\w+\() ?\w* ?\)'
java_object_re_str = '(?:[a-zA-Z]\w+\.)+[a-zA-Z_][a-zA-Z]+'
java_defines_str = '[A-Z][A-Z0-9]{2,20}[_A-Z0-9]{0,40}'
find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
spurious_terms = { '', "", " ", ' ',"\"","\"\"", '()', ')', '(', ':', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0','.',';','\,'}
cdd_common_words = {'Requirement', 'Android', 'same', 'Types', 'H:', 'The', 'implementations)', 'device',
                    'condition',
                    'Condition', 'any', 'unconditional;', '-', 'SR]', 'C:', 'Type', 'Tab:', 'implementation', '1',
                    'When', 'id=',
                    'assigned', ':', '2.', 'requirement', '(Requirements', 'consists', '(see', 'This', 'Each',
                    'ID', 'assigned.', 'Device', '1st', 'section', 'Watch', 'conditional;', 'A:', '<h4',
                    '(e.g.', 'type.', 'C-0-1).', 'T:', 'condition.', 'increments', 'defined', '0.', 'within',
                    'below:',
                    'applied', 'W:''', 'party', 'earlier', 'exempted', 'MUST', 'applications', 'requirement.',
                    'Devices', ';', 'support', 'document', 'level', 'through', 'logical', 'available',
                    'implementations', 'least', 'high', 'API', 'they:', 'If', 'launched', 'third', 'range'  "MUST",
                    "SHOULD",
                    "API", 'source.android.com', 'NOT', 'SDK', 'AND', 'MAY', 'AOSP', 'STRONGLY',
                    'developer.android.com', 'Test', '@Test', 'app,data', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    '0'}
cdd_common_words_to_remove = {'Requirement', 'Android', 'same', 'Types', 'H:', 'The',
                    'Condition', 'any', 'unconditional;',
                    'When', 'id=',  'This', 'Each','defined', 'within', 'below:',
                    'applied',  'MUST',  'requirement.','API', 'they:', 'If', 'launched', 'third', 'range' 
                    "SHOULD",'source.android.com', 'NOT', 'SDK', 'AND', 'MAY', 'AOSP', 'STRONGLY',
                    'developer.android.com', 'Test', '@Test', 'app,data', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    '0'}
common_methods = {'getFile', 'super', 'get', 'close', 'set', 'test', 'using', 'value', 'more' 'open', 'getType',
                  'getMessage', 'equals', 'not', 'find', 'search', 'length', 'size', 'getName', 'ToDo', 'from',
                  'String', 'HashMap', "None", "no"}

common_english_words = {'AND', 'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on',
                        'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one',
                        'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can',
                        'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will',
                        'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
                        'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
                        'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been',
                        'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come',
                        'made', 'may', 'here', 'must'}
#
# found_in_java_source = {
#     'all', 'back', 'result', 'check', 'null', 'test', 'end', 'time', 'regular', 'able', 'start', 'Default',
#     'times', 'timestamp', 'should', 'Build', 'Remote',
#     'non', 'name', 'End', 'top', 'stop', 'class', 'Location', 'ID3', 'state', 'create', 'add', 'LOCATION_MODE',
#     '0x00', 'present', 'sent', 'broadcast', 'Callback()',
#     'Mode', 'mode', 'record', 'Method', 'app', 'previous', '800', 'call', 'connected', 'false', 'For', 'run',
#     'batching', '-1000',
#     'getName()', 'clear', 'per', 'under', 'Lock', 'disable', 'enable', 'content', 'size', 'actual', 'verify',
#     'less', 'already', 'extend', 'text)', 'reflect',
#     'signal', 'use', '2.0', 'variable', 'concurrent', 'lit', 'error', 'setting', 'expected', 'method', 'Report',
#     'scanner', 'cases', 'change', 'device)', 'match', 'receive', 'param', 'manager', '180', 'only', 'class);',
#     'Class', '200', 'bit', 'part', '(no', 'Using', 'action', 'devices)', '(generic', 'nor', 'before',
#     'appropriate', 'it;', 'press', 'provide', 'equal', 'Open', 'true', 'except', 'right', 'Project', 'over',
#     'Source', 'read', 'applicable', 'work', 'either', 'specific', 'See', 'language', 'Settings;', 'Package',
#     'limitation', 'required', 'Pack', 'limitations', 'true;', 'context', 'file',
#     'require', '(the', 'package', 'licenses', 'Unless', 'writing', '8000;', '(in', 'Filter;', 'soft', 'text;',
#     'unit', 'New', 'copy', 'types', 'type', 'function', '1000', '100', 'used', '(10', 'determine', 'met',
#     'annotation', 'fail', 'java.util.List', 'link',
#     'first', 'functionalities', 'contains', 'contain', 'All', 'off', 'called', 'list', 'feature', 'whether',
#     'implement', 'supported', 'devices', 'timeout', 'matched', 'com.android', 'tests',
#     'Service;', 'correct', 'Profile;', 'support', 'Number', 'rect', 'parameters', 'parameter', 'matching',
#     'states', 'profile)', 'position', 'begin', '10;', 'Level', 'allowed', 'more', 'Maximum', 'otherwise',
#     'milliseconds', 'Access', 'seconds', 'form', 'hidden', 'invoke', 'array', 'platform', 'Such', 'ONLY', '(by',
#     'class;', 'Simple', 'other', 'put', 'report', 'MAX', 'true);', '0x02', 'protect', 'known',
#     'flags', 'level', "won't", 'unknown', 'cause', 'matches', 'turned', 'returned', 'lose', 'Key', 'behavior',
#     'emulate', 'Can', 'Note', 'does', 'even', 'between', 'random', 'With', 'methods', 'must',
#     'target', 'ID;', 'just', 'naming', 'characters', 'address', 'Generic', 'basic', 'original', 'reported',
#     'running', 'complete', 'full', 'certain', 'based', 'away', 'want', 'once', 'real',
#     'started', 'strong', 'buffer', 'range', 'next', 'base', 'far', 'completely', 'least', 'explicit', 'or;', 'declare',
#     '(for', 'Are', 'source', 'preload', 'key', 'test('}

java_keywords = {'abstract', 'continue', 'for', 'new', 'switch', 'assert', '**', '*default', 'goto', '*', 'package',
                 'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements',
                 'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', '**', '**',
                 'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
                 'interface', 'static', 'class', 'finally', 'long', 'strictfp', '**', 'volatile', 'const', '*',
                 'float', 'native', 'super', 'while', 'void', 'include', '#include'}

license_words = "/** **/ ** Copyright 2020 The Android Open Source Project * * Licensed under the Apache License, Version 2.0 (the  License); " \
                "* you may not use this file except in compliance with the License. * You may obtain a copy of the License at ** " \
                "http: // www .apache.org/licenses/LICENSE-2.0 * * Unless required by applicable law or agreed to in writing, software * distributed under the License is distributed on an AS IS"\
                " BASIS, * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. * See the License for the specific language governing permissions and * limitations " \
                "under the License.(C) \"AS IS\" */".split(' ')

all_words_to_skip: set = set().union(common_methods).union(common_english_words) \
    .union(java_keywords) \
    .union(license_words) \
    .union(spurious_terms)

TEST_FILES_TO_DEPENDENCIES_STORAGE = 'storage/test_file_to_dependencies.pickle'
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
RESULT_COUNT = 'RESULT_COUNT'
REQUIREMENT = 'requirement'
KEY_AS_NUMBER = 'key_as_number'
TEST_AVAILABILITY = 'Test Availability'
FILE_NAME = 'file_name'
PIPELINE_FILE_NAME = 'pipeline_file_name'
PIPELINE_METHOD_TEXT = 'pipeline_method_text'
METHOD_TEXT = 'method_text'
MANUAL_SEARCH_TERMS = 'manual_search_terms'
AUTO_SEARCH_TERMS = 'auto_search_terms'
SEARCH_TERMS = 'search_terms'
NOT_SEARCH_TERMS = 'not_search_terms'
NOT_METHODS = 'not_methods'
NOT_FILES = 'not_files'
SEARCH_ROOTS = 'search_roots'
NOT_SEARCH_ROOTS = 'not_search_roots'

MODULES = 'modules'
METHODS = 'methods'
CLASS_DEFS = 'class_defs'

MODULE = 'module'
METHOD = 'method'
CLASS_DEF = 'class_def'

MATCHED_TERMS = 'matched_terms'
QUALIFIED_METHOD = 'qualified_method'
URLS = 'urls'
METHODS_STRING = 'methods_string'
MATCHED_FILES = 'matched_files'
MAX_MATCHES = 'max_matches'
MAX_MATCHES_DEFAULT = 50000
# Protect a set of columns in the row or the whole row
PROTECTED = 'protected'
SHORTENED = "Shortened"
FLAT_RESULT = 'FLAT_RESULT'
# SCRIPT_OPTIONS = 'SCRIPT_OPTIONS'
SO_ONLY_SEARCH_KEYS = "ONLY_SEARCH_KEYS"
not_annotated_test_start = "public void test"
# Used in merge_tables to populate missing fields in the the target release sheets.
current_cdd_11_header: [] = (
    [SECTION, SECTION_ID, REQ_ID, TEST_AVAILABILITY, ANNOTATION_, 'New Req for R?', 'New CTS for R?',
     CLASS_DEF, METHOD, MODULE])
ccd_12_full_header_for_ref = [SECTION, SECTION_ID, REQ_ID, TEST_AVAILABILITY, ANNOTATION_,  NEW_REQ_FOR_S_,
                              NEW_CTS_FOR_S_, CLASS_DEF, METHOD, MODULE, COMMENT_INTERNAL, "Comment (external)", "New vs Updated(Q)",
                              CTS_BUG_ID, CDD_BUG_ID, "CDD CL", AREA, SHORTEND, TEST_LEVEL, "", "external version", "", "", ""]
ccd_12_subset_target_field_header = [ANNOTATION_, NEW_REQ_FOR_S_, NEW_CTS_FOR_S_, COMMENT_INTERNAL, CTS_BUG_ID, CDD_BUG_ID,
                                     AREA, SHORTEND, TEST_LEVEL]
#  Used in create_full_table_from_cdd create a full table from the CDD, containing all the information from the CDD but not doing any processing (besides to the keys)
cdd_info_only_header: [] = (
    [SECTION, SECTION_ID, REQ_ID, KEY_AS_NUMBER, FULL_KEY, REQUIREMENT, '', '', '', '', '', '', '', '', '',
     '', ''])

# Used in several methods that take data from a table cdd_to_cts_app_header header and copy just those columns for release.
update_release_header: [] = ([TEST_AVAILABILITY, CLASS_DEF, METHOD, MODULE,COMMENT_INTERNAL,CTS_BUG_ID])

# Used because it will be natural to look at final results and update manual fields we will copy back to input source, but just those fields
update_manual_header: [] = (
    [PROTECTED, MANUAL_SEARCH_TERMS, SEARCH_ROOTS, NOT_SEARCH_TERMS, NOT_SEARCH_ROOTS, NOT_FILES, NOT_METHODS])
results_header: [] = [CLASS_DEF, METHOD, MODULE, FILE_NAME,  MATCHED_FILES, METHODS_STRING, URLS,  METHOD_TEXT,  MATCHED_TERMS,QUALIFIED_METHOD,]
# Contains all the fields that are used to review and iterate on mappings.
cdd_to_cts_app_header: [] = [SECTION, SECTION_ID, REQ_ID, FULL_KEY, KEY_AS_NUMBER, REQUIREMENT, TEST_AVAILABILITY, SEARCH_ROOTS, SEARCH_TERMS,
                             MANUAL_SEARCH_TERMS,
                             NOT_SEARCH_TERMS, NOT_FILES,MAX_MATCHES,
                             CLASS_DEFS, METHODS, MODULES,
                             PROTECTED] + results_header + ccd_12_subset_target_field_header
# What data is to be copied from each row to the search_info dictionary
fields_for_search_info_header: [] = update_manual_header+[REQUIREMENT,TEST_AVAILABILITY]
flat_file_header:[] = [SECTION, SECTION_ID, REQ_ID, FULL_KEY,MANUAL_SEARCH_TERMS,  REQUIREMENT,TEST_AVAILABILITY,CLASS_DEF, METHOD, MODULE, MATCHED_TERMS,METHODS_STRING, SEARCH_TERMS, FILE_NAME, COMMENT_INTERNAL,CTS_BUG_ID,TEST_LEVEL]

table_delimiter = '\t'
table_dialect = 'excel-tab'
table_newline = ''
table_encoding = 'UTF-8'
table_lineterminator = table_newline
re_tag = "re_tag:"


def set_cts_path():
    os.environ['CTS_SOURCE_ROOT'] = CTS_SOURCE_ROOT
    os.environ['USER_HOME'] = '~/'
    os.environ['PROJECT_DIR'] = CTS_SOURCE_ROOT


if __name__ == '__main__':
    start = time.perf_counter()
    set_cts_path()
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
