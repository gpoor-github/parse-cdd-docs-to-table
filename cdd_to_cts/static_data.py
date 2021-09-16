import os
import time

CTS_SOURCE_PARENT = "/home/gpoor/cts-source/"

CTS_SOURCE_NAME = 'cts'
CTS_SOURCE_ROOT = CTS_SOURCE_PARENT + CTS_SOURCE_NAME

CDD_REQUIREMENTS_FROM_HTML_FILE = 'input/cdd-11-mod-test.txt'
INPUT_TABLE_FILE_NAME = 'input/new_recs_remaining_todo.csv'
TEST_FILES_TXT = "input_scripts/test-files.txt"
TEST_CASE_MODULES = "input_scripts/testcases-modules.txt"
INPUT_DEPENDENCIES_FOR_CTS_TXT = 'input_scripts/cts-deps-from-test-3-trans.txt'

SECTION_ID_RE_STR = '"(?:\d{1,3}_)+'
composite_key_string_re = "\s*(?:<li>)?\["
req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
full_key_string_for_re = '>(?:[0-9]{1,3}.)*[0-9]?[0-9]/' + req_id_re_str
FULL_KEY_RE_WITH_ANCHOR = '>(?:[0-9]{1,3}(</a>)?.)*' + req_id_re_str
java_methods_re_str = '(?:[a-zA-Z]\w+\( ?\w* ?\))'
java_object_re_str = '(?:[a-zA-Z]\w+\.)+[a-zA-Z_][a-zA-Z]+'
java_defines_str = '[A-Z][A-Z0-9]{2,20}[_A-Z0-9]{0,40}'
find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
cdd_common_words = {'Requirement', 'Android', 'same', 'Types)', 'H:', 'The', 'implementations)', 'device',
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
                    "API", 'source.android.com', 'NOT', 'SDK', 'MAY', 'AOSP', 'STRONGLY',
                    'developer.android.com', 'Test', '@Test', 'app,data'}

common_methods = {'getFile', 'super', 'get', 'close', 'set', 'test', 'using', 'value', 'more' 'open', 'getType',
                  'getMessage', 'equals', 'not', 'find', 'search', 'length', 'size', 'getName', 'ToDo', 'from',
                  'String', 'HashMap', "None", "no"}

common_english_words = {'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on',
                        'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one',
                        'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can',
                        'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will',
                        'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
                        'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
                        'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been',
                        'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come',
                        'made', 'may', 'here'}

