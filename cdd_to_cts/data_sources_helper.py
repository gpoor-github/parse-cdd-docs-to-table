import re

from cdd_to_cts import class_graph, persist, helpers
from cdd_to_cts.helpers import process_requirement_text, find_java_objects, find_urls, build_composite_key, \
    find_full_key
from cdd_to_cts.init_data_sources import key_to_java_objects
from cdd_to_cts.static_data import TEST_FILES_TO_DEPENDENCIES_STORAGE, composite_key_string_re, req_id_re_str, \
    full_key_string_for_re, CDD_REQUIREMENTS_FROM_HTML_FILE


def parse_cdd_html_to_requirements(cdd_html_file=CDD_REQUIREMENTS_FROM_HTML_FILE):
    key_to_full_requirement_text_local = dict()
    key_to_java_objects_local = dict()
    key_to_urls_local = dict()
    section_to_section_data = dict()
    # Should do key_to_cdd_section = dict()
    # keys_not_found: list = []
    total_requirement_count = 0
    with open(cdd_html_file, "r") as text_file:
        print(f"CDD HTML to csv file is {cdd_html_file}")
        cdd_requirements_file_as_string = text_file.read()
        section_re_str: str = r'"(?:\d{1,3}_)+'
        cdd_sections_splits = re.split('(?={})'.format(section_re_str), cdd_requirements_file_as_string,
                                       flags=re.DOTALL)
        section_count = 0
        for section in cdd_sections_splits:
            section = helpers.clean_html_anchors(section)
            cdd_section_id_search_results = re.search(section_re_str, section)
            if not cdd_section_id_search_results:
                continue

            cdd_section_id = cdd_section_id_search_results[0]
            cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
            cdd_section_id = cdd_section_id.replace('_', '.')
            section_to_section_data[cdd_section_id] = str(cdd_section_id_search_results[0]).replace("\"", "")
            if '13' == cdd_section_id:
                # section 13 is "Contact us" and has characters that cause issues at lest for git
                print(f"Warning skipping section 13 {section}")
                continue
            key_to_full_requirement_text_local[cdd_section_id] = process_requirement_text(section, None)
            req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)

            total_requirement_count = process_section(find_full_key, full_key_string_for_re, cdd_section_id,
                                                      key_to_full_requirement_text_local, req_id_splits,
                                                      section_count, total_requirement_count)
            # Only build a key if you can't find any...
            if len(req_id_splits) < 2:
                req_id_splits = re.split(composite_key_string_re, str(section))

                total_requirement_count = process_section(build_composite_key, req_id_re_str, cdd_section_id,
                                                          key_to_full_requirement_text_local, req_id_splits,
                                                          section_count, total_requirement_count)

            section_count += 1
        for key in key_to_full_requirement_text_local:
            requirement_text = key_to_full_requirement_text_local.get(key)
            key_to_urls_local[key] = find_urls(requirement_text)
            key_split = key.split('/')

            java_objects_temp = find_java_objects(requirement_text)
            java_objects_temp.add(key_split[0])
            if len(key_split) > 1:
                java_objects_temp.add(key_split[1])
            key_to_java_objects_local[key] = java_objects_temp
    if len(key_to_full_requirement_text_local) < 50:
        raise SystemExit("Less than 50 requirements!? " + str(key_to_full_requirement_text_local))
    return key_to_full_requirement_text_local, key_to_java_objects_local, key_to_urls_local, cdd_requirements_file_as_string, section_to_section_data


def process_section(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                    record_id_splits, section_id_count, total_requirement_count):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_split = helpers.clean_html_anchors(record_id_split)
            record_id_count += 1
            total_requirement_count += 1
            print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')
            key_to_full_requirement_text_param[key] = process_requirement_text(record_id_split,
                                                                               key_to_full_requirement_text_param.get(
                                                                                   key))
    return total_requirement_count


def get_file_dependencies():
    # if not testfile_dependencies_to_words:
    try:
        testfile_dependencies_to_words_local = persist.read(TEST_FILES_TO_DEPENDENCIES_STORAGE)
    except IOError:
        print("Could not open android_studio_dependencies_for_cts, recreating ")
        testfile_dependencies_to_words_local = class_graph.parse_dependency_file()
        persist.write(testfile_dependencies_to_words_local, TEST_FILES_TO_DEPENDENCIES_STORAGE)
    return testfile_dependencies_to_words_local





def remove_ubiquitous_words_code(word_set_dictionary: [str, set]):
    test_suite_last = ""
    word_set_last = set()
    aggregate_set = set()
    for key in word_set_dictionary:
        test_suite = str(key)[0:str(key).find("/src")]
        if test_suite_last != test_suite:
            word_set_last = aggregate_set
            test_suite_last = test_suite
            aggregate_set.clear()
            aggregate_set.update(word_set_last)

        word_set = set(word_set_dictionary.get(key))
        filtered_word_set: set = word_set.difference(word_set_last)
        word_set_dictionary[key] = filtered_word_set

    return word_set_dictionary

def convert_relative_filekey(local_file: str):
    return '\"{}\"'.format(local_file.replace('cts/', '$PROJECT_DIR$/', 1))
