from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FacebookMessengerCalls(Artifact):
    def __post_init__(self) -> None:
        self.name = "Calls"
        self.category = "Facebook Messenger"
        self.report_headers = (
            "Timestamp",
            "Sender Name",
            "Sender ID",
            "Call Type",
            "Call Duration/Subtitle",
        )
        self.web_icon = WebIcon.FACEBOOK

    @Search("**/lightspeed-*.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                datetime(thread_messages.timestamp_ms/1000,'unixepoch') as Timestamp,
                contacts.name as 'Sender Name',
                thread_messages.thread_key,
                attachments.title_text as "Call Type",
                attachments.subtitle_text as "Duration/Subtitle"
                from thread_messages
                left join contacts
                    on thread_messages.sender_id = contacts.id
                left join attachments
                    on thread_messages.message_id = attachments.message_id
                where attachments.title_text like 'Audio Call' or attachments.title_text like 'Video Chat'
                order by Timestamp
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
