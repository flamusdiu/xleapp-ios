import datetime

from pathlib import Path

from PIL import Image
from xleapp import Artifact, Search, WebIcon

from xleapp_ios.helpers.parsers import ktxparser


class ApplicationSnapshots(Artifact):
    def __post_init__(self) -> None:
        self.name = "App Snapshots (screenshots)"
        self.category = "Installed Apps"
        self.web_icon = WebIcon.PACKAGE
        self.description = (
            "Snapshots saved by iOS for individual apps appear here. Blank "
            "screenshots are excluded here. Dates and times shown are from "
            "file modified timestamps"
        )
        self.report_headers = ('App Name', 'Source Path', 'Date Modified', 'Snapshot')

    @Search(
        "**/Library/Caches/Snapshots/*",
        "**/SplashBoard/Snapshots/*",
        file_names_only=True,
        return_on_first_hit=False,
    )
    def process(self) -> None:
        def save_ktx_to_png_if_valid(ktx_path: Path, save_to_path: Path) -> bool:
            """Excludes all white or all black blank images"""
            with open(ktx_path, 'rb') as f:
                ktx = ktxparser.KTX_reader()
                try:
                    if ktx.validate_header(f):
                        data = ktx.get_uncompressed_texture_data(f)
                        dec_img = Image.frombytes(
                            'RGBA',
                            (ktx.pixelWidth, ktx.pixelHeight),
                            data,
                            'astc',
                            (4, 4, False),
                        )
                        # either all black or all white https://stackoverflow.com/questions/14041562/python-pil-detect-if-an-image-is-completely-black-or-white
                        # if sum(dec_img.convert("L").getextrema()) in (0, 2):
                        #     logfunc('Skipping image as it is blank')
                        #     return False

                        dec_img.save(save_to_path, "PNG")
                        return True
                except (OSError, ValueError, ktxparser.liblzfse.error) as ex:
                    self.log(message=f'Had an exception - {str(ex)}')
            return False

        data_list = []
        # Format=  [ [ 'App Name', 'ktx_path', mod_date, 'png_path' ], .. ]

        for fp in self.found:
            if fp.path.is_dir():
                continue

            if fp.path.stat().st_size < 2500:
                continue

            if "downscaled" not in fp.path.parts:
                app_name = fp.path.parts[-2].split(" ")[0]
            else:
                app_name = fp.path.parts[-3].split(" ")[0]

            if app_name.startswith('sceneID'):
                app_name = app_name[8:]

            dash_pos = app_name.find("-")

            if dash_pos > 0:
                app_name = app_name[0:dash_pos]

            if fp.path.suffix == '.ktx':
                if fp.path.stat().st_size < 2500:  # too small, they are blank
                    continue
                png_path = Path(
                    self.data_save_folder / f"{app_name}_{fp.path.parts[-1][:4]}.png",
                )
                if save_ktx_to_png_if_valid(fp.path, png_path):
                    last_modified_date = datetime.datetime.fromtimestamp(
                        fp.path.stat().st_mtime,
                    )
                    data_list.append([app_name, fp.path, last_modified_date, png_path])
            elif fp.path.suffix == '.jpeg':
                jpg_path = Path(self.data_save_folder / f"{app_name}_{fp.path.parts[-1]}")
                if self.copyfile(fp.path, jpg_path):
                    last_modified_date = datetime.datetime.fromtimestamp(
                        fp.path.stat().st_mtime,
                    )
                    data_list.append([app_name, fp.path, last_modified_date, jpg_path])

        if data_list:
            for app_name, ktx_path, mod_date, img_path in data_list:
                img_html = (
                    f'<a href="{str(img_path)}"><img src="{str(img_path)}" '
                    'class="img-fluid" style="max-height:300px; max-width:400px"></a>'
                )
                self.data.append(
                    (f"{str(app_name)}", f"{str(ktx_path)}", mod_date, img_html),
                )
