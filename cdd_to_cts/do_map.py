import time

from cdd_to_cts import cdd_html_to_cts_create_sheets

if __name__ == '__main__':
    start = time.perf_counter()
    cdd_html_to_cts_create_sheets.cdd_html_to_cts_create_sheets('all')
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')