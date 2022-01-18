#  Block to comment
# android-cts-12.0_r1
import os
import re
import sys

import parser_constants
import parser_helpers
from parser_constants import req_id_re_str, full_key_string_for_re
from parser_helpers import process_section_splits_md_and_html, create_full_table_from_cdd
from path_constants import CDD_MD_ROOT


def parse_cdd_md(cdd_md_root=CDD_MD_ROOT, logging=False):
    # /Volumes/graham-ext/AndroidStudioProjects/cts
    key_to_full_requirement_text_local = dict()
    section_to_section_data = dict()
    print(cdd_md_root)
    section_count = 0
    total_requirement_count = 0
    # if not pathlib.Path(cdd_md_root).is_dir():
    #     parser_helpers.print_system_error_and_dump(f"Not directory {cdd_md_root}")
    for directory, subdirlist, filelist in os.walk(cdd_md_root):
        for sub_dir in subdirlist:
            section_re_str = '(\d{1,3}_)+'
            cdd_section_id_search_results = re.search(section_re_str, sub_dir)
            if not cdd_section_id_search_results:
                continue
            cdd_section_id = get_section_id(cdd_section_id_search_results)
            ccd_section_data = sub_dir
            section_to_section_data[cdd_section_id] = ccd_section_data

            section_count += 1
            if logging: print(sub_dir)
            for section_dir, section_sub_dir_list, section_file_list in os.walk(directory + "/" + sub_dir):
                for file in section_file_list:
                    sub_cdd_section = str(file)
                    cdd_section_id_search_results = re.search(section_re_str, sub_cdd_section)
                    if not cdd_section_id_search_results:
                        continue
                    section_count += 1

                    sub_cdd_section_id = get_section_id(cdd_section_id_search_results)
                    ccd_section_data = file.strip(".md")
                    section_to_section_data[sub_cdd_section_id] = ccd_section_data
                    md_file_contents = parser_helpers.read_file_to_string(file, section_dir + '/')
                    key_to_full_requirement_text_local[sub_cdd_section_id] = md_file_contents
                    if logging: print(sub_cdd_section_id)
                    section_md_splits = re.split("(?=###?#?)", md_file_contents)
                    for section in section_md_splits:

                        section_id_result = re.search('([0-9\.])+', section)
                        if section_id_result:
                            just_id_result = section_id_result[0]
                            cdd_section_id = just_id_result
                        remove_link_re_str = "\]\(#.+?\)"
                        section = re.sub(remove_link_re_str, "", section)
                        req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
                        match = re.match("(:?#).+(\w+)(:?\n)", section)
                        if match is not None:
                            ccd_section_data = match[0]
                            ccd_section_data = ccd_section_data.strip("#").strip("\n").replace("\\.", " ").strip()
                            section_to_section_data[sub_cdd_section_id] = ccd_section_data

                        total_requirement_count = process_section_splits_md_and_html(parser_helpers.find_full_key,
                                                                                     full_key_string_for_re,
                                                                                     cdd_section_id,
                                                                                     key_to_full_requirement_text_local,
                                                                                     req_id_splits,
                                                                                     section_count,
                                                                                     total_requirement_count,
                                                                                     section_to_section_data,
                                                                                     ccd_section_data, logging)
                        # Only build a key if you can't find any...
                        if len(req_id_splits) < 2:
                            req_id_splits = re.split("(\*\s*?\[)", str(section))

                            total_requirement_count = process_section_splits_md_and_html(
                                parser_helpers.build_composite_key, req_id_re_str, cdd_section_id,
                                key_to_full_requirement_text_local, req_id_splits,
                                section_count, total_requirement_count, section_to_section_data, ccd_section_data,
                                logging)
    return key_to_full_requirement_text_local, section_to_section_data


def get_section_id(cdd_section_id_search_results: []):
    cdd_section_id = cdd_section_id_search_results[0]
    cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
    cdd_section_id = cdd_section_id.replace('_', '.')
    return cdd_section_id


def get_users_aosp_dir(argv):
    """
    @param argv:
    """
    try:
        import getopt
        opts, args = getopt.getopt(argv)
    except Exception as e:
        print(f"Exception parsing command line, this is probably okay = [{str(e)}]")
    aosp_md_doc_dir = ""
    if len(argv) > 1:
        aosp_md_doc_dir = argv[1]
    if len(aosp_md_doc_dir) < 2:
        aosp_md_doc_dir = input("Enter aosp directory containing the cdd directory containing .md files.\n")
    aosp_md_doc_dir = os.path.expanduser(aosp_md_doc_dir)
    return aosp_md_doc_dir

def get_users_file_name(argv):
    """
    @param argv:
    """
    try:
        import getopt
        opts, args = getopt.getopt(argv)
    except Exception as e:
        print("Could not parse command line for file, normal will try to generate")
    file_name = ""
    if len(argv) > 2:
        file_name = argv[2]
    if len(file_name) < 2:
        file_name = input("Enter your file_name or hit return and the app will try and generate one based on the value from git describe.\n")
    file_name = os.path.expanduser(file_name)
    return file_name



def get_md_file_name_from_git_describe(git_root):
    import subprocess
    import parser_helpers
    description = "generic_md_parsing_file_name"
    try:
        result = subprocess.run(['git', 'describe'], cwd=git_root, stdout=subprocess.PIPE)
        description = str(result.stdout, 'utf-8').strip("\n")
    except Exception as e:
        parser_helpers.print_system_error_and_dump(f"failed to git describe on {git_root}", e)
    pass
    file_name = description + ".tsv"
    print(f" Your md file will be [{file_name}]")
    return file_name


def do_parse_cdd_md_creat_file(file_name,
                               is_keep_section_headers=False):
    _key_to_full_requirement_text_local, _section_to_section_data = parse_cdd_md(root_folder)
    create_full_table_from_cdd(_key_to_full_requirement_text_local, _key_to_full_requirement_text_local.keys(),
                               _section_to_section_data,
                               f"../output/{file_name}", parser_constants.cdd_info_only_header, is_keep_section_headers)
    print(len(_key_to_full_requirement_text_local))


if __name__ == '__main__':
    root_folder = get_users_aosp_dir(sys.argv)
    local_file_name = get_users_file_name(sys.argv)
    if len(local_file_name) < 2:
        local_file_name = get_md_file_name_from_git_describe(root_folder)
    do_parse_cdd_md_creat_file(local_file_name, False)
