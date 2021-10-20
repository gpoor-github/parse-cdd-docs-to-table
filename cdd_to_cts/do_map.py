import time

import table_ops
from cdd_to_cts import static_data, helpers, data_sources
from cdd_to_cts.react import RxData, my_print
from check_sheet import diff_tables_files


def do_on_complete():
    print("completed")



# noinspection DuplicatedCode
if __name__ == '__main__':
    start = time.perf_counter()
    cdd_12_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html"
    cdd_12_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_table_created.tsv"

    scr = data_sources.SourceCrawlerReducer(
            cdd_requirements_html_source=cdd_12_html_file,
            global_table_input_file_build_from_html=cdd_12_created,
            cts_root_directory=static_data.CTS_SOURCE_ROOT,
            do_search=False)
    scr.create_full_table_from_cdd(scr.key_to_full_requirement_text,scr.key_to_full_requirement_text,
                                   cdd_12_created)
    cdd_11_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_table_created.tsv"

    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content=    diff_tables_files(cdd_12_created,cdd_11_created)
    cdd_12_todo_output_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_working/cdd_12_todo_output.tsv"

    table_ops.make_new_table_from_keys(dif_1_2, cdd_12_created,cdd_12_todo_output_file)

    rx_output_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_working/cdd_12_todo_created.tsv"

    # noinspection DuplicatedCode
    rd = RxData()
    rd.main_do_create_table(input_table_file=cdd_12_todo_output_file,output_file=rx_output_file) \
        .subscribe(
        on_next=lambda table: my_print(len(table), "do_map() wrote table of size{} "),
        on_completed=lambda: do_on_complete(),
        on_error=lambda err: helpers.raise_error("rx on_error do_map()", err))

    print(" Now check final output")
    # table_ops.diff_tables_files(rx_output_file, requirements_to_search_generated_table)

    # rs = ReadSpreadSheet()
    # result, not_found, found = rs.parse_data(rx_output_file)
    # print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
