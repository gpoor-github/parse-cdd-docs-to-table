import re
from unittest import TestCase

import helpers
import static_data
import table_ops
from react import RxData, my_print
from table_ops import update_manual_fields, read_table_sect_and_req_key


class TestRxData(TestCase):
    def test_react_flow(self):
        input_file_name = "input/oplus-5.1.csv"
        output_file_name = "output/oplus-5.1.csv"
        rd = RxData()
        rd.max_matches = 200
        result_table = [[str]]
        output_file_name = helpers.find_valid_path(output_file_name)

        # if not input_file.exists():
        #     copyfile(static_data.WORKING_ROOT + original_source_csv, static_data.WORKING_ROOT + output_file_name)
        #     print("Expected first time through")

        rd.main_do_create_table(input_file_name, output_file_name).subscribe(
            on_next=lambda table: my_print("that's all folks!{} "),
            on_completed=lambda: print("completed"),
            on_error=lambda err: helpers.raise_error("in main", err))
        # copyfile(static_data.WORKING_ROOT+output_file_name, static_data.WORKING_ROOT+input_file_name)
        # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    #
    # def test_convert_unconvert(self):
    #     input_file_to_be_updated_with_manual_terms = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_manual_fields_test.csv"
    #     output_file_to_take_as_input_for_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/output_for_manual_fields.csv"
    #     __input_table_keyed, __input_header_keyed = table_ops.read_table_to_dictionary(
    #         input_file_to_be_updated_with_manual_terms)
    #
    #     table, table_index_dict, output_header = table_ops.convert_to_table_with_index_dict(__input_table_keyed,
    #                                                                                         __input_header_keyed)
    #     updated_table, updated_header = table_ops.update_manual_fields(table, table_index_dict, output_header,
    #                                                                    output_file_to_take_as_input_for_update)
    #     input_table_keyed, input_header_keyed = table_ops.convert_to_keyed_table_dict(updated_table,
    #                                                                                   updated_header)
    #     self.assertEqual("Yes 1 manual_search_terms",
    #                      input_table_keyed.get("5.1/H-1-1")[input_header_keyed.index(static_data.MANUAL_SEARCH_TERMS)])
    #     self.assertEqual("Yes inputfile 2",
    #                      input_table_keyed.get("5.1/H-1-2")[input_header_keyed.index("input_file_ex1")])

    def test_update_manual_fields(self):
        input_file_to_be_updated_with_manual_terms = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_manual_fields_test.csv"
        output_file_to_take_as_input_for_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/source_for_manual_fields_test.csv"
        table1_org, key_fields1_org, header1_org, duplicate_rows1_org = read_table_sect_and_req_key(
            input_file_to_be_updated_with_manual_terms, static_data.update_manual_header)
        update_header: [str] = [static_data.cdd_info_only_header]

        updated_table, update_header = update_manual_fields(table1_org, key_fields1_org, header1_org,
                                                            output_file_to_take_as_input_for_update, update_header)
        table_ops.write_table("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/test_update_table.csv",
                              updated_table, update_header)
        self.assertEqual("Yes 1 manual_search_terms",
                         updated_table[0][update_header.index(static_data.MANUAL_SEARCH_TERMS)])
        self.assertEqual("Yes inputfile 2", updated_table[1][update_header.index("input_file_ex1")])
        self.assertEqual("Yes 1 manual_search_terms", updated_table[0][update_header.index(static_data.MANUAL_SEARCH_TERMS)])
        self.assertEqual("Yes 2 manual_search_terms", updated_table[1][update_header.index(static_data.MANUAL_SEARCH_TERMS)])
        self.assertEqual("Yes 3 manual_search_terms", updated_table[2][update_header.index(static_data.MANUAL_SEARCH_TERMS)])

    def test_update_manual_fields_from_main(self):

        rd = RxData()
        rd.max_matches = 200
        result_table = [[str]]

        input_file_to_be_updated_with_manual_terms = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_manual_fields_test.csv"
        output_file_to_take_as_input_for_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/output_update_manual_fields_test_2.csv"

        rd.main_do_create_table(input_file_to_be_updated_with_manual_terms,
                                output_file_to_take_as_input_for_update).subscribe(
            on_next=lambda table: my_print(
                f"react.py main created [{output_file_to_take_as_input_for_update}] from [{input_file_to_be_updated_with_manual_terms}] "),
            on_completed=lambda: print("completed"),
            on_error=lambda err: helpers.raise_error("in main", err))

    def test_update_manual_field_new_approach(self):

        rd = RxData()
        rd.max_matches = 200
        result_table = [[str]]

        input_file_to_be_updated_with_manual_terms = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_manual_fields_test.csv"
        output_file_to_take_as_input_for_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/output_update_manual_fields_test_2.csv"

        rd.main_do_create_table(input_file_to_be_updated_with_manual_terms,
                                output_file_to_take_as_input_for_update).subscribe(
            on_next=lambda table: my_print(
                f"react.py main created [{output_file_to_take_as_input_for_update}] from [{input_file_to_be_updated_with_manual_terms}] "),
            on_completed=lambda: print("completed"),
            on_error=lambda err: helpers.raise_error("in main", err))

    def test_play2_re_search(self):
        logging = True
        search_terms = set("1.2".split(' '))
        mediapc_test_file = "1.2 3.5 192 122 12 1"
        full_text_of_file_str = mediapc_test_file

        search_terms.difference_update(static_data.spurious_terms)
        if logging:
            print(f"\nsearching {mediapc_test_file} for {str(search_terms)}")
        for matched_term in search_terms:
            matched_term = matched_term.strip(' ')
            if logging:
                print(f"\nsearching  for [{str(matched_term)}] in [{mediapc_test_file}]")
            if not matched_term:
                continue
            re_matches_from_file_search = re.findall(matched_term, full_text_of_file_str,
                                                     flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)
            matches = len(re_matches_from_file_search)
            is_found = matches > 0
            if is_found:
                print(
                    f"MATCH=[{re_matches_from_file_search[0]}] times[{str(len(re_matches_from_file_search))}]  found in  [{mediapc_test_file}]  ")
            else:
                print(f" [{str(matched_term)}] not found in  [{mediapc_test_file}]  ")
            self.assertEqual(3, matches)

            re_matches_from_file_search = re.findall(re.escape(matched_term), full_text_of_file_str,
                                                     flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)
            matches = len(re_matches_from_file_search)
            is_found = matches > 0
            if is_found:
                print(
                    f"MATCH=[{re_matches_from_file_search[0]}] times[{str(len(re_matches_from_file_search))}]  found in  [{mediapc_test_file}]  ")
            else:
                print(f" [{str(matched_term)}] not found in  [{mediapc_test_file}]  ")
            self.assertEqual(1, matches)

    def test_play_re_search(self):
        logging = True
        search_terms = set("\... H-1-3 5\.1 codec  'H-1-3' 5.1.?H-1-3 decoder Advertise video".split(' '))
        mediapc_test_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/sample_subset_java_source.java"
        full_text_of_file_str = helpers.read_file_to_string(mediapc_test_file)

        search_terms.difference_update(static_data.spurious_terms)
        if logging:
            print(f"\nsearching {mediapc_test_file} \n for {str(search_terms)}")
        for matched_term in search_terms:
            matched_term = matched_term.strip(' ')
            if logging:
                print(f"\nsearching {mediapc_test_file} \n for {str(search_terms)}")
            if not matched_term:
                continue
            re_matches_from_file_search = re.findall(matched_term, full_text_of_file_str,
                                                     flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)

            is_found = len(re_matches_from_file_search) > 0
            if is_found:
                print(f"match={re_matches_from_file_search[0]}")
            else:
                print(f"Nothing {mediapc_test_file} \n for {str(search_terms)}")

    def test_execute_search_on_file_for_terms_return_results(self):
        logging = True
        search_terms = set("\... H-1-3 5\.1 codec  'H-1-3' 5.1.?H-1-3 decoder Advertise video".split(' '))

        mediapc_test_file = "/home/gpoor/cts-source/cts/tests/tests/media/src/android/media/cts/MediaCodecCapabilitiesTest.java"
        full_text_of_file_str = helpers.read_file_to_string(mediapc_test_file)

        search_terms.difference_update(static_data.spurious_terms)
        if logging:
            print(f"\nsearching {mediapc_test_file} \n for {str(search_terms)}")
        for matched_term in search_terms:
            matched_term = matched_term.strip(' ')
            if logging:
                print(f"\nsearching {mediapc_test_file} \n for {str(search_terms)}")
            if not matched_term:
                continue
            re_matches_from_file_search = re.findall(matched_term, full_text_of_file_str,
                                                     flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)

            is_found = len(re_matches_from_file_search) > 0
            if is_found:
                print(f"match={re_matches_from_file_search[0]}")
            else:
                print(f"Nothing {mediapc_test_file} \n for {str(search_terms)}")
