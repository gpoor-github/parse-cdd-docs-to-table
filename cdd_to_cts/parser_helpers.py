import os
import re
import sys
import traceback

import path_constants
import parser_constants
import table_ops
import parser_constants
from path_constants import CTS_SOURCE_PARENT
from stackdump import stackdump


def convert_version_to_number_from_full_key(full_key):
    key_split = full_key.split('/')
    if len(key_split) == 1:
        return convert_version_to_number(key_split[0], '0.0.0')
    else:
        return convert_version_to_number(key_split[0], key_split[1])


def convert_version_to_number(section_id, requirement_id):
    section_splits = section_id.split(".")
    section_as_number = ''
    for i in range(4):
        if i < len(section_splits):
            idx = 0
            for j in range(1, -1, -1):
                if j >= len(section_splits[i]):
                    section_as_number += '0'
                else:
                    section_as_number += section_splits[i][idx]
                    idx += 1
        else:
            section_as_number += "00"

    requirement_splits = requirement_id.split("-")
    requirement_as_number = '{}'.format(ord(requirement_splits[0][-1]))
    for k in range(1, len(requirement_splits)):
        if len(requirement_splits[k]) > 1:
            requirement_as_number = "{}{}".format(requirement_as_number,requirement_splits[k])
        else:
            requirement_as_number = "{}0{}".format(requirement_as_number,requirement_splits[k])

    return "{}.{}".format(section_as_number,requirement_as_number)


def print_system_error_and_dump(message= "ERROR.. default cdd parser message.", a_exception= None):
    print(message, file=sys.stderr)
    stackdump(message)
    traceback.print_exc()
    if a_exception:
        print(str(a_exception), file=sys.stderr)
        raise a_exception
    else:
        raise Exception(message)


def raise_error_system_exit(message= "ERROR.. default cdd parser message.", a_exception= None):
    print_system_error_and_dump(message,a_exception)
    raise SystemExit(message)

def process_requirement_text(text_for_requirement_value):
    value = cleanhtml(text_for_requirement_value)
    value = remove_n_spaces_and_delimiter(value)
    return value


def find_section_id(section):
    cdd_section_id_search_results = re.search(parser_constants.SECTION_ID_RE_STR, section)
    if cdd_section_id_search_results:
        cdd_section_id = cdd_section_id_search_results[0]
        cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
        cdd_section_id = cdd_section_id.replace('_', '.')
        return cdd_section_id
    return ""


def remove_n_spaces_and_delimiter(value):
    value = re.sub("\\s\\s+", " ", value)
    value = re.sub(parser_constants.table_delimiter, " ", value)
    return value


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_html_anchors(raw_html):
    return raw_html.replace("</a>", "")


def read_file_to_string(file, prepend_path_if_needed= CTS_SOURCE_PARENT):
    full_path = file
    if not file.startswith('/') and file.find(prepend_path_if_needed) == -1:
        if not  prepend_path_if_needed.endswith("/"):
            prepend_path_if_needed = prepend_path_if_needed+"/"
        full_path = prepend_path_if_needed + file

    with open(full_path, "r") as text_file:
        file_string_raw = text_file.read()
        file_string = re.sub(' Copyright.+limitations under the License', "", file_string_raw, flags=re.DOTALL)
        text_file.close()
        return file_string


def write_file_to_string(full_path, value):

    with open(full_path, "w") as text_file:
        text_file.write(value)
        text_file.close()

def build_composite_key(key_string_for_re, record_id_split, section_id):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id = record_id_result[0].rstrip(']').strip(" ").strip(']').strip('>').strip('[')
        return '{}/{}'.format(section_id, record_id)
    else:
        return None


def find_full_key(key_string_for_re, record_id_split, section_id=None):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id_string = record_id_result[0].strip(" ").strip(']').strip('>').strip('[')
        return record_id_string
    else:
        return None


def find_valid_path(file_name):
    """
    @rtype: str
    """
    # if file_name.find(path_constants.WORKING_ROOT[0:10]) != -1:
    #     return file_name
    #
    # if file_name.find(path_constants.WORKING_ROOT) == -1:
    #     if not path_constants.WORKING_ROOT.endswith('/') and not file_name.startswith('/'):
    #         file_name = path_constants.WORKING_ROOT + '/' + file_name
    #     else:
    #         file_name = path_constants.WORKING_ROOT + file_name
    return file_name


