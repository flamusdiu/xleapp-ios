import glob
import os
import pathlib
import sqlite3

from html_report.artifact_report import ArtifactHtmlReport
from helpers import is_platform_windows, open_sqlite_db_readonly, timeline, tsv

from artifacts.Artifact import AbstractArtifact


class TileAppDisc(ab.AbstractArtifact):
    _name = 'Tile App Discovered Tiles'
    _search_dirs = '*/private/var/mobile/Containers/Shared/AppGroup/*/com.thetxleapp.tile-DiscoveredTileDB.sqlite*'
    _category = 'Accounts'

    def get(self, files_found, seeker):
        for file_found in files_found:
            file_found = str(file_found)

            if file_found.endswith('tile-DiscoveredTileDB.sqlite'):
                break

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(
            """
        SELECT
        datetime(ZLAST_MODIFIED_TIMESTAMP,'unixepoch','31 years'),
        ZTILE_UUID
        FROM
        ZTILENTITY_DISCOVEREDTILE
        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1]))

                description = 'Tile IDs seen from other users'
                report = ArtifactHtmlReport('Tile App - Discovered Tiles')
                report.start_artifact_report(
                    report_folder, 'Tile App Discovered Tiles', description
                )
                report.add_script()
                data_headers = ('Last Modified Timestamp', 'Tile UUID')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()

            tsvname = 'Tile App Discovered Tiles'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Tile Discovered Tiles'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Tile App Discovered Tiles data available')

        db.close()
