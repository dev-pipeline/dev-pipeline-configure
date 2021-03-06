#!/usr/bin/python3

import re


def _append_helper(config, key, value):
    if key in config:
        config[key] = "{},{}".format(config.get(key, raw=True), value)
    else:
        config[key] = value


def _prepend_helper(config, key, value):
    if key in config:
        config[key] = "{},{}".format(value, config.get(key, raw=True))
    else:
        config[key] = value


def _erase_helper(config, key):
    if key in config:
        del config[key]


_ENV_PATTERN = re.compile(r"^env\.")


def _append_prepend_helper(config, key, key_suffix, helper_fn, value):
    if _ENV_PATTERN.match(key):
        key = "{}.{}".format(key, key_suffix)
    _append_helper(config, key, value)


def append_value(config, key, value):
    _append_prepend_helper(config, key, "append", _append_helper, value)


def prepend_value(config, key, value):
    _append_prepend_helper(config, key, "prepend", _prepend_helper, value)


def erase_value(config, key, value):
    del value
    if _ENV_PATTERN.match(key):
        _erase_helper(config, key + ".append")
        _erase_helper(config, key + ".prepend")
    _erase_helper(config, key)


def override_value(config, key, value):
    erase_value(config, key, value)
    config[key] = value


_CONFIG_SECTIONS = [
    ("prepend", prepend_value),
    ("append", append_value),
    ("override", override_value),
    ("erase", erase_value),
]


def apply_config_modifiers(modifier_config, component_config):
    for modifier_section in _CONFIG_SECTIONS:
        if modifier_config.has_section(modifier_section[0]):
            for key, value in modifier_config[modifier_section[0]].items():
                modifier_section[1](component_config, key, value)
