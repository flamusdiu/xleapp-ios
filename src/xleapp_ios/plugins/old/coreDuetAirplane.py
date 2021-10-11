from xleapp.html_report import Icon
from html_report.artifact_report import ArtifactHtmlReport
from helpers import timeline, tsv
from helpers.db import open_sqlite_db_readonly

from artifacts.Artifact import Artifact


class CoreDuetAireplane(ab.Artifact):

    _name = 'CoreDuet Airplane Mode'
    _search_dirs = '**/coreduetd.db'
    _category = 'CoreDuet'
    _web_icon = WebIcon.PAUSE

    def __init__(self):
        super().__init__(self)

    def get(files_found, report_folder, seeker):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute(
            """
        select
        datetime(zcreationdate+978307200,'unixepoch'),
        time(zlocaltime,'unixepoch'),
        time(zcreationdate-zlocaltime,'unixepoch'),
        case zairplanemodeon
        when "0" then "off"
        when "1" then "on"
        end
        from zcddmairplanemodeevent
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries > 0:
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3]))

            description = ''
            report = ArtifactHtmlReport('CoreDuet Airplane Mode')
            report.start_artifact_report(report_folder, 'Airplane Mode', description)
            report.add_script()
            data_headers = (
                'Create Time',
                'Local Device Time',
                'Time Zone',
                'Airplane Mode',
            )
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Coreduet Airplane Mode'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Coreduet Airplane Mode'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No data available in table')
