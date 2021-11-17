#  Block to comment
# android-cts-12.0_r1
import os
import pathlib
import re

import helpers
from data_sources_helper import process_section
from static_data import CDD_MD_ROOT, full_key_string_for_re, composite_key_string_re, req_id_re_str, SECTION_ID_RE_STR


def parse_cdd_md(cdd_md_root:str=CDD_MD_ROOT,logging=False):
    # /Volumes/graham-ext/AndroidStudioProjects/cts
    key_to_full_requirement_text_local = dict()
    section_to_section_data = dict()
    print(cdd_md_root)
    section_count =0
    total_requirement_count =0
    if not pathlib.Path(cdd_md_root).is_dir():
        helpers.raise_error(f"Not directory {cdd_md_root}")
    for directory, subdirlist, filelist in os.walk(cdd_md_root):
        for sub_dir in subdirlist:
            section_re_str: str = '(\d{1,3}_)+'
            cdd_section_id_search_results = re.search(section_re_str, sub_dir)
            if not cdd_section_id_search_results:
                continue
            cdd_section_id = get_section_id(cdd_section_id_search_results)
            section_to_section_data[cdd_section_id] = sub_dir
            section_count+=1
            if logging: print(sub_dir)
            for section_dir, section_sub_dir_list, section_file_list in os.walk(directory+"/"+sub_dir):
                for file in section_file_list:
                    sub_cdd_section:str = str(file)
                    cdd_section_id_search_results = re.search(section_re_str, sub_cdd_section)
                    if not cdd_section_id_search_results:
                        continue
                    section_count += 1

                    sub_cdd_section_id = get_section_id(cdd_section_id_search_results)
                    section_to_section_data[sub_cdd_section_id] = file.strip(".md")
                    md_file_contents = helpers.read_file_to_string(file,section_dir+'/')
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

                        total_requirement_count = process_section(helpers.find_full_key, full_key_string_for_re, cdd_section_id,
                                                                  key_to_full_requirement_text_local, req_id_splits,
                                                                  section_count, total_requirement_count, logging)
                        # Only build a key if you can't find any...
                        if len(req_id_splits) < 2:
                            req_id_splits = re.split("(\*\s*?\[)", str(section))

                            total_requirement_count = process_section(helpers.build_composite_key, req_id_re_str, cdd_section_id,
                                                                      key_to_full_requirement_text_local, req_id_splits,
                                                                      section_count, total_requirement_count, logging)
    return key_to_full_requirement_text_local, section_to_section_data


def get_section_id(cdd_section_id_search_results:[]):

    cdd_section_id = cdd_section_id_search_results[0]
    cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
    cdd_section_id = cdd_section_id.replace('_', '.')
    return cdd_section_id

if __name__ == '__main__':
    key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md()

    print(len(key_to_full_requirement_text_local))