import csv
import re
import os


def read_table(file_name: str):
    table = []
    header = []
    keyFields: dict = dict()
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
                keyFields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, keyFields, header


class AugmentSheetWithCDDInfo:
    # !/usr/bin/python

    def find_test_files(self, reference_diction: dict):
        # traverse root directory, and list directories as dirs and files as files
        collected_value: dict = dict()
        for root, dirs, files in os.walk("/home/gpoor/cts-source"):
            path = root.split(os.sep)
            for file in files:
                if file.endswith('.java'):
                    fullpath = '{}/{}'.format(root, file)
                    path_set = set()
                    with open(fullpath, "r") as text_file:
                        file_string = text_file.read()
                        for reference in reference_diction:
                            value_set = reference_diction[reference]
                            values = str(value_set).split(' ')
                            for value in values:
                                if len(value) > 4:
                                    result = file_string.find(value)
                                    if result > -1:
                                        print('found {} in  {}'.format(value, fullpath))
                                        path_set.add(fullpath)
                            if len(path_set) > 0:
                                collected_value[reference] = ' '.join(path_set)
        return collected_value

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def clean_html_anchors(self, raw_html: str):
        return raw_html.replace("</a>", "")

    def augment_table(self):
        recs_read: dict
        key_to_full_requirement_text = dict()
        key_to_java_objects = dict()
        section_id_re_str: str = 'id="\d[\d_]*'
        key_to_urls = dict()

        foundCount = 0
        notfoundCount = 0
        keys_not_found: list = []
        req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
        key_string_re = '[(?:\d.)|\d]+/' + req_id_re_str
        table1, recs_read, header = read_table('new_recs_todo.csv')
        cdd_string: str = ""
        total_requirement_count = 0

        with open("cdd-11.html", "r") as text_file:
            cdd_string = text_file.read()

        cdd_string = self.clean_html_anchors(cdd_string)
        section_id_re_str: str = '"(?:\d{1,3}_)+'
        section_id_re = re.compile(section_id_re_str)
        cdd_sections_splits = re.findall(section_id_re_str + '.+?id=', cdd_string, flags=re.DOTALL)
        cdd_section_findall = re.findall(section_id_re, cdd_string)
        section_id_count = 0
        cdd_section_id: str = ""
        for section in cdd_sections_splits:
            if section_id_count < len(cdd_section_findall):
                cdd_section_id: str = cdd_section_findall[section_id_count]
                cdd_section_id = cdd_section_id.replace('"', '')
                cdd_section_id = cdd_section_id.rstrip('_').replace('_', '.')
            key_to_full_requirement_text[cdd_section_id] = section
           # key_string_re = '[(?:\d.)|\d]+/' + req_id_re_str
            record_id_splits = re.split(r"\s*(?:<li>)?\[",str(section)) #re findall(req_id_re_str + ".+(?=\[)|(?:id=)", section, flags=re.DOTALL)
            record_id_count = 0
            for record_id_split in record_id_splits:

                previous_value = None
                record_id_result = re.search(req_id_re_str, record_id_split)
                if record_id_result:
                    record_id = record_id_result[0].rstrip(']')
                    constructed_key = '{}/{}'.format(cdd_section_id, record_id)
                    findurl_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    found_urls = set(re.findall(findurl_re_str, record_id_split))
                    found_urls_str = ""
                    for found_url in found_urls:
                        found_urls_str += "{} ".format(found_url)
                    key_to_urls[constructed_key] = found_urls_str

                    value = self.cleanhtml(record_id_split)
                    value = re.sub("\s\s+", " ", value)
                    value = value.strip("][")
                    java_elements_aggregated_str = ""
                    java_methods_re_str = '(?:[a-zA-Z]\w+\(\))'
                    java_methods = set(re.findall(java_methods_re_str, value))
                    if len(java_methods) > 0:
                        java_elements_aggregated_str += ' '.join(java_methods) + ' '

                    java_object_re_str = '(?:[a-zA-Z]\w+\.)+(?:\w+)'
                    java_objects = set(re.findall(java_object_re_str, value))
                    java_defines_str = '[A-Z0-9]{4,29}_[_A-Z]*'
                    java_defines = set(re.findall(java_defines_str, value))

                    for java_define in java_defines:
                        java_elements_aggregated_str += "{} ".format(java_define)
                    for java_object in java_objects:
                        java_elements_aggregated_str += "{} ".format(java_object)
                    if java_elements_aggregated_str != "":
                        key_to_java_objects[constructed_key] = java_elements_aggregated_str

                    previous_value = key_to_full_requirement_text.get(constructed_key)
                    if previous_value:
                        value = '{} | {}'.format(previous_value, value)
                    else:
                        value = 'key=[{}]: [{}'.format(constructed_key, value)
                    key_to_full_requirement_text[constructed_key] = value
                    record_id_count += 1
                    total_requirement_count += 1
                    print(
                        f'section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} key [{constructed_key}] value {value} ')
                else:
                    print(f'Error red\c_id not found in [{record_id_split}]')


           # full_keys_find_all = re.findall(key_string_re, section)
            record_id_splits = re.split('(?={})'.format(key_string_re), section)
            record_id_count = 0
            for record_id_split in record_id_splits:
                previous_value = None
                record_id_result = re.search(key_string_re,record_id_split)
                if record_id_result:
                    found_full_key = record_id_result[0].rstrip(']')
                    findurl_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    found_urls = set(re.findall(findurl_re_str, record_id_split))
                    found_urls_str = ""
                    for found_url in found_urls:
                        found_urls_str += "{} ".format(found_url)
                    key_to_urls[found_full_key] = found_urls_str

                    value = self.cleanhtml(record_id_split)
                    value = re.sub("\s\s+", " ", value)
                    value = value.strip("][")
                    java_elements_aggregated_str = ""
                    java_methods_re_str = '(?:[a-zA-Z]\w+\(\))'
                    java_methods = set(re.findall(java_methods_re_str, value))
                    if len(java_methods) > 0:
                        java_elements_aggregated_str += ' '.join(java_methods) + ' '

                    java_object_re_str = '(?:[a-zA-Z]\w+\.)+(?:\w+)'
                    java_objects = set(re.findall(java_object_re_str, value))
                    java_defines_str = '[A-Z0-9]{4,29}_[_A-Z]*'
                    java_defines = set(re.findall(java_defines_str, value))

                    for java_define in java_defines:
                        java_elements_aggregated_str += "{} ".format(java_define)
                    for java_object in java_objects:
                        java_elements_aggregated_str += "{} ".format(java_object)
                    if java_elements_aggregated_str != "":
                        key_to_java_objects[found_full_key] = java_elements_aggregated_str

                    previous_value = key_to_full_requirement_text.get(found_full_key)
                    if previous_value:
                        value = '{} | {}'.format(previous_value, value)
                    else:
                        value = 'fullkeyF=[{}]: [{}'.format(found_full_key, value)
                    key_to_full_requirement_text[found_full_key] = value
                    record_id_count += 1
                    total_requirement_count += 1
                    print(
                        f'section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} key [{found_full_key}] value {value} ')
            # else:
            #         print(f'Error red\c_id not found in [{record_id_split}]')
            section_id_count += 1
            # output_file = open('augmented_output.csv', 'w') cdd_string = self.cleanhtml(cdd_string)

        keys_to_files_dict = None
        #keys_to_files_dict = self.find_test_files(key_to_java_objects)

        with open('augmented_output.csv', 'w', newline='') as csv_output_file:
            # csv_writer = csv.writer(csv_output_file, delimiter=',')

            output_count = 0
            for temp_key in recs_read:
                section_name = ""
                key_str: str = temp_key
                key_str = key_str.rstrip(".").strip(' ')

                section_data = key_to_full_requirement_text.get(key_str)
                if section_data:
                    foundCount += 1
                    table1[output_count].append('{}'.format(section_data))

                    print(f' Found[{key_str}] count {foundCount} requirement_text=[{section_data}]')
                else:
                    notfoundCount += 1
                    keys_not_found.append(key_str)
                    table1[output_count].append(
                        '! ERROR Item: {} Not found in CDD 11 https://source.android.com/compatibility/11/android-11-cdd'.format(
                            notfoundCount))
                    table1[output_count].append(key_to_urls.get(key_str))
                    print(f'NOT FOUND![{key_str}] count {notfoundCount} key  ')


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
            # csv_writer = csv.writer(csv_output_file, delimiter=',')
            output_count = 0
            for key in key_to_full_requirement_text:
                section_name = ""
                key_str: str = key
                print(f"keys from  {output_count} [{key_str}]")
                key_str = key_str.rstrip(".").strip(' ')
                key_split = key_str.split('/')
                table2.append(['','','','','','','','',''])
                table2[output_count][1]=key_split[0]
                if len(key_split) > 1:
                    table2[output_count][2]=key_split[1]
                table2[output_count][3] = key_str
                section_data = self.cleanhtml(key_to_full_requirement_text.get(key_str))
                table2[output_count].append(section_data.replace(","," ").replace("\n"," "))
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
        cdd_string = self.cleanhtml(cdd_string)
        for missing_key in keys_not_found:
            i += 1
            key_result = cdd_string.find(missing_key)

            if key_result > -1:
                Exception('Key {} not found, but it was there '.format(missing_key))
            else:  # look harder
                # print(f"\nConfirmed missing whole key {missing_key} {i}")
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
        print(f'Not {notfoundCount} Found {foundCount}  of {notfoundCount+foundCount}')


if __name__ == '__main__':
    AugmentSheetWithCDDInfo().augment_table()
