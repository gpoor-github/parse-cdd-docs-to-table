import json
import time

from cdd_to_cts import static_data, helpers, table_ops, data_sources
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.react import RxData, my_print
from cdd_to_cts.update_release import update_release_table_with_changes

if __name__ == '__main__':
    start = time.perf_counter()
    scr = data_sources.SourceCrawlerReducer()
    scr.create_full_table_from_cdd("output/full_cdd.csv", static_data.cdd_info_only_header)

    scr.do_cdd_html_to_cts_create_sheets("output/created_table.csv", "output/updated_table.csv",
                                         static_data.cdd_to_cts_app_header)
    rd = RxData()
    result_table = [[str]]
    final_output_file = "output/built_from_created2.csv"
    rd.main_do_create_table("input/created_output.csv",
                            final_output_file) \
        .subscribe(
        on_next=lambda table: my_print(table, "that's all folks!{} "),
        on_completed=lambda: print("completed"),
        on_error=lambda err: helpers.raise_error("in main", err))


    original_sheet_file_name1 = "data_files/CDD-11_2021-11-23-sorted.csv"
    final_output_file = "output/built_from_created2.csv"
    new_updated_table_file1 = 'output/new_updated_table_for_release.csv'
    update_release_table_with_changes(original_sheet_file_name1, final_output_file, new_updated_table_file1)

    print(" Now check final output")
    table_ops.diff_tables(original_sheet_file_name1, new_updated_table_file1)

    rs = ReadSpreadSheet()
    result, not_found, found = rs.parse_data(final_output_file)
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
