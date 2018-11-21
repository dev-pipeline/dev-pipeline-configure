#!/usr/bin/python3

import os.path

import devpipeline_core.config.parser
import devpipeline_core.config.paths


def get_package_info(config):
    import_name = config.get("import")
    if import_name:
        colon_pos = import_name.find(':')
        package_name = import_name[:colon_pos]
        package_version = import_name[colon_pos + 1:]
        return (package_name, package_version)
    return None


def _get_packages_root():
    return devpipeline_core.config.paths._make_path(None, "packages.d")


def _get_package_path(base_dir, package_name):
    return os.path.join(base_dir, package_name, "versions.conf")


def get_package_config(package_name, version):
    package_path = _get_package_path(_get_packages_root(), package_name)
    package_config = devpipeline_core.config.parser.read_config(package_path)
    if package_config:
        if version in package_config:
            return package_config[version]
        raise Exception(
            "{} doesn't have version {}".format(
                package_name, version))
    raise Exception(
        "Failed to load package config for {}".format(package_name))
