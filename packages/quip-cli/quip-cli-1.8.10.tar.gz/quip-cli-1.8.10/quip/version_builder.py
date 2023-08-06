import os
import yaml
import re
import shutil
import glob


VERSION_FILES = [ 
    { 
        "file": "src/extension.yml",
        "format": "yml",
        "location": "extension.version"
    },
    { 
        "file": "script.yml",
        "format": "yml",
        "location": "script.version"
    },
    { 
        "file": "src/extension.py",
        "format": "regex",
        "location": r"^\s*(gl_version|version|__version__)\s*=\s*[\"']+([^\"']+)[\"']+",
        "group": 2
    },
    { 
        "file": "src/__init__.py",
        "format": "regex",
        "location": r"^\s*(gl_version|version|__version__)\s*=\s*[\"']+([^\"']+)[\"']+",
        "group": 2
    },
    { 
        "file": "src/templates/script*",
        "format": "regex",
        "location": r"^\s*(gl_version|version|__version__)\s*=\s*[\"']+([^\"']+)[\"']+",
        "group": 2
    }
]

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def safeset(dct, value, *keys):
    _dct = dct
    for key in keys[:-1]:
        try:
            dct = dct[key]
        except KeyError:
            return None
    dct[keys[-1]] = value
    return _dct

def find_current_version(version_files=None):
    versions = []
    if version_files is None:
        version_files = VERSION_FILES
    for file_desc in version_files:
        file_path = file_desc["file"]
        _format = file_desc.get("format")
        location = file_desc.get("location", "")
        group = file_desc.get("group", 1)
        if "*" in file_path or "?" in file_path:
            # there is wildcard
            files = glob.glob(file_path)
        else:
            files = [file_path]

        for _file in files:
            _versions = get_version_from_file(_file, _format, location, group)
            if len(_versions) > 0:
                versions = versions + _versions

    _versions = set(versions)
    if len(_versions) > 1:
        print(f"There are multiple versions: {_versions}")
    
    return list(_versions)


def get_version_from_file(file_path, format, location, group=1):
    versions = []
    if os.path.exists(file_path):
        if format in ["yaml", "yml"]:
            location = location.split(".")
            with open(file_path) as f:
                conf = yaml.safe_load(f)
                _version = safeget(conf, *location)
                print(f"{file_path} : {_version}")
                versions.append(_version)
        elif format in ["py", "python", "script", "regex", "regexp"]:
            with open(file_path) as f:
                content = f.read()
            regex = re.compile(location, re.MULTILINE)
            matches = regex.finditer(content)
            for match in matches:
                _version = match.group(group)
                print(f"{file_path} : {_version}")
                if _version not in versions:
                    versions.append(_version)
    
    return versions


def update_version_in_file(file_path, old_version, new_version, format, location, group):
    if os.path.exists(file_path):
        if format in ["yaml", "yml"]:
            with open(file_path) as f:
                conf = yaml.safe_load(f)

            location = location.split(".")
            _version = safeget(conf, *location)
            if _version == old_version:
                conf = safeset(conf, new_version, *location)
                with open(file_path, "w") as f:
                    yaml.dump(conf, f, sort_keys=False)
                    print(f"{file_path} : {old_version} -> {new_version}")
            else:
                print(f"{file_path} : {old_version} != {_version}")

        elif format in ["py", "python", "script", "regex", "regexp"]:
            with open(file_path) as f:
                content_lines = f.readlines()
            
            content = "\n".join(content_lines)
            regex = re.compile(location, re.MULTILINE)
            matches = regex.search(content)
            if matches is None:
                print(f"skipping {file_path}")
                return None

            new_file_path = file_path + ".tmp"
            with open(new_file_path, "w") as f:
                for line in content_lines:
                    match = regex.search(line)
                    if match is not None:
                        _version = match.group(group)
                        if _version == old_version:
                            line = line.replace(old_version, new_version)
                            print(f"{file_path} : {old_version} -> {new_version}")
            
                    f.write(line)

            # Backup
            backup_filename = os.path.join(os.path.dirname(file_path), "." + os.path.basename(file_path) + ".bckp")
            shutil.move(file_path, backup_filename)
            os.rename(new_file_path, file_path)


def get_new_version(method, version):
    num_split_re = re.compile(r'(\d+)([\-\+\.a-zA-Z]*)(\d*)')
    _version = version.split(".")
    release, major, minor, beta = [1,0,0,0]
    release_text = major_text = minor_text = ""
    if len(_version) > 0:
        matches = num_split_re.search(_version[0])
        if matches is not None:
            release = int(matches.group(1))
            release_text = matches.group(2)
    
    if len(_version) > 1:
        matches = num_split_re.search(_version[1])
        if matches is not None:
            major = int(matches.group(1))
            major_text = matches.group(2)

    if len(_version) > 2:
        matches = num_split_re.search(_version[2])
        if matches is not None:
            minor = int(matches.group(1))
            minor_text = matches.group(2)
            if len(matches.group(3)) > 0:
                beta = int(matches.group(3))

    if method == "release":
        release += 1
        major = 0
        minor = 0
    elif method == "major":
        major += 1
        minor = 0
    elif method == "minor":
        minor += 1
    elif method == "beta":
        if minor_text == "b":
            beta += 1
        else:
            minor_text = "b"
            beta = 1
    elif method == "rc":
        if minor_text == "-rc":
            beta += 1
        else:
            minor_text = "-rc"
            beta = 1
    
    result = f"{release}{release_text}.{major}{major_text}.{minor}{minor_text}"
    if beta > 0:
        result = result + f"{beta}"
    
    return result


def update_version(old_version, new_version, version_files=None):
    versions = []
    update = False
    if version_files is None:
        version_files = VERSION_FILES

    for file_desc in version_files:
        file_path = file_desc["file"]
        _format = file_desc.get("format")
        location = file_desc.get("location", "")
        group = file_desc.get("group", 1)
        if "*" in file_path or "?" in file_path:
            # there is wildcard
            files = glob.glob(file_path)
        else:
            files = [file_path]

        for _file in files:
            update_version_in_file(_file, old_version, new_version, _format, location, group)