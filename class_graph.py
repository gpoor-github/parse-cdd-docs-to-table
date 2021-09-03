import re


def getPackageName2(class_path):
    class_path = class_path.replace("/", ".").rstrip(".java")
    split_path = class_path.split(".src.")
    if len(split_path) > 1:
        class_path = split_path[1]
    return class_path


class read_class_graph:
    re_method = re.compile('(\w+?)\(\)')
    re_class = re.compile('class (\w+)')

    def parse_(self, line_method):
        method_result = self.re_method.search(line_method)
        class_def = ""
        method = ""
        if method_result:
            method = method_result.group(0)
        else:
            class_result = self.re_class.search(line_method)
            if class_result:
                class_def = class_result.group(0)
        return class_def, method

    def parse_data(self, file_name_in: str):
        # /Volumes/graham-ext/AndroidStudioProjects/cts
        input_file = open(file_name_in, 'r')
        test_classes_to_dependent_classes: dict = dict()
        dependency_list: [] = list()
        file_as_string = input_file.read()
        file_splits = file_as_string.split('<file path=')
        target_file_name ="!Error target_file_name not found"
        for a_file_split in file_splits:
            target_file_name = re.search('\"(.+?)\"+?', a_file_split).group(0) #.replace('$PROJECT_DIR$/tests/acceleration/Android.bp"')
            dependencies_split = a_file_split.split('<dependency path=')
            dependency_list: [] = list()
            for a_dependencies_split in dependencies_split:
                dependencies_file_name = re.search('\"(.+?)+\"', a_dependencies_split).group(0)
                dependency_list.append(dependencies_file_name)
            test_classes_to_dependent_classes[target_file_name] = dependency_list
        input_file.close()
        return test_classes_to_dependent_classes


if __name__ == '__main__':
    read_class_graph().parse_data('input/android_studio_dependencies_for_cts.txt')
