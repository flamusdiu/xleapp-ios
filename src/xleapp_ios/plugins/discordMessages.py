import json

import magic

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get


class DiscordMessages(Artifact):
    def __post_init__(self):
        self.name = "Discord Messages"
        self.category = "Discord"
        self.report_headers = (
            "Timestamp",
            "Edited Timestamp",
            "Username",
            "Bot?",
            "Content",
            "Attachments",
            "User ID",
            "Channel ID",
            "Embedded Author",
            "Author URL",
            "Author Icon URL",
            "Embedded URL",
            "Embedded Script",
            "Footer Text",
            "Footer Icon URL",
            "Source File",
        )
        self.web_icon = WebIcon.MESSAGE_SQUARE

    @Search("*/com.hammerandchisel.discord/fsCachedData/*", return_on_first_hit=False)
    def process(self) -> None:
        for fp in self.found:
            mime = magic.from_file(str(fp()), mime=True)

            if mime != "text/plain":
                continue  # Checks if not text

            with open(fp()) as file_in:
                for json_data in file_in:
                    try:
                        json_parse = json.loads(json_data)

                        if not isinstance(json_parse, list):
                            continue

                        for message in json_parse:
                            username = deep_get(message, "author", "username")
                            userid = deep_get(message, "author", "id")
                            botuser = deep_get(message, "author", "bot")
                            timestamp = deep_get(message, "timestamp")
                            edited_timestamp = deep_get(message, "edited_timestamp")
                            content = deep_get(message, "content")
                            channel_id = deep_get(message, "channel")
                            attachments = {
                                attachment.get("url", "")
                                for attachment in deep_get(message, "attachments")
                            }
                            embeds = deep_get(message, "embeds")

                            embed_metadata = []
                            if embeds:
                                for embed in embeds:
                                    embed_metadata.append(deep_get(embed, "url"))
                                    embed_metadata.append(deep_get(embed, "description"))
                                    embed_metadata.append(
                                        deep_get(embed, "author", "name"),
                                    )
                                    embed_metadata.append(
                                        deep_get(embed, "author", "url"),
                                    )
                                    embed_metadata.append(
                                        deep_get(embed, "author", "icon_url"),
                                    )
                                    embed_metadata.append(
                                        deep_get(embed, "footer", "text"),
                                    )
                                    embed_metadata.append(
                                        deep_get(
                                            embed,
                                            "footer",
                                            "icon_url",
                                        ),
                                    )
                            else:
                                embed_metadata = ['', '', '', '', '', '', '']

                            file_path = fp.path.resolve()

                            self.data.append(
                                (
                                    timestamp,
                                    edited_timestamp,
                                    username,
                                    botuser,
                                    content,
                                    "\n".join(attachments),
                                    userid,
                                    channel_id,
                                    *embed_metadata,
                                    file_path,
                                ),
                            )

                    except TypeError:
                        pass  # File is not JSON
