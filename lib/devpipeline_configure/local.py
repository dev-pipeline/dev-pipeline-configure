#!/usr/bin/python3

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


def consolidate_local_keys(full_config):
    for name, config in full_config.items():
        del name
        del_keys = []
        for key in config:
            for key_suffix in _KEY_SUFFIXES:
                match = key_suffix[0].search(key)
                if match:
                    if not _ENV_PATTERN.match(key):
                        key_suffix[1](
                            config, match.group(1), config.get(key, raw=True))
                        del_keys.append(key)
                    else:
                        devpipeline_configure.modifiers.append_value(
                            config, "dp.env_list", _ENV_VARIABLE.match(key).group(1))
        for del_key in del_keys:
            del config[del_key]
