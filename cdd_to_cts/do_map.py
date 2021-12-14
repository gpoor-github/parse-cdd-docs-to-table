import time

import parse_cdd_html
import parser_constants
import table_ops
from cdd_to_cts import static_data, parser_helpers, data_sources
from cdd_to_cts.react import RxData, my_print
from check_sheet import diff_tables_files
from parser_helpers import create_full_table_from_cdd


def do_on_complete():
    print("completed")


def do_map_12():
    directory = "/a1_working_12/"

    cdd_12_created = f"{directory}/cdd_12_table_all_html.tsv"

    key_to_full_requirement_text_local,cdd_requirements_file_as_string, section_to_section_data= parse_cdd_html.parse_cdd_html_to_requirements("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html")
    create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                               section_to_section_data,
                               cdd_12_created, static_data.cdd_to_cts_app_header)
    cdd_12_downloaded_2021_11_22_html = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/html_cdd_12_downloaded_2021_11_22.tsv"
    cdd_11_downloaded_html = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/html_cdd_11_downloaded.tsv"

    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(cdd_12_downloaded_2021_11_22_html,cdd_11_downloaded_html )
    cdd_12_todo_output_file = f"{directory}cdd_12_master_diff_html_11_output.tsv"
    table_ops.make_new_table_from_keys(dif_1_2, cdd_12_created, cdd_12_todo_output_file)
    rx_output_file = f"{directory}cdd_12_todo_created.tsv"
    # noinspection DuplicatedCode
    rd = RxData()
    rd.main_do_create_table(input_table_file=cdd_12_todo_output_file, output_file=rx_output_file) \
        .subscribe(
        on_next=lambda table: my_print(len(table), "do_map() wrote table of size{} "),
        on_completed=lambda: do_on_complete(),
        on_error=lambda err: parser_helpers.print_system_error_and_dump("rx on_error do_map()", err))


def do_map_11():
    directory = "/a1_working_11/"
    cdd_11_created = f"{directory}cdd_11_table_all.tsv"

    scr = data_sources.SourceCrawlerReducer(
        md_file_root=parser_constants.CDD_MD_ROOT,
        global_table_input_file_built_from_requirment_md_files=cdd_11_created,
        cts_root_directory=parser_constants.CTS_SOURCE_ROOT,
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
        on_error=lambda err: parser_helpers.print_system_error_and_dump("rx on_error do_map()", err))


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