found_in_java_source = {
    'all', 'back', 'result', 'check', 'null', 'test', 'end', 'time', 'regular', 'able', 'start', 'Default',
    'times', 'timestamp', 'should', 'Build', 'Remote',
    'non', 'name', 'End', 'top', 'stop', 'class', 'Location', 'ID3', 'state', 'create', 'add', 'LOCATION_MODE',
    '0x00', 'present', 'sent', 'broadcast', 'Callback()',
    'Mode', 'mode', 'record', 'Method', 'app', 'previous', '800', 'call', 'connected', 'false', 'For', 'run',
    'batching', '-1000',
    'getName()', 'clear', 'per', 'under', 'Lock', 'disable', 'enable', 'content', 'size', 'actual', 'verify',
    'less', 'already', 'extend', 'text)', 'reflect',
    'signal', 'use', '2.0', 'variable', 'concurrent', 'lit', 'error', 'setting', 'expected', 'method', 'Report',
    'scanner', 'cases', 'change', 'device)', 'match', 'receive', 'param', 'manager', '180', 'only', 'class);',
    'Class', '200', 'bit', 'part', '(no', 'Using', 'action', 'devices)', '(generic', 'nor', 'before',
    'appropriate', 'it;', 'press', 'provide', 'equal', 'Open', 'true', 'except', 'right', 'Project', 'over',
    'Source', 'read', 'applicable', 'work', 'either', 'specific', 'See', 'language', 'Settings;', 'Package',
    'limitation', 'required', 'Pack', 'limitations', 'true;', 'context', 'file',
    'require', '(the', 'package', 'licenses', 'Unless', 'writing', '8000;', '(in', 'Filter;', 'soft', 'text;',
    'unit', 'New', 'copy', 'types', 'type', 'function', '1000', '100', 'used', '(10', 'determine', 'met',
    'annotation', 'fail', 'java.util.List', 'link',
    'first', 'functionalities', 'contains', 'contain', 'All', 'off', 'called', 'list', 'feature', 'whether',
    'implement', 'supported', 'devices', 'timeout', 'matched', 'com.android', 'tests',
    'Service;', 'correct', 'Profile;', 'support', 'Number', 'rect', 'parameters', 'parameter', 'matching',
    'states', 'profile)', 'position', 'begin', '10;', 'Level', 'allowed', 'more', 'Maximum', 'otherwise',
    'milliseconds', 'Access', 'seconds', 'form', 'hidden', 'invoke', 'array', 'platform', 'Such', 'ONLY', '(by',
    'class;', 'Simple', 'other', 'put', 'report', 'MAX', 'true);', '0x02', 'protect', 'known',
    'flags', 'level', "won't", 'unknown', 'cause', 'matches', 'turned', 'returned', 'lose', 'Key', 'behavior',
    'emulate', 'Can', 'Note', 'does', 'even', 'between', 'random', 'With', 'methods', 'must',
    'target', 'ID;', 'just', 'naming', 'characters', 'address', 'Generic', 'basic', 'original', 'reported',
    'running', 'complete', 'full', 'certain', 'based', 'away', 'want', 'once', 'real',
    'started', 'strong', 'buffer', 'range', 'next', 'base', 'far', 'completely', 'least', 'explicit', 'or;', 'declare',
    '(for', 'Are', 'source', 'preload', 'key', 'test('}

java_keywords = {'abstract', 'continue', 'for', 'new', 'switch', 'assert', '**', '*default', 'goto', '*', 'package',
                 'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements',
                 'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', '**', '**',
                 'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
                 'interface', 'static', 'class', 'finally', 'long', 'strictfp', '**', 'volatile', 'const', '*',
                 'float', 'native', 'super', 'while', 'void', 'include', '#include'}

license_words = {
    "/** **/ ** Copyright 2020 The Android Open Source Project * * Licensed under the Apache License, Version 2.0 (the  License); "
    "* you may not use this file except in compliance with the License. * You may obtain a copy of the License at ** "
    "http://www.apache.org/licenses/LICENSE-2.0 * * Unless required by applicable law or agreed to in writing, software * distributed under the License is distributed on an AS IS"
    " BASIS, * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. * See the License for the specific language governing permissions and * limitations "
    "under the License.(C) \"AS IS\" */"}

all_words_to_skip: set = set().union(cdd_common_words).union(common_methods).union(common_english_words) \
    .union(found_in_java_source) \
    .union(java_keywords) \
    .union(license_words)

TEST_FILES_TO_DEPENDENCIES_STORAGE = 'storage/test_file_to_dependencies.pickle'

new_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'class_def', 'method', 'module', 'full_key',
     'requirement', 'key_as_number', 'search_terms', 'manual_search_terms', 'matched_terms', 'file_name',
     'matched_files', 'methods_string',
     'urls'])
# Wow why doesn't that work ?: [] = (['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'Annotation?', 'New Req for R?', 'New CTS for R?',
     'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ',
     'Comment (external)', 'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external version', '', '', ''])

merge_header: [] = (
    ['Test Availability', 'class_def', 'method', 'module'])

add_keys_only: [] = (
    ['full_key', 'key_as_number'])


def set_cts_path():
    os.environ['CTS_SOURCE_ROOT'] = CTS_SOURCE_ROOT
    os.environ['USER_HOME'] = '~/'
    os.environ['PROJECT_DIR'] = CTS_SOURCE_ROOT


if __name__ == '__main__':
    start = time.perf_counter()

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
