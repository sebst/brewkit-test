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


def get_package_info_pantry(pkg_name, pantry=PANTRY_PKGX):
    pkg_info = {}
    pkg_info_path = os.path.join(PANTRY_PKGX, "projects", pkg_name, 'package.yml')
    # print(f"{pkg_info_path=}")
    if os.path.exists(pkg_info_path):
        with open(pkg_info_path, 'r') as f:
            pkg_info = load(f, Loader=Loader)
    return pkg_info

def package_supports_arch(pkg_name, arch):
    arch = arch.lower()
    pkg_info = get_package_info_pantry(pkg_name)
    if pkg_info.get('platforms'):
        platforms = pkg_info.get('platforms', [])
        if platforms == 'linux':
            return True
        if platforms == ['linux']:
            return True
        if platforms == f'linux/{arch}':
            return True
        if platforms == [f'linux/{arch}']:
            return True
        for platform in platforms:
            try:
                arch_name = platform.split('/')[1]
                if arch_name == arch:
                    return True
            except:
                pass
        return False
    else:
        return True

def get_package_info_dist(pkg_name, dist_api=DIST_PKGX_API_BASE_URL):
    pkg_info = {}
    for arch in ARCHS:
        if not package_supports_arch(pkg_name, arch):
            continue
        pkg_info[arch] = {}
        versions = []
        url = f"{dist_api}/{pkg_name}/linux/{arch}/versions.txt"
        response = requests.get(url)
        if response.status_code == 200:
            versions = response.text.splitlines()
        else: print(f"Error: finding versions for {pkg_name} on {arch} @ {url}")
        versions = [(v, f"{dist_api}/{pkg_name}/linux/{arch}/v{v}.tar.gz", f"{dist_api}/{pkg_name}/linux/{arch}/v{v}.tar.gz.asc", f"{dist_api}/{pkg_name}/linux/{arch}/v{v}.tar.gz.sha256sum") for v in versions]
        versions_dict = OrderedDict()
        for v in versions:
            versions_dict[v[0]] = {'url': v[1], 'asc_url': v[2], 'sha256sum_url': v[3]}
            response = requests.get(v[3])
            if response.status_code == 200:
                versions_dict[v[0]]['sha256sum'] = response.text.split()[0]
            else: print(f"Error: finding sha256sum for {pkg_name} on {arch} @ {v[3]}")
            response = requests.head(v[1])
            if response.status_code == 200:
                versions_dict[v[0]]['size'] = int(response.headers['Content-Length'])
            else: print(f"Error: finding size for {pkg_name} on {arch} @ {v[1]}")
        pkg_info[arch]['versions'] = versions_dict
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

def get_database(pantry=PANTRY_PKGX, dist_api=DIST_PKGX_API_BASE_URL):
    pkg_info = {}
    pkg_names = get_package_names_from_pantry(pantry)
    for i, pkg_name in enumerate(pkg_names):
        pkg_info[pkg_name] = {}
        pkg_info[pkg_name]['pantry'] = get_package_info_pantry(pkg_name, pantry)
        pkg_info[pkg_name]['dist'] = get_package_info_dist(pkg_name, dist_api)
        if MAX_PACKAGES and i > int(MAX_PACKAGES):
            break
    return pkg_info



def main():
    from pprint import pprint
    pkg_name = 'apache.org/httpd'
    pkg_info = get_database()
    # pprint(pkg_info)
    with open('db.json', 'w') as f:
        json.dump(pkg_info, f, indent=4)
    with open('db-minified.json', 'w') as f:
        json.dump(pkg_info, f)

if __name__ == '__main__':
    main()
