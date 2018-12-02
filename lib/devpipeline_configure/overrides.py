#!/usr/bin/python3

import devpipeline_core.paths

import devpipeline_configure.parser
import devpipeline_configure.modifiers


_SECTIONS = [
    ("prepend", devpipeline_configure.modifiers.prepend_value),
    ("append", devpipeline_configure.modifiers.append_value),
    ("override", devpipeline_configure.modifiers.override_value),
    ("erase", devpipeline_configure.modifiers.erase_value)
]


def _get_override_path(config, override_name, package_name):
    return devpipeline_core.paths.make_path(config, "overrides.d",
                                            override_name,
                                            "{}.conf".format(package_name))


def _apply_override(override_name, config):
    for component in config.components():
        component_config = config.get(component)
        override_path = _get_override_path(
            component_config, override_name, component)
        if os.path.isfile(override_path):
            override_config = devpipeline_configure.parser.read_config(
                override_path)
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
