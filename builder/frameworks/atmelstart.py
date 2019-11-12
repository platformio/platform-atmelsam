# AtmelStart Framework build script
# Author: Frank Leon Rose
# Copyright (c) 2019
#
# Given framework = atmelstart, this builder will look for an
# `atstart_file = myproject.atstart` line in the Platformio environment.
# It will use that file to request a package of generated code from
# Atmel Start (start.atmel.com).
# Then it will build the env with the generated code files.

import sys
import os
import os.path
import re
import json
import requests
import zipfile

env = DefaultEnvironment()

try:
    import yaml
except ImportError:
    env.Execute("$PYTHONEXE -m pip install pyyaml")
    import yaml
from yaml import Loader

env.SConscript("_bare.py")

DOWNLOAD_DIR = os.path.join(env.subst('$PROJECT_WORKSPACE_DIR'), "atmelstart_downloads")
BUILD_DIR = os.path.join(env.subst('$PROJECT_BUILD_DIR'), env.subst('$PIOENV'))
PACKAGES_DIR = os.path.join(BUILD_DIR, "atmelstart_packages")
output_filename = os.path.join(BUILD_DIR, "atmelstart.json")

atstart_file = env.BoardConfig().get("build.atmelstart.atstart_file", None)
if atstart_file is None:
    sys.stderr.write("Error: Please specify property `board_build.atmelstart.atstart_file = myproject.atstart`.\nThe file path is relative to the project directory.\n")
    env.Exit(1)
input_filename = os.path.join(env['PROJECT_DIR'], atstart_file)
if not os.path.isfile(input_filename):
    sys.stderr.write("Error: atstart_file specifies a non-existent or invalid file: {}\n".format(input_filename))
    env.Exit(1)

def convert_config_yaml_to_json(input, output):
    def dictToArray(d, idKey):
        a = []
        for (key, value) in d.items():
            if idKey:
                value[idKey] = key
            a.append(value)
        return a

    def fixDefinition(a):
        for element in a:
            element["definition"] = {
              "identifier": element["definition"],
              "base": element["definition"]
            }

    def sort_config(config):
        config["middlewares"].sort(key=lambda x: x["identifier"])
        config["drivers"].sort(key=lambda x: x["identifier"])
        config["pads"].sort(key=lambda x: x["name"])

        # Force order of keys in configuration. Fails to accept configuration without this.
        sorted_config = {}
        for key in ['jsonForm', 'formatVersion', 'board', 'identifier', 'name', 'details', 'application', 'middlewares', 'drivers', 'pads']:
            sorted_config[key] = config[key]

        return sorted_config

    def load_yaml(input_filename):
        with open(input_filename, "r") as f:
            config = yaml.load(f, Loader=Loader)
        config["middlewares"] = dictToArray(config["middlewares"], "identifier")
        config["drivers"] = dictToArray(config["drivers"], "identifier")
        config["pads"] = dictToArray(config["pads"], None)
        config["jsonForm"] = "=1"
        config["formatVersion"] = 2
        config["identifier"] = ""
        fixDefinition(config["drivers"])

        return config

    def load_json(input_filename):
        with open(input_filename, "r") as f:
            return json.load(f)

    def dump(config, output_filename, pretty = False):
        with open(output_filename, "w") as f:
            indent = 2
            separators = (',', ': ')
            if not pretty:
                indent = None
                separators = (',', ':')
            json.dump(config, f, indent=indent, separators=separators, sort_keys=pretty)

    # json_file = load("atmel_start_config.json")
    config = load_yaml(input)
    config = sort_config(config)
    dump(config, output)

def hash_file(file):
    import hashlib
    m = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            m.update(chunk)
    return m.hexdigest()

def download_package(config_file, download_dir, packages_dir):
    hash = hash_file(config_file)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    filename = os.path.join(download_dir, hash + '.zip')
    if os.path.isfile(filename):
        print('NOTE: Atmel Start package', filename, 'already downloaded. Delete it and re-run if you want to re-download')
    else:
        print("Downloading Atmel Start package", filename, "...")
        with open(config_file, 'r') as project_json:
            headers = {'content-type': 'text/plain'}
            r = requests.post('http://start.atmel.com/api/v1/generate/?format=atzip&compilers=[atmel_studio,make]&file_name_base=atmel_start_config', headers=headers, data=project_json)
        if not r.ok:
            # Double check that the JSON is minified. If it's not, you'll get a 404.
            print(r.text)
            sys.exit(1)
        with open(filename, 'wb') as out:
            out.write(r.content)

    package_dir = os.path.join(packages_dir, hash)
    if not os.path.isdir(package_dir):
        print("Unzipping ...")
        z = zipfile.ZipFile(filename)
        z.extractall(package_dir)

    return package_dir

convert_config_yaml_to_json(input_filename, output_filename)
package_dir = download_package(output_filename, DOWNLOAD_DIR, PACKAGES_DIR)

def valid_source(p):
    return "armcc" not in p and "IAR" not in p and "RVDS" not in p

include_paths = []
source_paths = []
linker_script = None
for dirpath, dirnames, filenames in os.walk(package_dir):
    if valid_source(dirpath):
        if any(".h" in fn for fn in filenames):
            include_paths.append(dirpath)
        if any(".c" in fn for fn in filenames):
            source_paths.append(dirpath)

    if "gcc" in dirpath:
        for fn in filenames:
            if "flash.ld" in fn:
                linker_script = os.path.realpath(os.path.join(dirpath, fn))

if linker_script is None or not os.path.isfile(linker_script):
    sys.stderr.write("Error: Failed to find linker script in downloaded package.\n")
    env.Exit(1)

def adjust_linker_offset(script_name, ldscript):
    offset_address = env.BoardConfig().get("upload.offset_address", "0")
    if int(offset_address, 0)==0:
        return ldscript

    content = ""
    with open(ldscript) as fp:
        content = fp.read()
        # original:     rom      (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00040000
        # transformed:  rom      (rx)  : ORIGIN = 0x00000000+0x2000, LENGTH = 0x00040000-0x2000
        content = re.sub(
            r"^(\s*rom.*ORIGIN[^,]+)(,\s*LENGTH.*)$",
            r"\1+%s\2-%s" % (offset_address, offset_address),
            content, flags=re.MULTILINE)

    offset_script = os.path.join(BUILD_DIR,
                    "%s_flash_%s.ld" % (script_name, offset_address))

    with open(offset_script, "w") as fp:
        fp.write(content)

    return offset_script

linker_script = adjust_linker_offset(env.subst('$PIOENV'), linker_script)
env.Replace(LDSCRIPT_PATH=linker_script)

env.Append(CPPPATH=[os.path.realpath(p) for p in include_paths])

sources = ["-<*>"]
sources.extend(["+<{}>".format(os.path.join(sp, '*.c')) for sp in source_paths])
sources.append("-<{}>".format('main.c'))

env.BuildSources(
    os.path.join("$BUILD_DIR", "FrameworkCMSISVariant"),
    package_dir,
    sources
)
