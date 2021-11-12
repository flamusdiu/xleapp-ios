import datetime
import plistlib

from xleapp import Artifact, Search, WebIcon


class GoogleMapsCacheRoutes(Artifact):
    def __post_init__(self) -> None:
        self.name = "Google Maps Cache Routes"
        self.category = "Locations"
        self.description = "Google Maps Cache Routes"
        self.web_icon = WebIcon.MAP_PIN
        self.report_headers = ("Timestamp", "Latitude", "Longitude", "Source File")
        self.timeline = True

    @Search(
        "**/Library/Application Support/CachedRoutes/*.plist",
        return_on_first_hit=False,
    )
    def process(self) -> None:
        for fp in self.found:
            timestamp_from_file_name = int(fp.path.stem)
            datatime_time = datetime.datetime.fromtimestamp(
                timestamp_from_file_name / 1000,
            )

            pl = plistlib.load(fp())
            for obj in pl["$objects"]:
                lat = obj["_coordinateLat"]
                lon = obj["_coordinateLong"]
                self.data.append((datatime_time, lat, lon, str(fp.path)))
