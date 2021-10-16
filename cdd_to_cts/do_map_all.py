#  Block to comment

import time

import helpers
import static_data
from do_map import do_prep, do_on_complete
from react import RxData, my_print

# Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run

if __name__ == '__main__':
    start = time.perf_counter()
    # When this is all we can use our own generated table
    downloaded_filter_table = static_data.DATA_SOURCES_CSV_FROM_HTML_1st
    all_for_cdd_12_ds = "output/cdd_12_from_data_sources_all.tsv"
    all_for_cdd_12_rx = "output/cdd_12_from_react_all.tsv"

    cdd_requirements_downloaded_html_file, keys_for_requirements_to_map_downloaded_csv_table, \
    requirements_generated_from_html, requirements_to_search_generated_table = \
        do_prep(cdd_requirements_downloaded_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
                keys_for_requirements_to_map_downloaded_csv_table=downloaded_filter_table,
                requirements_generated_from_html=static_data.DATA_SOURCES_CSV_FROM_HTML_1st,
                requirements_to_search_generated_table=all_for_cdd_12_ds)

    rd = RxData()
    rd.main_do_create_table(input_table_file=all_for_cdd_12_ds,
                            output_file=all_for_cdd_12_rx) \
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
