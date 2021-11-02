from pathlib import Path

from xleapp.artifacts import ArtifactError, Artifacts
from xleapp.plugins import Plugin


class IosPlugin(Plugin):
    @property
    def folder(self) -> Path:
        """Returns path of the plugin folder"""
        return Path(__file__).parent

    def pre_process(self, artifacts: Artifacts) -> None:
        for artifact in artifacts.data:
            # Now ready to run
            # Special processing for iTunesBackup Info.plist as it is a
            # separate entity, not part of the Manifest.db. Seeker won't find it
            if (
                artifacts.app.device["type"] == "ios"
                and artifacts.app.extraction_type == "itunes"
            ):
                if artifact.name == "ITUNES_BACKUP_INFO":
                    info_plist_path = Path(artifacts.app.input_path) / "Info.plist"
                    if not info_plist_path.exists():
                        ArtifactError("Info.plist not found for iTunes Backup!")
                    else:
                        artifacts['LAST_BUILD'].select = False
            else:
                artifacts['ITUNES_BACKUP_INFO'].select = False
