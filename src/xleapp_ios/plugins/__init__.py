import fnmatch
import logging
import shutil
import sqlite3
import tarfile
import typing as t
from functools import cached_property
from pathlib import Path
from zipfile import ZipFile

from xleapp.artifacts import ArtifactError, Artifacts
from xleapp.helpers.db import open_sqlite_db_readonly
from xleapp.helpers.search import FileSeekerBase
from xleapp.helpers.utils import is_platform_windows
from xleapp.plugins import Plugin

logger = logging.getLogger("xleapp.logfile")


class IosPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()

        self.register_seekers("ITUNES", FileSeekerItunes())

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
                and artifacts.app.extraction_type == "ITUNES"
            ):
                if artifact.name == "ITUNES_BACKUP_INFO":
                    info_plist_path = Path(artifacts.app.input_path) / "Info.plist"
                    if not info_plist_path.exists():
                        ArtifactError("Info.plist not found for iTunes Backup!")
                    else:
                        artifacts['LAST_BUILD'].select = False
            else:
                artifacts['ITUNES_BACKUP_INFO'].select = False


class FileSeekerItunes(FileSeekerBase):
    """Searches iTunes Backup for files."""

    manifest_db: Path
    directory: Path

    def __call__(
        self,
        directory_or_file,
        temp_folder,
    ) -> t.Type[FileSeekerBase]:
        self.input_path = Path(directory_or_file)
        self.temp_folder = Path(temp_folder)
        if self.validate:
            self.all_files = self.build_files_list()

        return self

    def build_files_list(self, folder=None) -> list:
        """Populates paths from Manifest.db files into _all_files"""

        all_files: dict[str, str] = {}
        db = open_sqlite_db_readonly(self.manifest_db)
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT
            fileID,
            relativePath
            FROM
            Files
            WHERE
            flags=1
            """,
        )
        db.row_factory = sqlite3.Row
        all_rows = cursor.fetchall()
        for row in all_rows:
            relative_path: str = row['relativePath']
            hash_filename: str = row['fileID']
            all_files[relative_path] = hash_filename
        db.close()

        return all_files

    def search(self, filepattern: str):
        pathlist = []

        if filepattern.find("*") == -1:
            if is_platform_windows():
                original_location = Path(f"\\\\?\\{self.directory / filepattern}")
            else:
                original_location = self.directory / filepattern
            pathlist.append(original_location)
        else:
            matching_keys = fnmatch.filter(self._all_files, filepattern)
            for relative_path in matching_keys:
                hash_filename = self._all_files[relative_path]

                if is_platform_windows():
                    original_location = Path(
                        f"\\\\?\\{self.directory / hash_filename[:2] / hash_filename}"
                    )
                    temp_location = Path(f"\\\\?\\{self.temp_folder / relative_path}")
                else:
                    original_location = (
                        Path(self.directory) / hash_filename[:2] / hash_filename
                    )
                    temp_location = Path(self.temp_folder) / relative_path
                temp_location.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_location, temp_location)
                pathlist.append(temp_location)

        return iter(pathlist)

    def cleanup(self) -> None:
        # no cleanup for this seeker
        pass

    @cached_property
    def validate(self) -> bool:
        mime: str
        input_path: Path
        mime, input_path = self.input_path
        extract_dir = self.temp_folder / "backup"

        if mime == "dir":
            manifest_db = input_path / "Manifest.db"
            if manifest_db.exists():
                self.manifest_db = manifest_db
        elif mime in ["application/x-gzip", "application/x-tar"]:
            with tarfile.open(input_path, "r:*") as gz_or_tar_file:
                num_of_files = sum(1 for member in gz_or_tar_file if member.isreg())
                for member in gz_or_tar_file:
                    if fnmatch.fnmatch(member.name, "**/Manifest.db"):
                        logger.info(f"Manifest.db found in {input_path!r}...")
                        logger.info(
                            f"Extracing {num_of_files} files from backup to {self.temp_folder!r}"
                        )

                        gz_or_tar_file.extractall(path=extract_dir)
                        self.manifest_db = extract_dir / member.path
        elif mime == "application/zip":
            with ZipFile(input_path) as zip_file:
                num_of_files = len(zip_file.infolist())
                for member in zip_file.namelist():
                    if fnmatch.fnmatch(member, "**/Manifest.db"):
                        logger.info(f"Manifest.db found in {input_path!r}...")
                        logger.info(
                            f"Extracing {num_of_files} files from backup to {self.temp_folder!r}"
                        )
                        zip_file.extractall(path=extract_dir)
                        self.manifest_db = extract_dir / member

        if self.manifest_db:
            self.directory = self.manifest_db.parent
            return True
        return False

    @property
    def priorty(self) -> int:
        return 10
