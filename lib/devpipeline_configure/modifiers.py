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


_ENV_PATTERN = re.compile(R"^env\.")


def append_value(config, key, value):
    if _ENV_PATTERN.match(key):
        key += ".append"
    _append_helper(config, key, value)


def prepend_value(config, key, value):
    if _ENV_PATTERN.match(key):
        key += ".prepend"
    _prepend_helper(config, key, value)


def override_value(config, key, value):
    if _ENV_PATTERN.match(key):
        _erase_helper(config, key + ".append")
        _erase_helper(config, key + ".prepend")
    config[key] = value


def erase_value(config, key, value):
    del value
    if _ENV_PATTERN.match(key):
        _erase_helper(config, key + ".append")
        _erase_helper(config, key + ".prepend")
    _erase_helper(config, key)
