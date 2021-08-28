import csv
import re
import os


def read_table(file_name: str):
    table = []
    header = []
    key_fields: dict = dict()
    with open(file_name) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                header = row
                line_count += 1
            else:
                print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                table.append(row)
                table_index = line_count - 1
                # Section,section_id,req_id
                section_value = table[table_index][header.index("Section")]
                section_id_value = table[table_index][header.index("section_id")]
                req_id_value = table[table_index][header.index("req_id")]
                class_def_value = table[table_index][header.index("class_def")]
                method_value = table[table_index][header.index("method")]
                module_value = table[table_index][header.index("module")]
                key_value = '{}/{}'.format(section_id_value.rstrip('.'), req_id_value)
                key_fields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, key_fields, header

    # find urls that may help find the tests for the requirment


def find_urls(text_to_scan_urls: str):
    find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


# find likely java objects from a text block
def find_java_objects(text_to_scan_for_java_objects: str):
    java_elements_aggregated_str = ""
    java_objects = set()

    java_methods_re_str = '(?:[a-zA-Z]\w+\( ?\w* ?\))'
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))

    java_object_re_str = '(?:[a-zA-Z]\w+\.)+(?:\w+)'
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))

    java_defines_str = '[A-Z0-9\.]{3,29}[_A-Z]*'
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))
    java_objects.difference_update(
        {"MUST", "SHOULD", "API", 'source.android.com', 'NOT', 'SDK', 'MAY', 'AOSP', 'developer.android.com'})

    return " ".join(java_objects)


def process_requirement_text(text_for_requirement_value: str, previous_value: str):
    value = cleanhtml(text_for_requirement_value)
    value = re.sub("\s\s+", " ", value)
    value = re.sub(",", ";", value)
    if previous_value:
        return '{} | {}'.format(previous_value, value)
    else:
        return value


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_html_anchors(raw_html: str):
    return raw_html.replace("</a>", "")


def find_test_files(reference_diction: dict):
    # traverse root directory, and list directories as dirs and files as files
    collected_value: dict = dict()
    for root, dirs, files in os.walk("/home/gpoor/cts-source"):
        path = root.split(os.sep)
        for file in files:
            if file.endswith('.java'):
                fullpath = '{}/{}'.format(root, file)
                with open(fullpath, "r") as text_file:
                    file_string = text_file.read()
                    for reference in reference_diction:
                        files_as_seperated_strings = collected_value.get(reference)
                        if files_as_seperated_strings:
                            path_set = set(files_as_seperated_strings.split(' '))
                        else:
                            path_set = set()
                        value_set = reference_diction[reference]
                        values = str(value_set).split(' ')
                        for value in values:
                            if len(value) > 4:
                                result = file_string.find(value)
                                if result > -1:
                                    print('{} found {} in  {}'.format(reference, value, fullpath))
                                    path_set.add(fullpath)
                        if len(path_set) > 0:
                            collected_value[reference] = ' '.join(path_set)
    return collected_value


