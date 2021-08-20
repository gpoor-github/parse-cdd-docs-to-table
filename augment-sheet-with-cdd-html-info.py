import csv
import re


def read_table(file_name: str):
    table = []
    header = []
    keyFields: dict = {"": ""}
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
                key_value = '{}/{}'.format(section_id_value.lstrip('.'), req_id_value)
                keyFields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, keyFields


class CompareSheets:

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def compare_tables(self):
        recs_read: dict
        section_to_data_dict = {"none": "[]"}
        foundCount = 0
        notfoundCount = 0
        req_id_re_str = '[ACHTW]-[0-9][0-9]?-[0-9][0-9]?'
        req_id_re = re.compile(req_id_re_str)
        section_id_re = re.compile('id="\d[\d_]*')
        #section_content_re = re.compile('id="\d[\d_]*.*<h/d>')

        # section_id_re = re.compile('\d\.\d\.(\d\.)?[\d]?')
        # section_id_re = re.compile('\d\.\d\.\d?\.?\d?')

        table1, recs_read = read_table('new-recs-11.csv')
        cdd_string: str = ""
        with open("cdd-11.html", "r") as text_file:
            cdd_string = text_file.read()

        cdd_sections_splits = re.findall('id="\d[\d_]*.+?<h', cdd_string, flags=re.DOTALL)
        cdd_section_findall = re.findall(section_id_re, cdd_string)
        total_requirement_count = 0
        section_id_count = 0
        cdd_section_id: str = ""

        for section in cdd_sections_splits:
            if section_id_count < len(cdd_section_findall):
                cdd_section_id: str = cdd_section_findall[section_id_count]
                cdd_section_id = cdd_section_id.replace('id="', '')
                cdd_section_id = cdd_section_id.rstrip('_').replace('_', '.')
            section_to_data_dict[cdd_section_id] = section

            #record_id_findall = re.findall(req_id_re, section)
            record_id_splits = re.findall('[ACHTW]-[0-9][0-9]?-[0-9][0-9]?.+?\[',section, flags=re.DOTALL)
            record_id_count = 0
            for record_id_split in record_id_splits:
                foundUrls = re.findall("(<url>https?://[^\s]+)", record_id_split)
                previous_value = None
                record_id_result= re.search('[ACHTW]-[0-9][0-9]?-[0-9][0-9]?',record_id_split)
                if record_id_result:
                    record_id = record_id_result[0].rstrip(']')
                    rec_id_key = '{}/{}'.format(cdd_section_id, record_id)
                    value = self.cleanhtml(record_id_split)
                    value = re.sub("\s\s+", " ", value)
                    value = value.strip("][")

                    previous_value = section_to_data_dict.get(rec_id_key)
                    if previous_value:
                        value = '{} | {}'.format(previous_value, value)
                    else:
                        value = 'key=[{}]: {}'.format(rec_id_key, value)
                    section_to_data_dict[rec_id_key] = value
                    record_id_count += 1
                    total_requirement_count += 1
                    print( f'section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} key [{rec_id_key}] value {value} ')
                else:
                    print(f'Error red_id not found in [{record_id_split}]')
            section_id_count += 1

        for temp_key in recs_read:
            section_name = ""
            key_str: str = temp_key
            key_str = key_str.rstrip(".").strip(' ')

            section_data = section_to_data_dict.get(key_str)
            if section_data:
                foundCount += 1
                print(f'Found#=[{foundCount}] key=[{key_str}] requirement=[{section_data}]')
            else:
                notfoundCount += 1
                print(f'Not {notfoundCount} key [{key_str}] ')

            print(f'Not {notfoundCount} found {foundCount} ')
            pass


if __name__ == '__main__':
    CompareSheets().compare_tables()
