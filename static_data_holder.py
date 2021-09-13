new_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'class_def', 'method', 'module', 'full_key',
     'requirement', 'key_as_number', 'search_terms', 'urls', 'file_name', 'manual_search_terms', 'methods_string',
     'matched'])
# Wow why doesn't that work ?: [] = (['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'Annotation?', 'New Req for R?', 'New CTS for R?',
     'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ',
     'Comment (external)', 'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external version', '', '', ''])
all_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'Annotation?', 'New Req for R?',
     'New CTS for R?', 'class_def', 'method', 'module', 'full_key',
     'requirement', 'key_as_number', 'search_terms', 'urls', 'file_name', 'manual_search_terms',
     'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
     'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external section_id', '', '', ''])
merge_header: [] = (
    ['Test Availability', 'class_def', 'method', 'module'])

add_keys_only: [] = (
    ['full_key', 'key_as_number'])
