import os
import glob
import json

import requests
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PANTRY_PKGX = os.environ.get('PANTRY_PKGX', os.path.join(SCRIPT_DIR, '../pantry/pkgx.dev/'))

def get_package_info_pantry(pkg_name, pantry=PANTRY_PKGX):
    pkg_info = {}
    pkg_info_path = os.path.join(PANTRY_PKGX, "projects", pkg_name, 'package.yml')
    print(f"{pkg_info_path=}")
    if os.path.exists(pkg_info_path):
        with open(pkg_info_path, 'r') as f:
            pkg_info = load(f, Loader=Loader)
    return pkg_info

def get_package_info_dist(pkg_name, arch='x86-64'):
    pkg_info = {}
    versions = []
    url = f"https://dist.pkgx.dev/{pkg_name}/linux/{arch}/versions.txt"
    print(f"{url=}")
    response = requests.get(url)
    if response.status_code == 200:
        versions = response.text.splitlines()
    pkg_info['versions'] = versions
    return pkg_info

def get_package_names_from_pantry(pantry=PANTRY_PKGX):
    pkg_names = []
    pkg_info_files = glob.glob(f"{pantry}/projects/**/**/package.yml", recursive=True)
    for pkg_info_file in pkg_info_files:
        pkg_info_file = pkg_info_file.removeprefix(pantry + '/projects/')
        pkg_info_file = pkg_info_file.removesuffix('/package.yml')
        pkg_name = pkg_info_file 
        pkg_names.append(pkg_name)
    return pkg_names

def get_dist_versions_for_packages(package_names=None):
    if not package_names:
        package_names = get_package_names_from_pantry()
    pkg_info = {}
    for pkg_name in package_names:
        pkg_info[pkg_name] = get_package_info_dist(pkg_name)
    return pkg_info



def main():
    from pprint import pprint
    pkg_name = 'apache.org/httpd'
    pkg_info = get_dist_versions_for_packages()
    # pprint(pkg_info)
    with open('dist-versions.json', 'w') as f:
        json.dump(pkg_info, f, indent=4)

if __name__ == '__main__':
    main()
