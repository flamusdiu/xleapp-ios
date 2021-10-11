import os
import plistlib
from datetime import datetime

from html_report.artifact_report import ArtifactHtmlReport
from helpers import is_platform_windows, tsv

from artifacts.Artifact import Artifact


class ICloudWifi(ab.Artifact):

    _name = 'iCloud Wifi Networks'
    _search_dirs = '**/com.apple.wifid.plist'
    _category = 'Wifi Connections'

    def get(self, files_found, seeker):
        data_list = []
        file_found = str(files_found[0])
        with open(file_found, 'rb') as fp:
            pl = plistlib.load(fp)
            timestamp = ''

            if 'values' in pl.keys():
                for key, val in pl['values'].items():
                    network_name = key

                    if type(val) == dict:
                        for key2, val2 in val.items():
                            if key2 == 'value':
                                if type(val2) == dict:
                                    if 'BSSID' in val2:
                                        bssid = str(val2['BSSID'])
                                    else:
                                        bssid = 'Not Available'

                                    if 'SSID_STR' in val2:
                                        ssid = str(val2['SSID_STR'])
                                    else:
                                        ssid = 'Not Available'

                                    if 'added_by' in val2:
                                        added_by = str(val2['added_by'])
                                    else:
                                        added_by = 'Not Available'

                                    if 'enabled' in val2:
                                        enabled = str(val2['enabled'])
                                    else:
                                        enabled = 'Not Available'

                                    if 'added_at' in val2:
                                        # Convert the value into a datetime object.
                                        my_time2 = str(val2['added_at'])
                                        datetime_obj = datetime.strptime(
                                            my_time2, '%b  %d %Y %H:%M:%S'
                                        )
                                        added_at = str(datetime_obj)
                                    else:
                                        added_at = 'Not Available'
                                    data_list.append(
                                        (bssid, ssid, added_by, enabled, added_at)
                                    )

        if len(data_list) > 0:
            report = ArtifactHtmlReport('iCloud Wifi Networks')
            report.start_artifact_report(report_folder, 'iCloud Wifi Networks')
            report.add_script()
            data_headers = ('BSSID', 'SSID', 'Added By', 'Enabled', 'Added At')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'iCloud Wifi Networks'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc('No data on iCloud WiFi networks')
