#!/usr/bin/python3

import os.path
import re

import devpipeline_configure.modifiers


_KEY_SUFFIXES = [
    (re.compile(R"([\w\.\-]+)\.prepend$"),
     devpipeline_configure.modifiers.prepend_value),
    (re.compile(R"([\w\.\-]+)\.append$"),
     devpipeline_configure.modifiers.append_value)
]

_ENV_PATTERN = re.compile(R"^env\.")
_ENV_VARIABLE = re.compile(R"env.(\w+)")


def consolidate_local_keys(config):
    for component in config.components():
        component_config = config.get(component)
        del_keys = []
        for key in component_config:
            for key_suffix in _KEY_SUFFIXES:
                m = key_suffix[0].search(key)
                if m:
                    if not _ENV_PATTERN.match(key):
                        key_suffix[1](
                            component_config, m.group(1), component_config.get(key, raw=True))
                        del_keys.append(key)
                    else:
                        devpipeline_configure.modifiers.append_value(component_config, "dp.env_list", _ENV_VARIABLE.match(key).group(1))
        for del_key in del_keys:
            del component_config[del_key]
