from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class GeodApplication(Artifact):
    def __post_init__(self) -> None:
        self.name = "GeoD Application"
        self.category = "Locations"
        self.web_icon = WebIcon.GRID
        self.report_headers = ("Creation Time", "Count ID", "Application")

    @Search("**/com.apple.geod/AP.db")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT count_type, app_id, createtime
                FROM mkcount
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
