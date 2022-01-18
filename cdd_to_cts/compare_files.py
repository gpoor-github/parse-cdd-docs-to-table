import ntpath
import sys


def get_file_names(argv):
        try:
            import getopt
            opts, args = getopt.getopt(argv)
        except Exception as e:
            print("Could not parse command line, enter the android files ")
        file_1 = ""
        file_2 = ""

        if len(argv) > 1:
            file_1 = argv[1]
        if len(argv) > 2:
            file_2 = argv[2]
        if len(file_1) < 1:
            file_1 = input("Enter the first file you want to compare:\n")
        if len(file_2) < 1:
            file_2 = input(f"Enter the second file you want to compare to file {file_1}:\n")
        if len(file_1) < 1:
            file_1 = input("Enter the first file you want to compare:\n")

        return file_1, file_2


def diff_table_files_and_create_diff_file(argv):
    file1, file2 =  get_file_names(argv)
    import check_sheet
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = check_sheet.diff_tables_files(file1, file2)
    name_part1 = ntpath.basename(file1).strip(".tsv")
    name_part2 = ntpath.basename(file2).strip(".tsv")

    output_file= f"../output/diff_{name_part1}_vs_{name_part2}.tsv"
    from cdd_to_cts import table_ops
    table_ops.make_new_table_from_keys(dif_1_2, file1,output_file )
if __name__ == '__main__':
    created_table_file_name= diff_table_files_and_create_diff_file(sys.argv)