class AugmentSheetWithCDDInfo:

    def augment_table(self):
        recs_read: dict = dict()
        key_to_full_requirement_text = dict()
        key_to_java_objects = dict()
        key_to_urls = dict()

        cdd_string, found_count, keys_not_found, notfound_count, recs_read, section_id_re_str, table1 = \
            self.parse_cdd_html_to_requirements_table(
                'Android 11 Compatibility Definition_full_original.html', key_to_full_requirement_text,
                key_to_java_objects,
                key_to_urls, recs_read)

        keys_to_files_dict = None
        # keys_to_files_dict = find_test_files(key_to_java_objects)

        with open('augmented_output.csv', 'w', newline='') as csv_output_file:
            output_count = 0
            for temp_key in recs_read:
                section_name = ""
                key_str: str = temp_key
                key_str = key_str.rstrip(".").strip(' ')

                section_data = key_to_full_requirement_text.get(key_str)
                if section_data:
                    found_count += 1
                    table1[output_count].append('{}'.format(section_data))
                    print(f' Found[{key_str}] count {found_count} requirement_text=[{section_data}]')
                else:
                    notfound_count += 1
                    keys_not_found.append(key_str)
                    table1[output_count].append(
                        '! ERROR Item: {} Not found in CDD 11 https://source.android.com/compatibility/11/android-11-cdd'.format(
                            notfound_count))
                    table1[output_count].append(key_to_urls.get(key_str))
                    print(f'NOT FOUND![{key_str}] count {notfound_count} key  ')

                table1[output_count].append(key_to_java_objects.get(key_str))
                if keys_to_files_dict:
                    filename = keys_to_files_dict.get(key_str)

                    if filename:
                        table1[output_count].append(filename)
                        class_name_split_src = filename.split('/src/')
                        if len(class_name_split_src) > 1:
                            class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")
                            table1[output_count][7] = class_name
                            table1[output_count][3] = "Yes"
                table1[output_count].append('Last augmented column')

                output_count += 1
            table_writer = csv.writer(csv_output_file)
            table_writer.writerows(table1)
            csv_output_file.close()

        table2 = list([])
        with open('created_output.csv', 'w', newline='') as csv_output_file:

            table2.append(['Section', 'section_id', 'req_id', 'Test', 'Availability', 'Annotation?' ',''New Req for R?',
                           'New CTS for R?', 'class_def', 'method', 'module',
                           'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
                           'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
                           'Test Level',
                           '', 'external version', '', '', ''])
            output_count = 1
            for key in key_to_full_requirement_text:
                section_name = ""
                key_str: str = key
                print(f"keys from  {output_count} [{key_str}]")
                key_str = key_str.rstrip(".").strip(' ')
                key_split = key_str.split('/')
                table2.append(['', '', '', '', '', '', '', '', ''])
                table2[output_count][1] = key_split[0]
                if len(key_split) > 1:
                    table2[output_count][2] = key_split[1]
                table2[output_count][3] = key_str
                section_data = key_to_full_requirement_text.get(key_str)
                table2[output_count].append(section_data.replace(",", " ").replace("\n", " "))
                table2[output_count].append(key_to_urls.get(key_str))
                table2[output_count].append(key_to_java_objects.get(key_str))
                if keys_to_files_dict:
                    filename = keys_to_files_dict.get(key_str)
                    if filename:
                        table2[output_count].append(filename)
                        class_name_split_src = filename.split('/src/')
                        if len(class_name_split_src) > 1:
                            class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")
                            table2[output_count][7] = class_name
                            table2[output_count][3] = "Yes"
                table2[output_count].append('Last augmented column')

                output_count += 1
            table_writer = csv.writer(csv_output_file)
            table_writer.writerows(table2)
            csv_output_file.close()

        i = 0
        cdd_string = clean_html_anchors(cdd_string)
        for missing_key in keys_not_found:
            i += 1
            key_result = cdd_string.find(missing_key)

            if key_result > -1:
                Exception('Key {} not found, but it was there '.format(missing_key))
            else:  # look harder
                split_key = str(missing_key).split('/')
                key_result = cdd_string.find(split_key[0])
                if key_result == -1:
                    print(f"Even SECTION {split_key[0]} of {missing_key} Not found!")
                id_rec_re_str = 'id=\"{}_[a-z].+?{}'.format(split_key[0], section_id_re_str)
                re_key_result = re.findall(id_rec_re_str, cdd_string, flags=re.DOTALL)
                if re_key_result:
                    is_id_rec_in_section = re_key_result[0].find(split_key[1])
                    if is_id_rec_in_section > -1:
                        Exception('Key {} not found, but it was there {}'.format(missing_key, re_key_result[0]))
            print(f"{missing_key} Missing {i}")
        print(f'Not {notfound_count} Found {found_count}  of {notfound_count + found_count}')

    def parse_cdd_html_to_requirements_table(self, cdd_html_file, key_to_full_requirement_text, key_to_java_objects,
                                             key_to_urls,
                                             recs_read):
        foundCount = 0
        notfoundCount = 0
        keys_not_found: list = []
        table1, recs_read, header = read_table('new_recs_todo.csv')
        cdd_string: str = ""
        total_requirement_count = 0
        with open(cdd_html_file, "r") as text_file:
            cdd_string = text_file.read()
        cdd_string = clean_html_anchors(cdd_string)
        section_id_re_str: str = '"(?:\d{1,3}_)+'
        cdd_sections_splits = re.split('(?={})'.format(section_id_re_str), cdd_string, flags=re.DOTALL)
        section_id_count = 0
        cdd_section_id: str = ""
        for section in cdd_sections_splits:
            cdd_section_id_search_results = re.search(section_id_re_str, section)
            if not cdd_section_id_search_results:
                continue
            cdd_section_id = cdd_section_id_search_results[0]
            cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
            cdd_section_id = cdd_section_id.replace('_', '.')
            key_to_full_requirement_text[cdd_section_id] = process_requirement_text(section, None)
            composite_key_string_re = "\s*(?:<li>)?\["
            req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
            req_id_splits = re.split(composite_key_string_re, str(section))
            total_requirement_count = self.process_section(self.build_composite_key, req_id_re_str, cdd_section_id,
                                                           key_to_full_requirement_text,
                                                           key_to_java_objects, key_to_urls, req_id_splits,
                                                           section_id_count, total_requirement_count)
            full_key_string_for_re = '>(?:[0-9]{1,3}.)*[0-9]?[0-9]/' + req_id_re_str
            req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
            total_requirement_count = self.process_section(self.find_full_key, full_key_string_for_re, cdd_section_id,
                                                           key_to_full_requirement_text,
                                                           key_to_java_objects, key_to_urls, req_id_splits,
                                                           section_id_count, total_requirement_count)
            section_id_count += 1
        return cdd_string, foundCount, keys_not_found, notfoundCount, recs_read, section_id_re_str, table1

    def process_section(self, record_key_method, key_string_for_re, section_id, key_to_full_requirement_text,
                        key_to_java_objects, key_to_urls,
                        record_id_splits, section_id_count, total_requirement_count):
        record_id_count = 0
        for record_id_split in record_id_splits:
            previous_value = None
            key = record_key_method(key_string_for_re, record_id_split, section_id)
            if key:
                key_to_urls[key] = find_urls(record_id_split)
                key_to_java_objects[key] = find_java_objects(record_id_split)
                key_to_full_requirement_text[key] = process_requirement_text(record_id_split,
                                                                             key_to_full_requirement_text.get(
                                                                                 key))
                record_id_count += 1
                total_requirement_count += 1
                print(
                    f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')
        return total_requirement_count

    def find_full_key(self, key_string_for_re, record_id_split, section_id):
        record_id_result = re.search(key_string_for_re, record_id_split)
        if record_id_result:
            record_id_string = record_id_result[0]
            return record_id_string.rstrip(']').lstrip('>')
        else:
            return None

    def build_composite_key(self, key_string_for_re, record_id_split, section_id):
        record_id_result = re.search(key_string_for_re, record_id_split)
        if record_id_result:
            record_id = record_id_result[0].rstrip(']')
            return '{}/{}'.format(section_id, record_id)
        else:
            return None


if __name__ == '__main__':
    AugmentSheetWithCDDInfo().augment_table()
