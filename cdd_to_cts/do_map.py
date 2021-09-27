import json
import time

from cdd_to_cts import static_data, helpers, table_ops, data_sources
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import update_release_table_with_changes, make_new_table_with_row_keys_from_table


def do_on_complete():
    print("completed")


if __name__ == '__main__':
    start = time.perf_counter()
    full_cdd = "output/full_cdd.csv"
    created_output = static_data.DATA_SOURCES_CSV_FROM_HTML_1st
    update_output = "output/updated_table.csv"
    scr = data_sources.SourceCrawlerReducer(
        cdd_requirements_html_source=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
        global_table_input_file_build_from_html =created_output,
        cts_root_directory=static_data.CTS_SOURCE_ROOT)
    # The constructor created the file
    data_sources_table_to_update = "input/new_recs_remaining_todo.csv"
    result_table = [[str]]

    make_new_table_with_row_keys_from_table(static_data.DATA_SOURCES_CSV_FROM_HTML_1st, data_sources_table_to_update, static_data.INPUT_TABLE_FILE_NAME_RX)

    rd = RxData()
    rx_output_file ="output/rx_build_final.csv"
    rd.main_do_create_table(input_table_file=static_data.INPUT_TABLE_FILE_NAME_RX,
                            output_file=rx_output_file, output_header=static_data.cdd_to_cts_app_header) \
        .subscribe(
            on_next=lambda table: my_print(table, "that's all folks!{} "),
            on_completed=lambda:  do_on_complete(),
            on_error=lambda err: helpers.raise_error("in main", err))

    original_sheet_file_name1 = "data_files/CDD-11_2021-11-23-sorted.csv"
    new_updated_table_file1 = 'output/new_updated_table_for_release.csv'
    update_release_table_with_changes(original_sheet_file_name1, rx_output_file, new_updated_table_file1)

    print(" Now check final output")
    table_ops.diff_tables(original_sheet_file_name1, new_updated_table_file1)

    rs = ReadSpreadSheet()
    result, not_found, found = rs.parse_data(rx_output_file)
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')