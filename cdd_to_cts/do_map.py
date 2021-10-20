import time

from cdd_to_cts import static_data, helpers, data_sources
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import make_new_table_with_row_keys_from_table


def do_on_complete():
    print("completed")



# noinspection DuplicatedCode
if __name__ == '__main__':
    start = time.perf_counter()
    cdd_11_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html"
    cdd_11_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_full_table_from_html.tsv"
    cdd_11_filter_by_table = cdd_11_table_generated_from_html_all #So no filter


    scr = data_sources.SourceCrawlerReducer(
            cdd_requirements_html_source=cdd_11_html_file,
            global_table_input_file_build_from_html=cdd_11_table_generated_from_html_all,
            cts_root_directory=static_data.CTS_SOURCE_ROOT,
            do_search=False)
    scr.create_full_table_from_cdd(scr.key_to_full_requirement_text,scr.key_to_full_requirement_text,
                                   cdd_11_table_generated_from_html_all)
    rx_output_file = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT

    # Remember FILTER_KEYS_DOWNLOADED_TABLE file  must exit before the program is run
    make_new_table_with_row_keys_from_table(cdd_11_table_generated_from_html_all,
                                            keys_for_requirements_to_map_downloaded_csv_table,
                                            rx_output_file)


    rd = RxData()
    rd.main_do_create_table(input_table_file=m_requirements_to_search_generated_table,
                            output_file=rx_output_file) \
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
