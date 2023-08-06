import json
import logging
import os.path
from io import BytesIO, StringIO
from zipfile import ZipFile
from urllib.request import urlopen
from pathlib import Path

import requests

home = Path.home()
default_storage = home.joinpath("ddragon")
ddragon_url = "https://ddragon.leagueoflegends.com/cdn/"


class Pipeline:
    def __init__(self, local_storage, download_if_missing, download_dragontail_if_missing):
        self.local_storage = local_storage
        self.download_if_missing = download_if_missing
        self.download_dragontail_if_missing = download_dragontail_if_missing

    def get_from_local(self, path, version=None, language='en_US'):
        path = path.format(version, language)
        local_path = os.path.join(self.local_storage, path)
        print(local_path)
        print(os.path.exists(local_path))
        if os.path.exists(local_path):
            return json.load(open(local_path,"r", encoding='utf-8'))
        else:
            if self.download_dragontail_if_missing:
                zip = self.download_dragontail(version)
                print(zip)
            elif self.download_if_missing:
                os.makedirs(local_path)

    def download_dragontail(self, version):
        dragontail_url = f"https://ddragon.leagueoflegends.com/cdn/dragontail-{version}.tgz"
        logging.info(f"Downloading dragontail : {dragontail_url}")
        resp = requests.get(dragontail_url, stream=True, verify=False)
        if resp.ok:
            print(resp.content)
            dragontail = ZipFile(BytesIO(resp.content))
            return dragontail
        else:
            logging.info("Bad zip file")


default_pipeline = Pipeline(default_storage, True, True)
