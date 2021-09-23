import time

from cdd_to_cts import static_data, helpers
from cdd_to_cts.cdd_html_to_cts_create_sheets import create_full_table_from_cdd, do_cdd_html_to_cts_create_sheets
from cdd_to_cts.react import RxData, my_print

if __name__ == '__main__':
    start = time.perf_counter()
    create_full_table_from_cdd("output/full_cdd.csv", static_data.cdd_info_only_header)

    do_cdd_html_to_cts_create_sheets("output/created_table.csv", "output/updated_table.csv",
                                     static_data.cdd_to_cts_app_header)
    rd = RxData()
    result_table = [[str]]
    rd.main_do_create_table(f"{static_data.WORKING_ROOT}input/created_output.csv",
                            f"{static_data.WORKING_ROOT}output/built_from_created2.csv") \
        .subscribe(
        on_next=lambda table: my_print(table, "that's all folks!{} "),
        on_completed=lambda: print("completed"),
        on_error=lambda err: helpers.raise_error("in main", err))

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
