
#  Block to comment
import re

import static_data
from cdd_to_cts import helpers
from cdd_to_cts.helpers import build_composite_key, find_full_key, find_valid_path, find_java_objects, \
    find_urls
from data_sources_helper import process_section_splits_md_and_html


def parse_cdd_html_to_requirements(cdd_html_file, logging=False):
    key_to_full_requirement_text_local = dict()
    key_to_java_objects_local = dict()
    key_to_urls_local = dict()
    section_to_section_data = dict()
    # Should do key_to_cdd_section = dict()
    # keys_not_found: list = []
    total_requirement_count = 0

    cdd_html_file = find_valid_path(cdd_html_file)

    with open(cdd_html_file, "r") as text_file:
        print(f"CDD HTML to csv file is {cdd_html_file}")
        cdd_requirements_file_as_string = text_file.read()
        #  section_re_str: str = r'"(?:\d{1,3}_)+'
        section_marker: str = r"data-text=\"\s*"
        #section_re_str: str = section_marker + static_data.SECTION_ID_RE_STR
        cdd_sections_splits = re.split('(?={})'.format(section_marker), cdd_requirements_file_as_string,
                                       flags=re.DOTALL)
        section_count = 0
        char_count = 0
        for section in cdd_sections_splits:
            section_count += 1
            char_count += len(section)
            section = helpers.clean_html_anchors(section)


            cdd_section_id_search_results = re.search(static_data.SECTION_ID_RE_STR, section)
            if not cdd_section_id_search_results:
                continue
            cdd_section_id = cdd_section_id_search_results[0]
            cdd_section_id = cdd_section_id.replace(section_marker, '').rstrip('.')
            section_re = r"\. ([\w \.]*)\s*"  # _([a-zA-Z_]+)"
            section_to_section_data[cdd_section_id] = cdd_section_id
            section_text_result = re.search(section_re, section)
            if section_text_result:
                section_text = section_text_result[0]
                section_text = section_text.strip()
                section_to_section_data[
                    cdd_section_id] = f'{section_to_section_data[cdd_section_id]}  {section_text}'

            if '13' == cdd_section_id:
                # section 13 is "Contact us" and has characters that cause issues at lest for git
                print(f"Warning skipping section 13 {section}")
                continue
            section = helpers.process_requirement_text(section)
            key_to_full_requirement_text_local[cdd_section_id] = helpers.prepend_any_previous_value(section, key_to_full_requirement_text_local.get(cdd_section_id))
            section_and_req_re = r"(([0-9]+\.[0-9])+/(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?])"
            section_and_req_re_2 = r"[\[>][\d+\.]+\d+/(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?]"
            re_comp = re.compile(section_and_req_re_2)
            req_id_findall = re.findall(section_and_req_re_2, section,flags=re.DOTALL)
            req_id_splits = re.split('(?={})'.format(section_and_req_re_2), section)

            total_requirement_count = process_section_splits_md_and_html(find_full_key, section_and_req_re_2, cdd_section_id,
                                                                         key_to_full_requirement_text_local, req_id_splits,
                                                                         section_count, total_requirement_count,
                                                                         section_to_section_data, section_to_section_data[cdd_section_id], logging)
            # Only build a key if you can't find any...

            if len(req_id_splits) < 2:
                composite_key_string_re = r'\s*(?:<li>)?\['

                req_id_splits = re.split(composite_key_string_re, str(section))

                total_requirement_count = process_section_splits_md_and_html(build_composite_key, static_data.req_id_re_str, cdd_section_id,
                                                                             key_to_full_requirement_text_local, req_id_splits,
                                                                             section_count, total_requirement_count, section_to_section_data, section_to_section_data[cdd_section_id], logging)

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
    if len(key_to_full_requirement_text_local) < 1:
        raise SystemExit("Less than 1 requirements!? " + str(key_to_full_requirement_text_local))
    return key_to_full_requirement_text_local, key_to_java_objects_local, key_to_urls_local, cdd_requirements_file_as_string, section_to_section_data


def process_section(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                    record_id_splits, section_id_count, total_requirement_count, section_text:str="", logging=True):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_count += 1
            total_requirement_count += 1
            key_to_full_requirement_text_param[key] = helpers.prepend_any_previous_value(record_id_split,
                                                                                         key_to_full_requirement_text_param.get(key))
            if logging: print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')

    return total_requirement_count