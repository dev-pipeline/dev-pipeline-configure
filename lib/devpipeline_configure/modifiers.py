#!/usr/bin/python3


def append_value(config, key, value):
    if key in config:
        config[key] = "{},{}".format(config[key], value)
    else:
        config[key] = value


def prepend_value(config, key, value):
    if key in config:
        config[key] = "{},{}".format(value, config[key])
    else:
        config[key] = value


def override_value(config, key, value):
    config[key] = value


def erase_value(config, key, value):
    del value
    del config[key]
