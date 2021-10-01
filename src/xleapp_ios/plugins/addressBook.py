from dataclasses import dataclass

from xleapp.artifacts.abstract import AbstractArtifact
from xleapp.helpers.decorators import Search, timed
from xleapp.report.webicons import Icon


@dataclass
class AddressBook(AbstractArtifact):
    def __post_init__(self):
        self.name = 'Address Book'
        self.category = 'Address Book'
        self.web_icon = Icon.BOOK_OPEN
        self.report_headers = (
            'Contact ID',
            'Contact Number',
            'First Name',
            'Middle Name',
            'Last Name',
            'Creation Date',
            'Modification Date',
            'Storage Place',
        )

    @timed
    @Search('**/AddressBook.sqlitedb')
    def process(self):
        for fp in self.found:
            cursor = fp.cursor()
            cursor.execute(
                """
                SELECT
                ABPerson.ROWID,
                VALUE,
                FIRST,
                MIDDLE,
                LAST,
                DATETIME(CREATIONDATE+978307200,'UNIXEPOCH'),
                DATETIME(MODIFICATIONDATE+978307200,'UNIXEPOCH'),
                NAME
                FROM ABPerson
                LEFT OUTER JOIN ABMultiValue ON ABPerson.ROWID = ABMultiValue.RECORD_ID
                LEFT OUTER JOIN ABStore ON ABPerson.STOREID = ABStore.ROWID
                """,
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    an = str(row[0])
                    an = an.replace("b'", "")
                    an = an.replace("'", "")
                    data_list.append(
                        (
                            an,
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                            row[5],
                            row[6],
                            row[7],
                        ),
                    )
                self.data = data_list
