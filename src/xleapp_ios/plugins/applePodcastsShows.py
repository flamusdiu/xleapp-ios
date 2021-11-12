from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class ApplePodcastsShows(Artifact):
    def __post_init__(self) -> None:
        self.name = "Shows"
        self.category = "Apple Podcasts"
        self.web_icon = WebIcon.PLAY_CIRCLE
        self.report_headers = (
            'Date Added',
            'Date Last Played',
            'Date Last Updated',
            'Date Downloaded',
            'Author',
            'Title',
            'Feed URL',
            'Description',
            'Web Page URL',
        )
        self.timeline = True

    @Search("**/MTLibrary.sqlite")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                datetime(ZADDEDDATE + 978307200, 'unixepoch'),
                datetime(ZLASTDATEPLAYED + 978307200, 'unixepoch'),
                datetime(ZUPDATEDDATE + 978307200, 'unixepoch'),
                datetime(ZDOWNLOADEDDATE + 978307200, 'unixepoch'),
                ZAUTHOR,
                ZTITLE,
                ZFEEDURL,
                ZITEMDESCRIPTION,
                ZWEBPAGEURL
                from ZMTPODCAST
            """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
