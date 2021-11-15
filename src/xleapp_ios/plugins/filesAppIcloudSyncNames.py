from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FilesAppICloudSyncNames(Artifact):
    def __post_init__(self) -> None:
        self.name = "iCloud Sync Names"
        self.category = "Files App"
        self.report_headers = ("Name",)
        self.web_icon = WebIcon.FILE_TEXT
        self.description = 'Device names that are able to sync to iCloud Drive.'

    @Search(
        (
            "*private/var/mobile/Library/Application Support/CloudDocs/"
            "session/db/server.db"
        ),
    )
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT
                name
                FROM
                devices
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
