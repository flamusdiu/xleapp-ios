import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import unix_epoch_to_readable_date


class VoiceRecording(Artifact):
    def __post_init__(self) -> None:
        self.name = "Voice Recordings"
        self.category = "Voice-Recordings"
        self.report_headers = ("Creation Date", "Title", "Path to File", "Audio File")
        self.report_title = "Voice Recordings"
        self.web_icon = WebIcon.MIC

    @Search(
        "**/Recordings/*.composition/manifest.plist",
        "**/Recordings/*.m4a",
        file_names_only=True,
    )
    def process(self):
        plist_files = []
        m4a_files = []

        for fp in self.found:
            if fp.path.suffix == ".plist":
                plist_files.append(fp())
            elif fp.path.suffix == ".m4a":
                m4a_filename = fp()
                m4a_filename = m4a_filename.replace(" ", "_")
                m4a_files.append(m4a_files)
                self.copyfile(fp.path, m4a_filename)

        plist_files.sort()
        m4a_files.sort()

        for plist_file, m4a_file in zip(plist_files, m4a_files):
            with open(plist_file, "rb") as file:
                pl = plistlib.load(file)
                ct = unix_epoch_to_readable_date(pl["RCSavedRecordingCreationTime"])

                audio = (
                    "<audio controls>"
                    f'<source src="{m4a_file}" type="audio/wav">'
                    "<p>Your browser does not support HTML5"
                    "audio elements.</p></audio>"
                )

                self.data.append(
                    (
                        ct,
                        pl["RCSavedRecordingTitle"],
                        pl["RCComposedAVURL"].split("//")[1],
                        audio,
                    ),
                )
