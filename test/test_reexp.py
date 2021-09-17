import os
import unittest

import rx
from rx import operators as ops

from cdd_to_cts import static_data
from cdd_to_cts.react import RxData, my_print


def my_map_dict(key: str, m_list: list) -> list:
    # mysubject = ReplaySubject()
    dict_list = list()
    for item in m_list:
        if ord(item[0]) > ord('a'):
            key = item
        else:
            dict_list.append('[{}:{}]'.format(key, item))
    return dict_list


class MyTestCase(unittest.TestCase):
    val = "2.3.3:\"2_3_3_software\" data-text=\" 2.3.3. Software \"> 2.3.3. Software </h4> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_0_intro\">3/T-0-1] MUST declare the features <a href=\"http://developer.android.com/reference/android/content/pm/PackageManager.html#FEATURE_LEANBACK\"><code translate=\"no\" dir=\"ltr\">android.software.leanback</code> and <code translate=\"no\" dir=\"ltr\">android.hardware.type.television</code>. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_2_3_1_common_application_intents\">3.2.3.1/T-0-1] MUST preload one or more applications or service components with an intent handler, for all the public intent filter patterns defined by the following application intents listed <a href=\"https://developer.android.com/about/versions/11/reference/common-intents-30\">here. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_4_web_compatibility\">3.4.1/T-0-1] MUST provide a complete implementation of the <code translate=\"no\" dir=\"ltr\">android.webkit.Webview</code> API. </li> </ul> <p> If Android Television device implementations support a lock screen,they: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_8_user_interface_compatibility\">3.8.10/T-1-1] MUST display the Lock screen Notifications including the Media Notification Template. </li> </ul> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_8_user_interface_compatibility\">3.8.14/T-SR] Are STRONGLY RECOMMENDED to support picture-in-picture (PIP) mode multi-window. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_10_accessibility\">3.10/T-0-1] MUST support third-party accessibility services. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_10_accessibility\">3.10/T-SR] Are STRONGLY RECOMMENDED to preload accessibility services on the device comparable with or exceeding functionality of the Switch Access and TalkBack (for languages supported by the preinstalled Text-to-speech engine) accessibility services as provided in the <a href=\"https://github.com/google/talkback\">talkback open source project. </li> </ul> <p> If Television device implementations report the feature <code translate=\"no\" dir=\"ltr\">android.hardware.audio.output</code>, they: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_11_text_to_speech\">3.11/T-SR] Are STRONGLY RECOMMENDED to include a TTS engine supporting the languages available on the device. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_11_text_to_speech\">3.11/T-1-1] MUST support installation of third-party TTS engines. </li> </ul> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_12_tv_input_framework\">3.12/T-0-1] MUST support TV Input Framework. </li> </ul> <h4 id="

    def test_something(self):
        d = "a 1 2 3 4 b 5 6 7 8 c 9 10 11"
        # react.process_section(self.val)

        # r = react.find_full_key(static_data.full_key_string_for_re, spit_val)
        # self.assertEqual(True, False)  # add assertion here

    def test_filtered_cdd_by_table(self, ):
        RxData().get_filtered_cdd_by_table("../" + static_data.INPUT_TABLE_FILE_NAME, "input/cdd.html").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 80))

        print("done")

    def test_rx_at_test_methods_to_words(self, ):
        RxData().get_at_test_method_words("../" + static_data.TEST_FILES_TXT). \
            pipe(ops.map(lambda v: my_print(v)),
                 ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 1370))

    def test_search_terms(self, ):
        RxData().get_search_terms("../" + static_data.CDD_REQUIREMENTS_FROM_HTML_FILE). \
            pipe(ops.map(lambda req: my_print(req, 'search in test[{}]\n'))).subscribe()

    def does_match(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.find(lambda item: self.does_match_item(target, item)))

    def does_match_item(self, target: str, term: str) -> bool:
        return target.find(term) > -1

    def test_search(self, ):
        RxData().get_at_test_method_words("../" + static_data.TEST_FILES_TXT).pipe(
            ops.map(lambda method_words: self.does_match(method_words, RxData().get_search_terms(
                "../" + static_data.CDD_REQUIREMENTS_FROM_HTML_FILE))),
            ops.map(lambda req: my_print(req, 'search result[{}]\n'))).subscribe()

    def test_cdd_html_to_requirements(self, ):
        RxData().get_cdd_html_to_requirements("../input/cdd-11-mod-test.txt").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 1370))

        print("done")


if __name__ == '__main__':
    unittest.main()

    print(os.path.join(os.path.dirname(__file__),
                       '..',
                       'resources'
                       'datafile1.txt'))
