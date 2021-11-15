import base64
import re

import defusedxml.ElementTree as ET

from xleapp import Artifact, Search, WebIcon


class DeviceActivator(Artifact):
    def __post_init__(self) -> None:
        self.name = "iOS Device Activator Data"
        self.category = "IOS Build"
        self.web_icon = WebIcon.GIT_COMMIT

    @Search("*private/var/mobile/Library/Logs/mobileactivationd/ucrt_oob_request.txt")
    def process(self) -> None:
        all_lines = ""
        data_list = []

        for fp in self.found:
            for line in fp():
                line = str(line, encoding="utf-8").strip()
                all_lines += line

            found = re.findall(
                (
                    "<key>ActivationInfoXML</key><data>(.*)</data><key>RKCertification"
                    "</key><data>"
                ),
                all_lines,
            )
            base64_message = found[0]

            data = base64.b64decode(base64_message)
            self.copyfile(data, "results.xml")

            xmlfile = self.data_save_folder / "results.xml"
            tree = ET.parse(xmlfile)
            root = tree.getroot()

            for elem in root:
                for elemx in elem:
                    for elemz in elemx:
                        data_list.append(str(elemz.text).strip())

            it = iter(data_list)
            self.data = list(zip(it, it))

            for key, value in self.data:
                if key in (
                    "EthernetMacAddress",
                    "BluetoothAddress",
                    "WifiAddress",
                    "ModelNumber",
                ):
                    self.app.device.update({key: value})
