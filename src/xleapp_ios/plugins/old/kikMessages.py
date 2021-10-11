import os
import sqlite3

from html_report.artifact_report import ArtifactHtmlReport
from packaging import version
from helpers import is_platform_windows, open_sqlite_db_readonly, timeline, tsv

import artifacts.artGlobals

from artifacts.Artifact import Artifact


class KikMessages(ab.Artifact):

    _name = 'Kik Messages'
    _search_dirs = '**/kik.sqlite*'
    _category = 'Kik'

    def get(self, files_found, seeker):

        for file_found in files_found:
            file_found = str(file_found)

            if file_found.endswith('.sqlite'):
                break

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(
            """
        SELECT
        datetime(ZKIKMESSAGE.ZRECEIVEDTIMESTAMP +978307200,'UNIXEPOCH') AS RECEIVEDTIME,
        datetime(ZKIKMESSAGE.ZTIMESTAMP +978307200,'UNIXEPOCH') as TIMESTAMP,
        ZKIKMESSAGE.ZBODY,
        case ZKIKMESSAGE.ZTYPE
            when 1 then 'rcvd'
            when 2 then 'sent'
            when 3 then 'grp admin'
            when 4 then 'grp msg'
            else 'unkn' end as 'Type',
        ZKIKMESSAGE.ZUSER,
        ZKIKUSER.ZDISPLAYNAME,
        ZKIKUSER.ZUSERNAME,
        ZKIKATTACHMENT.ZCONTENT
        from ZKIKMESSAGE
        left join ZKIKUSER on ZKIKMESSAGE.ZUSER = ZKIKUSER.Z_PK
        left join ZKIKATTACHMENT on ZKIKMESSAGE.Z_PK = ZKIKATTACHMENT.ZMESSAGE
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []

        if usageentries > 0:
            for row in all_rows:
                data_list.append(
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                )

            description = 'Kik Messages'
            report = ArtifactHtmlReport('Kik Messages')
            report.start_artifact_report(report_folder, 'Kik Messages', description)
            report.add_script()
            data_headers = (
                'Received Time',
                'Timestamp',
                'Message',
                'Type',
                'User',
                'Display Name',
                'Username',
                'Content',
            )
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Kik Messages'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Kik Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Kik data available')

        db.close()
