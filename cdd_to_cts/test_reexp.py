import os
import unittest

import rx
from rx import operators as ops

from cdd_to_cts import react, static_data
from cdd_to_cts.react import RxData, my_print, process_section


def my_map_dict(key: str, m_list: list) -> list:
    # mysubject = ReplaySubject()
    dict_list = list()
    for item in m_list:
        if ord(item[0]) > ord('a'):
            key = item
        else:
            dict_list.append('[{}:{}]'.format(key, item))
    return dict_list


def add_to_dic(data: str, a_dic: dict):
    splits = data.split(':', 1)
    a_dic[splits[0]] = splits[1]


def observable_to_dict(obs: rx.Observable) -> dict:
    a_dic = dict()
    obs.subscribe(on_next=lambda table_line: add_to_dic(table_line, a_dic))
    return a_dic


class MyTestCase(unittest.TestCase):
    val = "2.3.3:\"2_3_3_software\" data-text=\" 2.3.3. Software \"> 2.3.3. Software </h4> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_0_intro\">3/T-0-1] MUST declare the features <a href=\"http://developer.android.com/reference/android/content/pm/PackageManager.html#FEATURE_LEANBACK\"><code translate=\"no\" dir=\"ltr\">android.software.leanback</code> and <code translate=\"no\" dir=\"ltr\">android.hardware.type.television</code>. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_2_3_1_common_application_intents\">3.2.3.1/T-0-1] MUST preload one or more applications or service components with an intent handler, for all the public intent filter patterns defined by the following application intents listed <a href=\"https://developer.android.com/about/versions/11/reference/common-intents-30\">here. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_4_web_compatibility\">3.4.1/T-0-1] MUST provide a complete implementation of the <code translate=\"no\" dir=\"ltr\">android.webkit.Webview</code> API. </li> </ul> <p> If Android Television device implementations support a lock screen,they: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_8_user_interface_compatibility\">3.8.10/T-1-1] MUST display the Lock screen Notifications including the Media Notification Template. </li> </ul> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_8_user_interface_compatibility\">3.8.14/T-SR] Are STRONGLY RECOMMENDED to support picture-in-picture (PIP) mode multi-window. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_10_accessibility\">3.10/T-0-1] MUST support third-party accessibility services. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_10_accessibility\">3.10/T-SR] Are STRONGLY RECOMMENDED to preload accessibility services on the device comparable with or exceeding functionality of the Switch Access and TalkBack (for languages supported by the preinstalled Text-to-speech engine) accessibility services as provided in the <a href=\"https://github.com/google/talkback\">talkback open source project. </li> </ul> <p> If Television device implementations report the feature <code translate=\"no\" dir=\"ltr\">android.hardware.audio.output</code>, they: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_11_text_to_speech\">3.11/T-SR] Are STRONGLY RECOMMENDED to include a TTS engine supporting the languages available on the device. </li> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_11_text_to_speech\">3.11/T-1-1] MUST support installation of third-party TTS engines. </li> </ul> <p> Television device implementations: </p> <ul> <li>[<a href=\"https://source.android.com/compatibility/11/android-11-cdd#3_12_tv_input_framework\">3.12/T-0-1] MUST support TV Input Framework. </li> </ul> <h4 id="

    def test_something(self):
        d = "a 1 2 3 4 b 5 6 7 8 c 9 10 11"
        # react.process_section(self.val)

        # r = react.find_full_key(static_data.full_key_string_for_re, spit_val)
        # self.assertEqual(True, False)  # add assertion here

    def test_rx_table(self, ):
        rd = RxData()

        rd.build_replay_read_table("../" + static_data.INPUT_TABLE_FILE_NAME)
        rd.replay_header.subscribe(lambda v: my_print(v, "header = {}"))
        table_dic = observable_to_dict(rd.replay_input_table)
       # requirment_dic = observable_to_dict(rd.build_rx_parse_cdd_html_to_requirements())
        rd.build_rx_parse_cdd_html_to_requirements("../"+static_data.CDD_REQUIREMENTS_FROM_HTML_FILE).\
            pipe( ops.flat_map(lambda section_and_key: process_section(section_and_key)),
                  ops.map(lambda v: my_print(v)),ops.filter(lambda v:  table_dic.get(str(v).split(':',1)[0])),
                 ops.map(lambda v: my_print(v)),
                 ops.count()).\
            subscribe(lambda v: my_print(v, "matching row count = {}"))

        print("done")


if __name__ == '__main__':
    unittest.main()

    print(os.path.join(os.path.dirname(__file__),
                       '..',
                       'resources'
                       'datafile1.txt'))
