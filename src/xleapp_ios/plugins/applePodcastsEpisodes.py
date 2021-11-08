from xleapp import Artifact, Search, WebIcon


class ApplePodcastsEpisodes(Artifact):
    def __post_init__(self):
        self.name = "Episodes"
        self.category = "Apple Podcasts"
        self.web_icon = WebIcon.PLAY_CIRCLE
        self.report_headers = (
            'Import Date',
            'Metadata Timestamp',
            'Date Last Played',
            'Play State Last Modified',
            'Download Date',
            'Play Count',
            'Author',
            'Title',
            'Subtitle',
            'Asset URL',
            'Web Page URL',
            'Duration',
            'Size',
            'Play State',
        )

    @Search("**/MTLibrary.sqlite")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                '''
                SELECT
                datetime(ZIMPORTDATE + 978307200, 'unixepoch'),
                CASE ZMETADATATIMESTAMP
                    WHEN 0 THEN ''
                    ELSE datetime(ZMETADATATIMESTAMP + 978307200, 'unixepoch')
                END,
                datetime(ZLASTDATEPLAYED + 978307200, 'unixepoch'),
                datetime(ZPLAYSTATELASTMODIFIEDDATE + 978307200, 'unixepoch'),
                datetime(ZDOWNLOADDATE + 978307200, 'unixepoch'),
                ZPLAYCOUNT,
                ZAUTHOR,
                ZTITLE,
                ZITUNESSUBTITLE,
                ZASSETURL,
                ZWEBPAGEURL,
                ZDURATION,
                ZBYTESIZE,
                ZPLAYSTATE
                FROM ZMTEPISODE
                ORDER by ZMETADATATIMESTAMP
                '''
            )

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            data_list = []
            for row in all_rows:
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
                        row[9],
                        row[10],
                        row[11],
                        row[12],
                        row[13],
                    ),
                )

        self.data = data_list
