import json

from pathlib import Path
from re import DOTALL, search

from xleapp import Artifact, Search, WebIcon


class AppleWalletPasses(Artifact):
    def __post_init__(self):
        self.name = "Passes"
        self.category = "Apple Wallet"
        self.web_icon = WebIcon.SEND
        self.report_headers = (
            'Unique ID',
            'Organization Name',
            'Type',
            'Localized Description',
            'Pass Added',
            'Pending Delete',
            'Pass Details',
            'Front Fields Content',
            'Back Fields Content',
            'Encoded Pass',
        )

    @Search("**/nanopasses.sqlite3", "**/Cards/*.pkpass/pass.json")
    def process(self) -> None:
        for fp in self.found:
            data_list = []
            json_files: dict[str, Path] = {}
            if fp.path.suffix == ".json":
                json_path: Path = fp.path
                unique_id = search(
                    r"(?:(?<=ards/)|(?<=ards\\))(.*?)(?=.pkpass)",
                    str(json_path.parent),
                    flags=DOTALL,
                ).group(0)
                filename = f"{str(unique_id)}_{str(json_path.name)}"
                self.copyfile(json_path, filename)

                json_files[filename] = json_path / filename

            if fp.path.suffix == ".sqlite3":
                cursor = fp().cursor()
                cursor.execute(
                    """
                        SELECT UNIQUE_ID, ORGANIZATION_NAME, TYPE_ID, LOCALIZED_DESCRIPTION,
                        DATETIME(INGESTED_DATE + 978307200,'UNIXEPOCH'), DELETE_PENDING, ENCODED_PASS,
                        FRONT_FIELD_BUCKETS, BACK_FIELD_BUCKETS
                        FROM PASS
                    """,
                )

                all_rows = cursor.fetchall()

                if len(all_rows) > 0:
                    for row in all_rows:
                        json_file = json_files.get(row[0], "")
                        if json_file:
                            try:
                                with open(json_file) as json_content:
                                    json_data = json.load(json_content)
                            except Exception:
                                json_data = "Malformed data"

                            encoded_pass = str(row[6], 'utf-8', 'ignore')
                            front_field = str(row[7], 'utf-8', 'ignore')
                            back_field = str(row[8], 'utf-8', 'ignore')
                            data_list.append(
                                (
                                    row[0],
                                    row[1],
                                    row[2],
                                    row[3],
                                    row[4],
                                    row[5],
                                    json_data,
                                    front_field,
                                    back_field,
                                    encoded_pass,
                                ),
                            )

        self.data = data_list
