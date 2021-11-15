from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FacebookMessengerConversationGroups(Artifact):
    def __post_init__(self) -> None:
        self.name = "Conversation Groups"
        self.category = "Facebook Messenger"
        self.report_headers = (
            "Timestamp (Last Activity)",
            "Thread Key",
            "Thread Participants",
        )
        self.web_icon = WebIcon.FACEBOOK

    @Search("**/lightspeed-*.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                datetime(threads.last_activity_timestamp_ms/1000,'unixepoch'),
                thread_participant_detail.thread_key,
                group_concat(thread_participant_detail.name, ';')
                from thread_participant_detail
                join threads
                    on threads.thread_key = thread_participant_detail.thread_key
                group by thread_participant_detail.thread_key
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
