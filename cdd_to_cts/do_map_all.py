#  Block to comment

import time

import data_sources
import helpers
import static_data
from do_map import do_on_complete
from react import RxData, my_print

# Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run

if __name__ == '__main__':
    start = time.perf_counter()
    # When this is all we can use our own generated table
    downloaded_filter_table = static_data.DATA_SOURCES_CSV_FROM_HTML_1st
    all_for_cdd_12_ds = "output/cdd_12_from_data_sources_all.tsv"
    all_for_cdd_12_rx = "output/cdd_12_from_react_all.tsv"
    cdd_12_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_table_created.tsv"


    scr = data_sources.SourceCrawlerReducer(
            cdd_requirements_html_source=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
            global_table_input_file_build_from_html=static_data.DATA_SOURCES_CSV_FROM_HTML_1st,
            cts_root_directory=static_data.CTS_SOURCE_ROOT,
            do_search=False)
    scr.create_full_table_from_cdd(scr.key_to_full_requirement_text,scr.key_to_full_requirement_text,
                                   cdd_12_created)
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
