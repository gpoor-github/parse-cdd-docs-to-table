#  Block to comment
import re

from cdd_to_cts import parser_helpers, parser_constants
from cdd_to_cts.parser_helpers import build_composite_key, find_full_key, find_valid_path, \
    process_section_splits_md_and_html, create_full_table_from_cdd


def parse_cdd_html_to_requirements(cdd_html_file, logging=False):
    key_to_full_requirement_text_local = dict()
    section_to_section_data = dict()
    total_requirement_count = 0

    cdd_html_file = find_valid_path(cdd_html_file)

    with open(cdd_html_file, "r") as text_file:
        print(f"CDD HTML to csv file is {cdd_html_file}")
        cdd_requirements_file_as_string = text_file.read()
        #  section_re_str: str = r'"(?:\d{1,3}_)+'
        section_marker: str = r"data-text=\"\s*"
        # data-text=
        # section_re_str: str = section_marker + static_data.SECTION_ID_RE_STR
        cdd_sections_splits = re.split('(?={})'.format(section_marker), cdd_requirements_file_as_string,
                                       flags=re.DOTALL)
        section_count = 0
        char_count = 0
        for section in cdd_sections_splits:
            section_count += 1
            char_count += len(section)
            section = parser_helpers.clean_html_anchors(section)
            cdd_section_id_search_results = re.search(parser_constants.SECTION_ID_RE_STR, section)
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
            section = parser_helpers.process_requirement_text(section)
            key_to_full_requirement_text_local[cdd_section_id] = parser_helpers.prepend_any_previous_value(section,
                                                                                                           key_to_full_requirement_text_local.get(
                                                                                                               cdd_section_id))
            # CDD 11 had different HTML formatting section_and_req_re = r"(([0-9]+\.[0-9])+/(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?])"
            # re_comp = re.compile(section_and_req_re_2)
            # req_id_findall = re.findall(section_and_req_re_2, section, flags=re.DOTALL)

            section_and_req_re_2 = r"[\[>][\d+\.]+\d+/(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?]"
            req_id_splits = re.split('(?={})'.format(section_and_req_re_2), section)

            total_requirement_count = process_section_splits_md_and_html(find_full_key, section_and_req_re_2,
                                                                         cdd_section_id,
                                                                         key_to_full_requirement_text_local,
                                                                         req_id_splits,
                                                                         section_count, total_requirement_count,
                                                                         section_to_section_data,
                                                                         section_to_section_data[cdd_section_id],
                                                                         logging)
            # Only build a key if you can't find any...

            if len(req_id_splits) < 2:
                composite_key_string_re = r'\s*(?:<li>)?\['

                req_id_splits = re.split(composite_key_string_re, str(section))

                total_requirement_count = process_section_splits_md_and_html(build_composite_key,
                                                                             parser_constants.req_id_re_str, cdd_section_id,
                                                                             key_to_full_requirement_text_local,
                                                                             req_id_splits,
                                                                             section_count, total_requirement_count,
                                                                             section_to_section_data,
                                                                             section_to_section_data[cdd_section_id],
                                                                             logging)

            section_count += 1
    return key_to_full_requirement_text_local, cdd_requirements_file_as_string, section_to_section_data


def process_section(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                    record_id_splits, section_id_count, total_requirement_count, section_text: str = "", logging=False):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_count += 1
            total_requirement_count += 1
            key_to_full_requirement_text_param[key] = parser_helpers.prepend_any_previous_value(record_id_split,
                                                                                                key_to_full_requirement_text_param.get(
                                                                                                    key))
            if logging: print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')

    return total_requirement_count


if __name__ == '__main__':
    full_cdd_html = parser_helpers.find_valid_path(
        "input/cdd_12_download.html")

    key_to_full_requirement_text_local_, cdd_requirements_file_as_string_, section_to_section_data_ = parse_cdd_html_to_requirements(
        full_cdd_html)
    create_full_table_from_cdd(key_to_full_requirement_text_local_, key_to_full_requirement_text_local_,
                               section_to_section_data_,
                               "./output/cdd_12_gen_html.tsv", parser_constants.cdd_info_only_header)
