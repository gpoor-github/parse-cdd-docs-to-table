#  Block to comment
# android-cts-12.0_r1
import os
import pathlib
import re

import parser_constants
import parser_helpers
from parser_helpers import process_section_splits_md_and_html, create_full_table_from_cdd
from parser_constants import req_id_re_str, full_key_string_for_re
from path_constants import CDD_MD_ROOT


def parse_cdd_md(cdd_md_root=CDD_MD_ROOT,logging=False):
    # /Volumes/graham-ext/AndroidStudioProjects/cts
    key_to_full_requirement_text_local = dict()
    section_to_section_data = dict()
    print(cdd_md_root)
    section_count =0
    total_requirement_count =0
    # if not pathlib.Path(cdd_md_root).is_dir():
    #     parser_helpers.print_system_error_and_dump(f"Not directory {cdd_md_root}")
    for directory, subdirlist, filelist in os.walk(cdd_md_root):
        for sub_dir in subdirlist:
            section_re_str= '(\d{1,3}_)+'
            cdd_section_id_search_results = re.search(section_re_str, sub_dir)
            if not cdd_section_id_search_results:
                continue
            cdd_section_id = get_section_id(cdd_section_id_search_results)
            ccd_section_data= sub_dir
            section_to_section_data[cdd_section_id] = ccd_section_data

            section_count+=1
            if logging: print(sub_dir)
            for section_dir, section_sub_dir_list, section_file_list in os.walk(directory+"/"+sub_dir):
                for file in section_file_list:
                    sub_cdd_section= str(file)
                    cdd_section_id_search_results = re.search(section_re_str, sub_cdd_section)
                    if not cdd_section_id_search_results:
                        continue
                    section_count += 1

                    sub_cdd_section_id = get_section_id(cdd_section_id_search_results)
                    ccd_section_data = file.strip(".md")
                    section_to_section_data[sub_cdd_section_id] = ccd_section_data
                    md_file_contents = parser_helpers.read_file_to_string(file, section_dir + '/')
                    key_to_full_requirement_text_local[sub_cdd_section_id] =md_file_contents
                    if logging: print(sub_cdd_section_id)
                    section_md_splits = re.split("(?=###?#?)",md_file_contents)
                    for section in section_md_splits:

                        section_id_result = re.search('([0-9\.])+', section)
                        if section_id_result:
                            just_id_result =section_id_result[0]
                            cdd_section_id = just_id_result
                        remove_link_re_str= "\]\(#.+?\)"
                        section = re.sub(remove_link_re_str,"",section)
                        req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
                        match = re.match("(:?#).+(\w+)(:?\n)", section)
                        if match is not None:
                            ccd_section_data = match[0]
                            ccd_section_data= ccd_section_data.strip("#").strip("\n").replace("\\."," ").strip()
                            section_to_section_data[sub_cdd_section_id] = ccd_section_data

                        total_requirement_count = process_section_splits_md_and_html(parser_helpers.find_full_key, full_key_string_for_re, cdd_section_id,
                                                                                     key_to_full_requirement_text_local, req_id_splits,
                                                                                     section_count, total_requirement_count, section_to_section_data, ccd_section_data, logging)
                        # Only build a key if you can't find any...
                        if len(req_id_splits) < 2:
                            req_id_splits = re.split("(\*\s*?\[)", str(section))

                            total_requirement_count = process_section_splits_md_and_html(parser_helpers.build_composite_key, req_id_re_str, cdd_section_id,
                                                                                         key_to_full_requirement_text_local, req_id_splits,
                                                                                         section_count, total_requirement_count, section_to_section_data, ccd_section_data, logging)
    return key_to_full_requirement_text_local, section_to_section_data


def get_section_id(cdd_section_id_search_results:[]):

    cdd_section_id = cdd_section_id_search_results[0]
    cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
    cdd_section_id = cdd_section_id.replace('_', '.')
    return cdd_section_id

if __name__ == '__main__':
    root_folder = "~/aosp_cdd"
    _key_to_full_requirement_text_local, _section_to_section_data = parse_cdd_md(root_folder)
    create_full_table_from_cdd(_key_to_full_requirement_text_local, _key_to_full_requirement_text_local.keys(),
                               _section_to_section_data,
                               "../output/md_cdd_12_master.tsv", parser_constants.cdd_info_only_header)
    print(len(_key_to_full_requirement_text_local))