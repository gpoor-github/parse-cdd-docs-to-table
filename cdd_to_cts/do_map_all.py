#  Block to comment

import json
import os
import time

import data_sources
import helpers
import static_data
from check_sheet import ReadSpreadSheet
from react import RxData, my_print

if __name__ == '__main__':
    start = time.perf_counter()

    print(  f"current {os.getcwd()}"  )
    full_cdd = "output/full_cdd.tsv"
    limited_cdd= "input/new_recs_remaining_todo.tsv"

    created_output = static_data.DATA_SOURCES_CSV_FROM_HTML_1st
    final_output = "output/all_results_final_output.tsv"
    scr = data_sources.SourceCrawlerReducer(
        cdd_requirements_html_source=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE, # Remember CDD_REQUIREMENTS_FROM_HTML_FILE needs to be download
        global_table_input_file_build_from_html =created_output,
        cts_root_directory=static_data.CTS_SOURCE_ROOT)
    result_table:[[str]] = list()

    rd = RxData()
    rd.main_do_create_table(input_table_file=created_output,
                            output_file=final_output) \
        .subscribe(
            on_next=lambda table: my_print(len(table), "that's all folks! {} "),
            on_completed=lambda :  my_print("that's all folks!{} "),
            on_error=lambda err: helpers.raise_error("in main", err))


    rs = ReadSpreadSheet()
    result, not_found, found = rs.parse_data(final_output)
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
