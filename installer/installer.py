import os
import json
import requests
import tempfile
import hashlib
from functools import cache
from dataclasses import dataclass
import uuid
import datetime 

# import semver
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


def get_system_state():
    with open(os.path.join(SCRIPT_DIR, 'system-state.json')) as f:
        return json.load(f)


def add_system_state(session_id, action, payload):
    system_state = get_system_state()
    if session_id not in system_state:
        system_state[session_id] = []
    system_state[session_id].append({"action": action, "payload": payload, "timestamp": datetime.datetime.now().isoformat()})
    with open(os.path.join(SCRIPT_DIR, 'system-state.json'), 'w') as f:
        json.dump(system_state, f, indent=2)


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
        # print(dep_name)
        local_deps = [dep for dep in dependencies if dep.name==dep_name]
        # print(f"{local_deps=}")
        local_requirements = [dep.version_requirement for dep in local_deps]
        # print(local_requirements)
        install_versions = versions_to_install(dep_name, available_versions[dep_name], local_requirements)
        # print(f"{dep_name=} {install_versions=}")
        requirements_per_deps[dep_name] = install_versions
        # requirements_per_deps[dep_name] = [dep.version_requirement for dep in dependencies if dep==dep_name]
    # print(requirements_per_deps)
    return requirements_per_deps

def get_dependencies(package_name, version="latest", arch="x86-64", dependencies=None):
    # version = "latest"
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
    # if version not in available_versions:
    #     print(f'Version {version} not found in available versions for {package_name}')
    #     raise SystemExit(1)
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
    # solve_dependencies(dependencies)
    return dependencies


def plain_install(package_name, version="latest", arch="x86-64"):
    db = get_db()
    if package_name not in db:
        print(f'Package {package_name} not found in database')
        raise SystemExit(1)
    pkg_info = db[package_name]

    print(f'Plain-Installing {package_name} {version}')
    tgz_url = pkg_info['dist'][arch]["versions"][version]["url"]
    sha256 = pkg_info['dist'][arch]["versions"][version]["sha256sum"]
    tgz = requests.get(tgz_url)
    tgz.raise_for_status()
    with tempfile.TemporaryDirectory() as tmp_dir:
        with open(os.path.join(tmp_dir, 'package.tgz'), 'wb') as f:
            f.write(tgz.content)
        with open(os.path.join(tmp_dir, 'package.tgz'), 'rb') as f:
            if hashlib.sha256(f.read()).hexdigest() != sha256:
                print('Checksum mismatch')
                raise SystemExit(1)
        os.system(f'tar -xzf {os.path.join(tmp_dir, "package.tgz")} -C {DST_DIR} ')
        # List files in temp_dir
        return
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                # print(os.path.relpath(os.path.join(root, file), tmp_dir))
                relpath = str(os.path.dirname(os.path.relpath(os.path.join(root, file), tmp_dir)))
                # print(f"{relpath=}, {file=}")
                if relpath.startswith(f"{package_name}/v{version}"):
                    dst_relpath = relpath.removeprefix(f"{package_name}/v{version}/")
                    # print("Copying", file, "to", dst_relpath)
                    os.makedirs(os.path.join(DST_DIR, dst_relpath), exist_ok=True)
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(DST_DIR, dst_relpath, file)
                    # Copy file from src_file to dst_file
                    os.system(f'cp {src_file} {dst_file}')

def install_package(package_name, version="latest", arch="x86-64", check_dependencies=True):
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
    # TODO: Dependencies
    if check_dependencies:
        dependencies = get_dependencies(package_name, version, arch)
        solved_dependencies = solve_dependencies(dependencies, arch)
        # print(f"{len(dependencies)=} {dependencies=}")
        # print(f"{len(solved_dependencies)=} {solved_dependencies=}")
        for dep_name, dep_versions in solved_dependencies.items():
            for dep_version in dep_versions:
                install_package(dep_name, dep_version, arch, check_dependencies=False)

    print(f'Installing {package_name} {version}')
    # raise SystemExit(1)
    plain_install(package_name, version, arch)
    
    
        

def main_test_deps(package_name=None):
    from pprint import pprint
    if not package_name:
        package_name = 'python.org'
        package_name = 'git-scm.org'
        package_name = 'php.net'
        # install_package(package_name)

        if len(os.sys.argv) > 1:
            package_name = os.sys.argv[1]

    deps = (get_dependencies(package_name))
    solve_dependencies(deps)
    print(f"{len(deps)=} dependencies")
    unique_deps = list(set([dep.name for dep in deps]))
    print(f"{len(unique_deps)=} unique dependencies")

def main(package_name=None):
    from pprint import pprint
    if not package_name:
        package_name = 'python.org'
        package_name = 'git-scm.org'
        package_name = 'php.net'

        if len(os.sys.argv) > 1:
            package_name = os.sys.argv[1]
        
    SESSION_ID = uuid.uuid4()
    version = "latest"
    add_system_state(SESSION_ID, "install-requested", {"package_name": package_name, "version": version})
    install_package(package_name)
    # Remove DST_DIR recursively
    # os.rmdir(DST_DIR)


if __name__ == '__main__':
    main()
