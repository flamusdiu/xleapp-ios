from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class ApplePodcastsEpisodes(Artifact):
    def __post_init__(self) -> None:
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
        self.timeline = True

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
        if all_rows:
            for row in all_rows:
                row_dict = dict_from_row(row)
                self.data.append(tuple(row_dict.values()))
