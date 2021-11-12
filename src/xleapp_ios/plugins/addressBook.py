from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class AddressBook(Artifact):
    def __post_init__(self) -> None:
        self.name = "Address Book"
        self.category = "Address Book"
        self.web_icon = WebIcon.BOOK_OPEN
        self.report_headers = (
            "Contact ID",
            "Contact Number",
            "First Name",
            "Middle Name",
            "Last Name",
            "Creation Date",
            "Modification Date",
            "Storage Place",
        )

    @Search("**/AddressBook.sqlitedb")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()
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
            if all_rows:
                for row in all_rows:
                    an = str(row[0])
                    an = an.replace("b'", "")
                    an = an.replace("'", "")
                    row_dict = dict_from_row(row)
                    self.data.append((an, *tuple(row_dict.values())[1:]))
