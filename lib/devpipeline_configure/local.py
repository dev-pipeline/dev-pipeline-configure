#!/usr/bin/python3

import re

import devpipeline_configure.modifiers


_KEY_SUFFIXES = [
    (
        re.compile(r"([\w\.\-]+)\.prepend$"),
        devpipeline_configure.modifiers.prepend_value,
    ),
    (re.compile(r"([\w\.\-]+)\.append$"), devpipeline_configure.modifiers.append_value),
]

_ENV_PATTERN = re.compile(r"^env\.")
_ENV_VARIABLE = re.compile(r"env.(\w+)")


def _check_single_key(key, config):
    found_keys = []
    for key_suffix in _KEY_SUFFIXES:
        match = key_suffix[0].search(key)
        if match:
            if not _ENV_PATTERN.match(key):
                key_suffix[1](config, match.group(1), config.get(key, raw=True))
                found_keys.append(key)
            else:
                devpipeline_configure.modifiers.append_value(
                    config, "dp.env_list", _ENV_VARIABLE.match(key).group(1)
                )
    return found_keys


def _check_config_keys(config):
    found_keys = []
    for key in config:
        local_keys = _check_single_key(key, config)
        found_keys.extend(local_keys)
    for found_key in found_keys:
        del config[found_key]


def consolidate_local_keys(full_config):
    for name, config in full_config.items():
        del name
        _check_config_keys(config)
