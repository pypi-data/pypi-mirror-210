import os
import os.path as path
from urllib.request import urlretrieve, urlopen, URLError
import shutil

import appdirs


def get_default_love_app_zip_dir(version):
    return path.join(appdirs.user_cache_dir("makelove"), "love-app", version + ".zip")


def download_love_app_zip(version):
    download_url = "https://github.com/love2d/love/releases/download/{version}/love-{version}-macos.zip".format(
        version=version
    )

    target_path = get_default_love_app_zip_dir(version)
    print("Downloading love app to: '{}'".format(target_path))

    os.makedirs(path.dirname(target_path), exist_ok=True)
    print("Downloading '{}'..".format(download_url))
    urlretrieve(download_url, target_path)


def build_mac(config, version, target, target_directory, love_file_path):
    if target in config and "love_app_zip" in config[target]:
        love_app_zip = config[target]["love_app_zip"]
    else:
        assert "love_version" in config
        print("No love app specified for target {}".format(target))
        love_app_zip = get_default_love_app_zip_dir(config["love_version"])
        if path.isdir(love_app_zip):
            print("Love app already present in '{}'".format(love_app_zip))
        else:
            download_love_app_zip(config["love_version"])

    app_zip = path.join(target_directory, config["name"] + ".zip")
    shutil.copy(love_app_zip, app_zip)

    # I have to edit the zip in place instead of extracting, modifying and compressing again
    # because the .app directory contains symlinks to use them at all you either have to
    # enable Developer Mode or run as Administrator (as far as I understand).

    with ZipFile(app_zip, "w") as zipfile:
        pass
