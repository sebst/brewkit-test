import os
import glob
import json
from collections import OrderedDict

import requests
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PANTRY_PKGX = os.environ.get('PANTRY_PKGX', os.path.join(SCRIPT_DIR, '../pantry/pkgx.dev/'))
DIST_PKGX_API_BASE_URL = os.environ.get('PANTRY_DIST_API_BASE_URL', 'https://dist.pkgx.dev/')
MAX_PACKAGES = os.environ.get('MAX_PACKAGES', None)
ARCHS = ['x86-64', 'aarch64']


def get_package_names_from_pantry(pantry=PANTRY_PKGX):
    pkg_names = []
    pkg_info_files = glob.glob(f"{pantry}/projects/**/**/package.yml", recursive=True)
    for pkg_info_file in pkg_info_files:
        pkg_info_file = pkg_info_file.removeprefix(pantry + '/projects/')
        pkg_info_file = pkg_info_file.removesuffix('/package.yml')
        pkg_name = pkg_info_file 
        pkg_names.append(pkg_name)
    return pkg_names

def get_package_info_pantry(pkg_name, pantry=PANTRY_PKGX):
    pkg_info = {}
    pkg_info_path = os.path.join(PANTRY_PKGX, "projects", pkg_name, 'package.yml')
    # print(f"{pkg_info_path=}")
    if os.path.exists(pkg_info_path):
        with open(pkg_info_path, 'r') as f:
            pkg_info = load(f, Loader=Loader)
    return pkg_info


def remove_darwin_only():
    pkg_names = get_package_names_from_pantry()
    for pkg_name in pkg_names:
        pkg_info = get_package_info_pantry(pkg_name)
        if pkg_info.get('platforms'):
            if 'darwin' in pkg_info.get('platforms', []):
                if ('linux/x86-64' not in pkg_info.get('platforms', []) and 'linux/aarch64' not in pkg_info.get('platforms', [])) and ('linux' in pkg_info.get('platforms', [])):
                    print(f"Removing {pkg_name} from pantry")
                    os.system(f"rm -rf {os.path.join(PANTRY_PKGX, 'projects', pkg_name)}")


def main():
    remove_darwin_only()


if __name__ == '__main__':
    main()
