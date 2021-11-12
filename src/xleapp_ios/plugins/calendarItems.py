from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class CalendarItems(Artifact):
    def __post_init__(self) -> None:
        self.name = "Calendar Items"
        self.category = "Calendar"
        self.web_icon = WebIcon.CALENDAR
        self.report_headers = (
            "Start Date",
            "Start Timezone",
            "End Date",
            "End Timezone",
            "All Day?",
            "Summary",
            "Calendar ID",
            "Last Modified",
        )
        self.timeline = True

    @Search("**/Calendar.sqlitedb")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                    Select
                    DATETIME(start_date + 978307200, 'UNIXEPOCH') as startdate,
                    start_tz,
                    DATETIME(end_date + 978307200, 'UNIXEPOCH') as enddate,
                    end_tz,
                    all_day,
                    summary,
                    calendar_id,
                    DATETIME(last_modified+ 978307200, 'UNIXEPOCH') as lastmod
                    from CalendarItem
                    order by startdate
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
