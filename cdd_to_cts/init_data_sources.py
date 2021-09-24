import time

from cdd_to_cts import static_data, helpers
from cdd_to_cts.data_sources import SourceCrawlerReducer
from cdd_to_cts.data_sources_helper import get_file_dependencies, parse_cdd_html_to_requirements
from cdd_to_cts.helpers import build_test_cases_module_dictionary
from cdd_to_cts.static_data import CTS_SOURCE_PARENT, CDD_REQUIREMENTS_FROM_HTML_FILE, MANUAL_SEARCH_TERMS
from cdd_to_cts.table_ops import read_table


def search_files_as_strings_for_words(key: str):
    search_terms = key_to_java_objects.get(key)
    # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
    matching_file_set_out = dict()
    if search_terms:
        row = list()
        try:
            row = global_input_table[global_input_table_keys_to_index.get(key)]
        except Exception as err:
            helpers.raise_error(f" matching_file_set_out issue {matching_file_set_out}", err)

        try:
            col_idx = list(global_input_header).index(MANUAL_SEARCH_TERMS)

            if col_idx >= 0:
                if row[col_idx]:
                    manual_search_terms = set(row[col_idx].split(' '))
                    search_terms.update(manual_search_terms)
        except ValueError:
            print("warning no search manual search terms")
        pass

        for test_file in test_files_to_strings:
            file_string = test_files_to_strings.get(test_file)
            match_count = 0
            match_set = set()
            if search_terms:
                for search_term in search_terms:
                    this_terms_match_count = file_string.count(search_term)
                    if this_terms_match_count > 0:
                        match_set.add(search_term)
                        match_count += this_terms_match_count
                if len(match_set) > 0:
                    matching_file_set_out[test_file] = matching_file_set_out
    return matching_file_set_out


def diff_set_of_search_values_against_sets_of_words_from_files(count: int, file_and_path: str, word_set: set,
                                                               found_words_to_count: dict,
                                                               matching_file_set_out: dict, key: str,
                                                               search_terms: set,
                                                               start_time_file_crawl):
    if search_terms:
        result = word_set.intersection(search_terms)

        if len(result) > 0:
            count += 1
            if found_words_to_count.get(file_and_path):
                found_words_to_count[file_and_path] = len(result) + int(found_words_to_count[file_and_path])
            else:
                found_words_to_count[file_and_path] = len(result) + 5
            if (count % 100) == 0:
                end_time_file_crawl = time.perf_counter()
                print(
                    f' {len(result)} {count} time {end_time_file_crawl - start_time_file_crawl:0.4f}sec {key}  path  {file_and_path}')
            if not matching_file_set_out.get(file_and_path):
                matching_file_set_out[file_and_path] = result
            else:
                matching_file_set_out[key].update(result)

    else:
        print("warning no search terms ")
    return matching_file_set_out


def search_files_for_words(key: str):
    java_objects = key_to_java_objects.get(key)
    count = 0
    # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
    matching_file_set_out = dict()
    if not java_objects:
        return matching_file_set_out
    word_to_count = dict()
    start_time_crawl = time.perf_counter()

    row = global_input_table[global_input_table_keys_to_index.get(key)]
    col_idx = list(global_input_header).index("manual_search_terms")
    if col_idx >= 0:
        if row[col_idx]:
            manual_search_terms = set(row[col_idx].split(' '))
            java_objects.update(manual_search_terms)
    for item in files_to_words.items():
        words = item[1]
        if words:
            matching_file_set_out = diff_set_of_search_values_against_sets_of_words_from_files(count=count,
                                                                                               file_and_path=item[0],
                                                                                               word_set=words,
                                                                                               found_words_to_count=word_to_count,
                                                                                               matching_file_set_out=matching_file_set_out,
                                                                                               key=key,
                                                                                               search_terms=java_objects,
                                                                                               start_time_file_crawl=start_time_crawl)
    return matching_file_set_out


global_input_table, global_input_table_keys_to_index, global_input_header, global_duplicate_rows = read_table(
    static_data.INPUT_TABLE_FILE_NAME.replace('../', ''))
key_to_full_requirement_text, key_to_java_objects, key_to_urls, cdd_string, section_to_data = parse_cdd_html_to_requirements(
    CDD_REQUIREMENTS_FROM_HTML_FILE.replace('../', ''))

#    class DataSources:
files_to_test_cases = build_test_cases_module_dictionary(static_data.TEST_CASE_MODULES)

files_to_words, method_to_words, files_to_method_calls = SourceCrawlerReducer().get_cached_crawler_data()
testfile_dependencies_to_words = get_file_dependencies()

test_files_to_strings = SourceCrawlerReducer.make_test_file_to_dependency_strings()

if __name__ == '__main__':
    start = time.perf_counter()
    scr = SourceCrawlerReducer()
    #  scr.clear_cached_crawler_data()
    files_to_words, method_to_words, files_to_method_call = \
        scr.get_cached_crawler_data(CTS_SOURCE_PARENT)
    # remove_ubiquitous_words_code(files_to_words)
    test_files_to_strings = scr.make_test_file_to_dependency_strings()
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
