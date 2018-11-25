#!/usr/bin/python3

import os.path

import devpipeline_core.config.parser
import devpipeline_core.config.paths

import devpipeline_configure.modifiers


_SECTIONS = [
    ("prepend", devpipeline_configure.modifiers.prepend_value),
    ("append", devpipeline_configure.modifiers.append_value),
    ("override", devpipeline_configure.modifiers.override_value),
    ("erase", devpipeline_configure.modifiers.erase_value)
]

_OVERRIDES_PATH = devpipeline_core.config.paths._make_path(
    None, "overrides.d")


def _get_override_path(override_name, package_name):
    return os.path.join(_OVERRIDES_PATH, override_name,
                        "{}.conf".format(package_name))


def _apply_override(override_name, config):
    for component in config.components():
        override_path = _get_override_path(override_name, component)
        if os.path.isfile(override_path):
            override_config = devpipeline_core.config.parser.read_config(
                override_path)
            component_config = config.get(component)
            for override_section in _SECTIONS:
                if override_config.has_section(override_section[0]):
                    for override_key, override_value in override_config[override_section[0]].items(
                    ):
                        override_section[1](
                            component_config, override_key, override_value)


def apply_overrides(config):
    override_list = config.get("DEFAULT").get_list("dp.overrides")
    for override in override_list:
        _apply_override(override, config)
