import json
import time

from cdd_to_cts import static_data, helpers, table_ops, data_sources
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import update_release_table_with_changes

if __name__ == '__main__':
    start = time.perf_counter()
    full_cdd = "output/full_cdd.csv"
    created_output = "output/created_output.csv"
    update_output = "output/updated_table.csv"
    data_sources.global_to_data_sources_do_search=True
    scr = data_sources.SourceCrawlerReducer(
        cdd_requirements_html_source=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE.replace('../', ''),
        cts_root_directory=static_data.CTS_SOURCE_ROOT)
    scr.create_full_table_from_cdd(output_file=full_cdd, output_header=static_data.cdd_to_cts_app_header)
    scr.update_table_table_from_cdd(created_table_file=created_output, update_table_file=update_output,
                                    header=static_data.cdd_to_cts_app_header)
    rd = RxData()
    result_table = [[str]]
    rx_output_file ="output/rx_build.csv"
    rd.main_do_create_table(input_table_file=created_output,
                            output_file=rx_output_file, output_header=static_data.cdd_to_cts_app_header) \
        .subscribe(
        on_next=lambda table: my_print(table, "that's all folks!{} "),
        on_completed=lambda: print("completed"),
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