def process_section_splits_md_and_html(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                                       record_id_splits, section_id_count, total_requirement_count, section_to_section_data, section_data, logging=False):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_count += 1
            total_requirement_count += 1
            key_to_full_requirement_text_param[key] = prepend_any_previous_value(record_id_split,
                                                                                 key_to_full_requirement_text_param.get(key))
            section_to_section_data[key] = section_data
            if logging: print(
                'key [{}] {} value [{}] section/rec_id_count {}/{} {} '
                    .format(key,key_string_for_re,key_to_full_requirement_text_param.get(key),section_id_count,record_id_count,total_requirement_count))

    return total_requirement_count


def prepend_any_previous_value(text_for_requirement_value, previous_value= None):

    if previous_value:
        return '{} | {}'.format(previous_value, text_for_requirement_value)
    else:
        return text_for_requirement_value


def create_populated_table(key_to_full_requirement_text,keys_to_find_and_write,  section_to_data, header):
    table = []
    keys_to_table_index = dict()
    table_row_index = 0
    for temp_key in keys_to_find_and_write:
        key_str = temp_key
        key_str = key_str.rstrip(".").strip(' ')
        write_new_data_line_to_table(key_str, key_to_full_requirement_text, table, table_row_index, section_to_data, header)  # test_file_to_dependencies)
        keys_to_table_index[key_str] = table_row_index
        table_row_index += 1
    return table, keys_to_table_index


def write_new_data_line_to_table( key_str, keys_to_sections, table, table_row_index,
                                 section_to_data, header = parser_constants.cdd_info_only_header, search_func=None, logging=False):

    section_data = keys_to_sections.get(key_str)
    row = list(header)
    for i in range(len(row)):
        row[i] = ''
    if len(table) <= table_row_index:
        table.append(row)

    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][header.index('Section')] = section_to_data.get(key_str)

    table[table_row_index][header.index(parser_constants.SECTION_ID)] = key_split[0]

    table[table_row_index][header.index('full_key')] = key_str
    if section_data:
        section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
        if len(section_data_cleaned) > 110000:
            print("Warning line to long truncating ")
            section_data_cleaned = section_data_cleaned[0:110000]
        table[table_row_index][header.index(parser_constants.REQUIREMENT)] = section_data_cleaned

    if len(key_split) > 1:
        table[table_row_index][header.index(parser_constants.REQ_ID)] = key_split[1]
        table[table_row_index][header.index(parser_constants.KEY_AS_NUMBER)] = convert_version_to_number(
            key_split[0], key_split[1])

        # This function takes a long time
        # This is handled in the React Side now
        if search_func:
            search_func(key_str)
    else:
        # This function handles having just a section_id
        table[table_row_index][header.index(parser_constants.KEY_AS_NUMBER)] = convert_version_to_number_from_full_key(
            key_split[0])
        if logging: print("Only a major key? {}".format(key_str))


def create_full_table_from_cdd(
        key_to_full_requirement_text: [str, str], keys_to_find_and_write,
        section_to_data,
        output_file,
        output_header= parser_constants.cdd_info_only_header,
        is_keep_section_headers=False):

    table_for_sheet, keys_to_table_indexes = create_populated_table(key_to_full_requirement_text,
                                                                    keys_to_find_and_write,
                                                                    section_to_data,
                                                                    output_header)

    print("CDD csv file to write to output is [{}] output header is [{}]".format(output_file, str(output_header)))
    if not is_keep_section_headers:
         table_for_sheet, keys_to_table_indexes = table_ops.remove_none_requirements(table_for_sheet, keys_to_table_indexes)
    from table_ops import write_table
    write_table(output_file, table_for_sheet, output_header)


def get_users_file_name(argv, arg_number=1, prompt="Enter your file_name or hit return for empty file_name:",):
    """
    @param argv:
    """

    file_name = ""
    if len(argv) > arg_number:
        file_name = argv[arg_number]
    if len(file_name) < 2:
        file_name = input(prompt+"\n")
    file_name = os.path.expanduser(file_name)
    return file_name