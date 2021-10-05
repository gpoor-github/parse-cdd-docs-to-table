import json
import time

from cdd_to_cts import static_data, helpers, table_ops, data_sources
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import update_release_table_with_changes, make_new_table_with_row_keys_from_table


def do_on_complete():
    print("completed")



# Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run

def do_prep(cdd_requirements_downloaded_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
            keys_for_requirements_to_map_downloaded_csv_table: str = static_data.FILTER_KEYS_DOWNLOADED_TABLE,
            requirements_generated_from_html: str= static_data.DATA_SOURCES_CSV_FROM_HTML_1st,
            requirements_to_search_generated_table: str= static_data.FILTERED_TABLE_TO_SEARCH):

    data_sources.SourceCrawlerReducer(
        cdd_requirements_html_source=cdd_requirements_downloaded_html_file,
        # Remember CDD_REQUIREMENTS_FROM_HTML_FILE needs to be download
        global_table_input_file_build_from_html= requirements_generated_from_html,
        cts_root_directory=static_data.CTS_SOURCE_ROOT,
        do_search=True)

    # Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run
    make_new_table_with_row_keys_from_table(requirements_generated_from_html, keys_for_requirements_to_map_downloaded_csv_table,
                                            requirements_to_search_generated_table)
    return cdd_requirements_downloaded_html_file, keys_for_requirements_to_map_downloaded_csv_table,requirements_generated_from_html,requirements_to_search_generated_table

if __name__ == '__main__':
    start = time.perf_counter()
    cdd_requirements_downloaded_html_file, keys_for_requirements_to_map_downloaded_csv_table, \
    requirements_generated_from_html, requirements_to_search_generated_table=\
        do_prep()
    rx_output_file = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT

    rd = RxData()
    rd.main_do_create_table(input_table_file=requirements_to_search_generated_table,
                            output_file=rx_output_file) \
        .subscribe(
            on_next=lambda table: my_print(table, "that's all folks!{} "),
            on_completed=lambda:  do_on_complete(),
            on_error=lambda err: helpers.raise_error("in main", err))

    print(" Now check final output")
    table_ops.diff_tables_files(rx_output_file, requirements_to_search_generated_table)

    rs = ReadSpreadSheet()
    result, not_found, found = rs.parse_data(rx_output_file)
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')