from xleapp import Artifact, Search, WebIcon


class ApplePodcastsShows(Artifact):
    def __post_init__(self):
        self.name = "Apple Podcasts - Shows"
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
        if len(all_rows) > 0:
            data_list = []
            for row in all_rows():
                data_list.append(
                    (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                    ),
                )

        self.data = data_list
