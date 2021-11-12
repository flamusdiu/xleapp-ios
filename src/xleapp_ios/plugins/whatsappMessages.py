from collections import defaultdict
from pathlib import Path

from xleapp import Artifact, Search, WebIcon, open_sqlite_db_readonly


class WhatsappMessages(Artifact):
    def __post_init__(self) -> None:
        self.name = "Whatsapp - Messages"
        self.category = "Whatsapp"
        self.report_headers = (
            "Timestamp",
            "Sender Name",
            "From ID",
            "Receiver",
            "To ID",
            "Message",
            "Attachment File",
            "Thumb",
            "Attachment Local Path",
            "Starred?",
            "Latitude",
            "Longitude",
        )
        self.web_icon = WebIcon.MESSAGE_SQUARE
        self.timeline = True

    @Search(
        "*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite",
        "*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*",
        file_names_only=True,
        return_on_first_hit=False,
    )
    def process(self):
        media_list = defaultdict(set)
        files_found = self.found.copy()
        for file_found in files_found:
            if "sqlite" not in file_found().suffix:
                media_list[file_found().stem].add(file_found())
                self.found.remove(file_found)

            if file_found().suffix == ".sqlite":
                fp = str(file_found())

        db = open_sqlite_db_readonly(fp)
        cursor = db.cursor()

        cursor.execute(
            """
            select
            datetime(ZMESSAGEDATE+978307200, 'UNIXEPOCH') as TIMESTAMP,
            ZISFROMME,
            ZPARTNERNAME,
            ZFROMJID,
            ZTOJID,
            ZWAMESSAGE.ZMEDIAITEM,
            ZTEXT,
            ZSTARRED,
            ZMESSAGETYPE,
            ZLONGITUDE,
            ZLATITUDE,
            ZMEDIALOCALPATH,
            ZXMPPTHUMBPATH
            FROM ZWAMESSAGE
            left JOIN ZWAMEDIAITEM
            on ZWAMESSAGE.Z_PK = ZWAMEDIAITEM.ZMESSAGE
            left JOIN ZWACHATSESSION
            on ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION
            """,
        )
        all_rows = cursor.fetchall()

        if all_rows:
            for row in all_rows:

                if row["ZISFROMME"] == 1:
                    sender = "Local User"
                    receiver = row["ZPARTNERNAME"]
                else:
                    sender = row["ZPARTNERNAME"]
                    receiver = "Local User"

                if row["ZMESSAGETYPE"] == 5:
                    lon = row["ZLONGITUDE"]
                    lat = row["ZLONGITUDE"]
                else:
                    lat = ""
                    lon = ""

                thumb = row["ZXMPPTHUMBPATH"]
                localpath = row["ZMEDIALOCALPATH"]

                if thumb and Path(thumb).stem in media_list:
                    media_name = Path(thumb).name
                    media_base_name = Path(thumb).stem
                    media_base_path = media_list[media_base_name].pop().parent

                    try:
                        thumb_path = media_base_path / f"{media_name}"
                        url_src_path = self.copyfile(thumb_path, media_name)
                        thumb = f'<img src="{url_src_path}"></img>'
                    except FileNotFoundError:
                        thumb = ""
                else:
                    thumb = ""

                if localpath and Path(localpath).stem in media_list:
                    media_name = Path(localpath).name
                    media_base_name = Path(localpath).stem
                    media_base_path = media_list[media_base_name].pop().parent

                    try:
                        attachment_path = media_base_path / f"{media_name}"
                        url_src_path = self.copyfile(attachment_path, media_name)
                        attachment_img = f'<img src="{url_src_path}" width="300"></img>'
                    except FileNotFoundError:
                        attachment_img = ""
                else:
                    attachment_img = ""

                self.data.append(
                    (
                        row["TIMESTAMP"],
                        sender,
                        row["ZFROMJID"],
                        receiver,
                        row["ZTOJID"],
                        row["ZTEXT"],
                        attachment_img,
                        thumb,
                        localpath,
                        row["ZSTARRED"],
                        lat,
                        lon,
                    ),
                )
