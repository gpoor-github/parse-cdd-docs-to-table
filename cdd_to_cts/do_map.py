import time

import table_ops
from cdd_to_cts import static_data, helpers, data_sources
from cdd_to_cts.react import RxData, my_print
from check_sheet import diff_tables_files
from data_sources_helper import create_full_table_from_cdd
from parse_cdd_md import parse_cdd_md
from static_data import CDD_MD_ROOT


def do_on_complete():
    print("completed")


def do_map_12():
    directory = "/a1_working_12/"

    cdd_12_created = f"{directory}/cdd_12_table_all_md.tsv"


    key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md(CDD_MD_ROOT)
    create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                               section_to_section_data,
                               cdd_12_created, static_data.cdd_to_cts_app_header)

    cdd_11_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/md_cdd-11.tsv"
    cdd_12_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/md_cdd_12_master.tsv"
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(cdd_12_tsv,cdd_11_tsv )
    cdd_12_todo_output_file = f"{directory}cdd_12_master_diff_md_11_output.tsv"
    table_ops.make_new_table_from_keys(dif_1_2, cdd_12_created, cdd_12_todo_output_file)
    rx_output_file = f"{directory}cdd_12_todo_created.tsv"
    # noinspection DuplicatedCode
    rd = RxData()
    rd.main_do_create_table(input_table_file=cdd_12_todo_output_file, output_file=rx_output_file) \
        .subscribe(
        on_next=lambda table: my_print(len(table), "do_map() wrote table of size{} "),
        on_completed=lambda: do_on_complete(),
        on_error=lambda err: helpers.raise_error("rx on_error do_map()", err))


def do_map_11():
    directory = "/a1_working_11/"
    cdd_11_created = f"{directory}cdd_11_table_all.tsv"
    scr = data_sources.SourceCrawlerReducer(
        md_file_root=static_data.CDD_MD_ROOT,
        global_table_input_file_built_from_requirment_md_files=cdd_11_created,
        cts_root_directory=static_data.CTS_SOURCE_ROOT,
        do_search=False)
    create_full_table_from_cdd(scr.key_to_full_requirement_text, scr.key_to_full_requirement_text, scr.section_to_data,
                                   cdd_11_created)
    cdd_12_created = f"{directory}md_12_diff_11_full_created.tsv"
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(cdd_12_created,
                                                                                                   cdd_11_created)
    cdd_11_todo_output_file = "/d1_working/cdd_11_todo_output.tsv"
    table_ops.make_new_table_from_keys(dif_2_1, cdd_11_created, cdd_11_todo_output_file)
    rx_output_file = f"{directory}cdd_11_to_12_dif.tsv"
    # noinspection DuplicatedCode
    rd = RxData()
    rd.main_do_create_table(input_table_file=cdd_11_todo_output_file, output_file=rx_output_file) \
        .subscribe(
        on_next=lambda table: my_print(len(table), "do_map() wrote table of size{} "),
        on_completed=lambda: do_on_complete(),
        on_error=lambda err: helpers.raise_error("rx on_error do_map()", err))


# noinspection DuplicatedCode
if __name__ == '__main__':
    start = time.perf_counter()
    do_map_12()

    print(" Now check final output")
    # table_ops.diff_tables_files(rx_output_file, requirements_to_search_generated_table)

    # rs = ReadSpreadSheet()
    # result, not_found, found = rs.does_class_ref_file_exist(rx_output_file)
    # print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
