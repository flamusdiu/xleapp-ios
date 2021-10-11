from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from xleapp import Artifact, Search, WebIcon, open_sqlite_db_readonly, timed


@dataclass
class WhatsappMessages(Artifact):
    def __post_init__(self):
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
        self.kml = True
        self.timeline = True

    @timed
    @Search(
        "*/var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite*",
        "*/var/mobile/Containers/Shared/AppGroup/*/Message/Media/*/*/*/*.*",
        file_names_only=True,
        return_on_first_hit=False,
    )
    def process(self):
        data_list = []
        media_list = defaultdict(set)
        files_found = self.found.copy()
        for file_found in files_found:
            if not file_found().suffix.startswith(".sqlite"):
                media_list[file_found().stem].add(file_found())
                self.found.remove(file_found)

            if file_found().name.endswith(".sqlite"):
                fp = str(file_found())

        db = open_sqlite_db_readonly(fp)
        cursor = db.cursor()

        cursor.execute(
            """
            select
            datetime(ZMESSAGEDATE+978307200, 'UNIXEPOCH'),
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
            """
        )
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            for row in all_rows:

                if row[1] == 1:
                    sender = "Local User"
                    receiver = row[2]
                else:
                    sender = row[2]
                    receiver = "Local User"

                if row[8] == 5:
                    lon = row[9]
                    lat = row[10]
                else:
                    lat = ""
                    lon = ""

                thumb = row[12]
                attachment = row[11]
                localpath = row[11]

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

                if attachment and Path(attachment).stem in media_list:
                    media_name = Path(attachment).name
                    media_base_name = Path(attachment).stem
                    media_base_path = media_list[media_base_name].pop().parent

                    try:
                        attachment_path = media_base_path / f"{media_name}"
                        url_src_path = self.copyfile(attachment_path, media_name)
                        attachment = f'<img src="{url_src_path}" width="300"></img>'
                    except FileNotFoundError:
                        attachment = ""
                else:
                    attachment = ""

                data_list.append(
                    (
                        row[0],
                        sender,
                        row[3],
                        receiver,
                        row[4],
                        row[6],
                        attachment,
                        thumb,
                        localpath,
                        row[7],
                        lat,
                        lon,
                    )
                )

        self.data = data_list
