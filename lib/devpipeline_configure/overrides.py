#!/usr/bin/python3

import os.path

import devpipeline_core.paths

import devpipeline_configure.parser
import devpipeline_configure.modifiers


def get_override_path(config, override_name, package_name):
    return devpipeline_core.paths.make_path(
        config, "overrides.d", override_name, "{}.conf".format(package_name)
    )


def _apply_single_override(override_path, config):
    if os.path.isfile(override_path):
        override_config = devpipeline_configure.parser.read_config(override_path)
        devpipeline_configure.modifiers.apply_config_modifiers(override_config, config)
        return True
    return False


def _apply_override(override_name, full_config):
    for name, config in full_config.items():
        applied_overrides = []
        override_path = get_override_path(config, override_name, name)
        if _apply_single_override(override_path, config):
            applied_overrides.append(override_name)
        if applied_overrides:
            config.set("dp.applied_overrides", ",".join(applied_overrides))


def apply_overrides(config):
    override_list = config.get("DEFAULT").get_list("dp.overrides")
    for override in override_list:
        _apply_override(override, config)
