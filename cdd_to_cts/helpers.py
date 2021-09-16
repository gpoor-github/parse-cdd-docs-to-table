import re

from cdd_to_cts import static_data
from cdd_to_cts.static_data import find_url_re_str, java_methods_re_str, java_object_re_str, java_defines_str, \
    all_words_to_skip


def process_requirement_text(text_for_requirement_value: str, previous_value: str = None):
    value = cleanhtml(text_for_requirement_value)
    value = re.sub("\s\s+", " ", value)
    value = re.sub(",", ";", value)
    if previous_value:
        return '{} | {}'.format(previous_value, value)
    else:
        return value


def find_urls(text_to_scan_urls: str):
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


def find_java_objects(text_to_scan_for_java_objects: str) -> set:
    java_objects = set()
    #  java_objects.update(cleanhtml(process_requirement_text(text_to_scan_for_java_objects)).split(' '))
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))
    java_objects = remove_non_determinative_words(java_objects)
    java_objects.discard(None)
    return java_objects


def find_section_id(section: str) -> str:
    cdd_section_id_search_results = re.search(static_data.SECTION_ID_RE_STR, section)
    if cdd_section_id_search_results:
        cdd_section_id = cdd_section_id_search_results[0]
        cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
        cdd_section_id = cdd_section_id.replace('_', '.')
        return cdd_section_id
    return ""


def process_requirement_text(text_for_requirement_value: str, previous_value: str = None):
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


def remove_non_determinative_words(set_to_diff: set):
    return set_to_diff.difference(all_words_to_skip)
