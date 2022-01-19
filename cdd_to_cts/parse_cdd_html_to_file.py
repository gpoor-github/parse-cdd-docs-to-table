import sys

import parse_cdd_html
import parser_constants
import parser_helpers

def do_create_table_from_html_file(full_cdd_html_file_in, table_file_name_out, is_keep_section_headers=False):
    key_to_full_requirement_text_local_, cdd_requirements_file_as_string_, section_to_section_data_ = parse_cdd_html.parse_cdd_html_to_requirements(
        full_cdd_html_file_in)
    parse_cdd_html.create_full_table_from_cdd(key_to_full_requirement_text_local_, key_to_full_requirement_text_local_,
                               section_to_section_data_,
                               table_file_name_out, parser_constants.cdd_info_only_header, is_keep_section_headers)
    return table_file_name_out

def main(argv):

   local_html_file_name_in = parser_helpers.get_users_file_name(sys.argv,1,"Enter the path to the HTML file to parse.")
   local_table_file_name_out = parser_helpers.get_users_file_name(sys.argv,2,"Enter the name of the table output file")

   return do_create_table_from_html_file(local_html_file_name_in, local_table_file_name_out)

if __name__ == '__main__':
    created_table_file_name= main(sys.argv)

