import datetime

from xleapp import Artifact, Search, WebIcon


class FilesAppIcloudClientItems(Artifact):
    def __post_init__(self) -> None:
        self.name = "iCloud Client Items"
        self.category = "Files App"
        self.report_headers = ("Birthtime", "Filename", "Version Modified Time")
        self.web_icon = WebIcon.FILE_TEXT
        self.description = "Items stored in iCloud Drive with metadata about files."

    @Search(
        (
            "*private/var/mobile/Library/Application Support/CloudDocs/"
            "session/db/client.db"
        ),
    )
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
               SELECT
                item_birthtime,
                item_filename,
                version_mtime
                FROM
                client_items
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    birth_time = datetime.datetime.fromtimestamp(row["item_birthtime"])
                    version_m_time = datetime.datetime.fromtimestamp(row["version_mtime"])
                    self.data.append((birth_time, row["item_filename"], version_m_time))
