import json
import time

from cdd_to_cts import static_data, helpers, table_ops, data_sources
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import update_release_table_with_changes, make_new_table_with_row_keys_from_table
from table_ops import update_manual_fields


def do_on_complete():
    print("completed")


if __name__ == '__main__':
    start = time.perf_counter()
    full_cdd = "output/full_cdd.csv"
    created_output = static_data.DATA_SOURCES_CSV_FROM_HTML_1st
    update_output = "output/updated_table.csv"
    scr = data_sources.SourceCrawlerReducer(
        cdd_requirements_html_source=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE, # Remember CDD_REQUIREMENTS_FROM_HTML_FILE needs to be download
        global_table_input_file_build_from_html =created_output,
        cts_root_directory=static_data.CTS_SOURCE_ROOT)
    result_table:[[str]] = list()
    # Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run
    make_new_table_with_row_keys_from_table(static_data.DATA_SOURCES_CSV_FROM_HTML_1st, static_data.FILTER_KEYS_DOWNLOADED_TABLE, static_data.FILTERED_TABLE_TO_SEARCH )

    rx_output_file = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT

    try:
        update_manual_fields(static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT,static_data.FILTERED_TABLE_TO_SEARCH)
    except:
        print('Failure expected the first run, when there are no result to copy back with there edits. ')

    rd = RxData()
    rd.main_do_create_table(input_table_file=static_data.FILTERED_TABLE_TO_SEARCH,
                            output_file=rx_output_file, output_header=static_data.cdd_to_cts_app_header) \
        .subscribe(
            on_next=lambda table: my_print(table, "that's all folks!{} "),
            on_completed=lambda:  do_on_complete(),
            on_error=lambda err: helpers.raise_error("in main", err))

    original_sheet_file_name1 = "data_files/CDD-11_2021-11-23-sorted.csv"
    select_assigned_reqs = "input/new_recs_remaining_todo.csv"

    update_release_table_with_changes(original_sheet_file_name1, rx_output_file, select_assigned_reqs)
    new_updated_table_file1 = 'input/new_updated_table_for_release.csv'

    print(" Now check final output")
    table_ops.diff_tables_files(original_sheet_file_name1, new_updated_table_file1)

    rs = ReadSpreadSheet()
    result, not_found, found = rs.parse_data(rx_output_file)
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')