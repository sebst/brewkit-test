import asyncio
import os
import json
# import requests
import tempfile
import hashlib
from functools import cache
from dataclasses import dataclass

import aiohttp

from packaging.version import Version
from packaging.specifiers import SpecifierSet


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DST_DIR = os.path.join(SCRIPT_DIR, 'packages')
if not os.path.exists(DST_DIR):
    os.makedirs(DST_DIR)


@dataclass
class Dependency:
    name: str
    version_requirement: str
    from_package: str | None
    from_package_version: str | None


@cache
def get_db():
    with open(os.path.join(SCRIPT_DIR, '..', 'tools', '_optim_db-minified.json')) as f:
        return json.load(f)


def can_dependency_be_ignored(package_name, dep_name):
    return False
    if package_name == "python.org" and dep_name == "tcl-lang.org":
        return True
    return False


def can_be_satisfied_by_all(version, requirements):
    version = Version(version)
    for requirement in requirements:
        requirement = str(requirement)
        if requirement == '>=2.9.0<2.12':
            requirement = '>=2.9.0,<2.12'
        if requirement.startswith("~"):
            requirement = requirement.removeprefix("~")
            requirement = f">={requirement},<{version.major}.{version.minor+1}"
        if requirement.startswith("^"):
            requirement = requirement.removeprefix("^")
            requirement = f">={requirement},<{version.major+1}"
        if requirement.isnumeric():
            requirement = f">={requirement}"
        if requirement == "*":
            continue
        requirement = SpecifierSet(requirement)
        if version not in requirement:
            return False
    return True


def versions_to_install(package_name, available_versions, requirements):
    result = []
    sem_versions = {}
    for v in available_versions:
        try:
            sem_versions[v] = Version(v)
        except:
            print(f"Error parsing {v=} for {package_name=}")
            pass
    sem_versions = list(sem_versions.keys())
    sem_versions = sorted(sem_versions, key=lambda v: Version(v), reverse=True)
    satisfied_by_all = False
    for sem_version in sem_versions:
        if can_be_satisfied_by_all(sem_version, requirements):
            satisfied_by_all = True
            break
    if not satisfied_by_all:
        print(f"Not satisfied by all {package_name=}, {requirements=}")
        raise SystemExit(1)
    else:
        return [sem_version]
    return [available_versions[0]]


def solve_dependencies(dependencies, arch="x86-64"):
    db = get_db()
    unique_deps = list(set([dep.name for dep in dependencies]))
    available_versions = {}
    for dep_name in unique_deps:
        if dep_name not in db:
            print(f'Package {dep_name} not found in database')
            raise SystemExit(1)
        pkg_info = db[dep_name]
        available_versions[dep_name] = list(pkg_info['dist'][arch]["versions"].keys())
    requirements_per_deps = {}
    for dep_name in unique_deps:
        local_deps = [dep for dep in dependencies if dep.name==dep_name]
        local_requirements = [dep.version_requirement for dep in local_deps]
        install_versions = versions_to_install(dep_name, available_versions[dep_name], local_requirements)
        requirements_per_deps[dep_name] = install_versions
    return requirements_per_deps

def get_dependencies(package_name, version="latest", arch="x86-64", dependencies=None):
    if dependencies is None:
        dependencies = []
    db = get_db()
    if package_name not in db:
        print(f'Package {package_name} not found in database')
        raise SystemExit(1)
    pkg_info = db[package_name]
    if arch not in pkg_info['dist'].keys():
        print(f"{arch} not supported for {package_name}")
        raise SystemExit(1)
    available_versions = list(pkg_info['dist'][arch]["versions"].keys())
    if version == "latest":
        version = available_versions[-1]
    mentioned_dependencies = pkg_info['pantry'].get('dependencies', {})
    subst_keys = ["linux", f"linux/{arch}"]
    for subst_key in subst_keys:
        if subst_key in mentioned_dependencies:
            if isinstance(mentioned_dependencies[subst_key], dict):
                mentioned_dependencies.update(mentioned_dependencies[subst_key])
    for dep_name, dep_version in mentioned_dependencies.items():
        if dep_name == 'darwin': 
            continue
        if dep_name == 'linux':
            continue
        if dep_name == 'linux/x86-64':
            continue
        if dep_name == 'linux/aarch64':
            continue
        if can_dependency_be_ignored(package_name, dep_name):
            continue
        dependencies.append(Dependency(dep_name, dep_version, package_name, version))
        get_dependencies(dep_name, dep_version, arch, dependencies)
    return dependencies


async def plain_install(package_name, version="latest", arch="x86-64"):
    db = get_db()
    if package_name not in db:
        print(f'Package {package_name} not found in database')
        raise SystemExit(1)
    pkg_info = db[package_name]

    print(f'Plain-Installing {package_name} {version}')
    tgz_url = pkg_info['dist'][arch]["versions"][version]["url"]
    sha256 = pkg_info['dist'][arch]["versions"][version]["sha256sum"]
    async with aiohttp.ClientSession() as session:
        async with session.get(tgz_url) as tgz:
            # tgz = requests.get(tgz_url)
            # tgz.raise_for_status()
            with tempfile.TemporaryDirectory() as tmp_dir:
                with open(os.path.join(tmp_dir, 'package.tgz'), 'wb') as f:
                    # f.write(tgz.content)
                    f.write(await tgz.read())
                with open(os.path.join(tmp_dir, 'package.tgz'), 'rb') as f:
                    if hashlib.sha256(f.read()).hexdigest() != sha256:
                        print('Checksum mismatch')
                        raise SystemExit(1)
                os.system(f'tar -xzf {os.path.join(tmp_dir, "package.tgz")} -C {DST_DIR} ')


async def install_package(package_name, version="latest", arch="x86-64", check_dependencies=True):
    db = get_db()
    if package_name not in db:
        print(f'Package {package_name} not found in database')
        raise SystemExit(1)
    pkg_info = db[package_name]
    available_versions = list(pkg_info['dist'][arch]["versions"].keys())
    if version == "latest":
        version = available_versions[-1]
    if version not in available_versions:
        print(f'Version {version} not found in available versions')
        raise SystemExit(1)
    if check_dependencies:
        dependencies = get_dependencies(package_name, version, arch)
        solved_dependencies = solve_dependencies(dependencies, arch)
        async with asyncio.TaskGroup() as tg:
            for dep_name, dep_versions in solved_dependencies.items():
                for dep_version in dep_versions:
                    # await install_package(dep_name, dep_version, arch, check_dependencies=False)
                    tg.create_task(install_package(dep_name, dep_version, arch, check_dependencies=False))

    print(f'Installing {package_name} {version}')
    await plain_install(package_name, version, arch)


async def main(package_name=None):
    from pprint import pprint
    if not package_name:
        package_name = 'python.org'
        package_name = 'git-scm.org'
        package_name = 'php.net'

        if len(os.sys.argv) > 1:
            package_name = os.sys.argv[1]
        
    await install_package(package_name)
    # Remove DST_DIR recursively
    # os.rmdir(DST_DIR)


if __name__ == '__main__':
    asyncio.run(main())
