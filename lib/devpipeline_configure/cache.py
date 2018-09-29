#!/usr/bin/python3

import os.path

import devpipeline_core.config.parser

import devpipeline_configure.config


def _find_config():
    """Find a build cache somewhere in a parent directory."""
    previous = ""
    current = os.getcwd()
    while previous != current:
        check_path = os.path.join(current, "build.cache")
        if os.path.isfile(check_path):
            return check_path
        else:
            previous = current
            current = os.path.dirname(current)
    raise Exception("Can't find build cache")


def _raw_updated(config, cache_mtime):
    raw_mtime = os.path.getmtime(config.get("DEFAULT", "dp.build_config"))
    return cache_mtime < raw_mtime


def _updated_software(config, cache_mtime):
    # pylint: disable=unused-argument
    config_version = config.get("DEFAULT", "dp.version", fallback="0")
    return devpipeline_configure.version.ID > int(config_version, 16)


_OUTDATED_CHECKS = [
    _raw_updated,
    _updated_software
]


def _is_outdated(cache_file, cache_config):
    cache_mt = os.path.getmtime(cache_file)
    for check in _OUTDATED_CHECKS:
        if check(cache_config, cache_mt):
            return True
    return False


def update_cache(force=False, cache_file=None):
    """
    Load a build cache, updating it if necessary.

    A cache is considered outdated if any of its inputs have changed.

    Arguments
    force -- Consider a cache outdated regardless of whether its inputs have
             been modified.
    """
    if not cache_file:
        cache_file = _find_config()
    cache_config = devpipeline_core.config.parser.read_config(cache_file)
    if force or _is_outdated(cache_file, cache_config):
        cache_config = devpipeline_configure.config.process_config(
            cache_config.get("DEFAULT", "dp.build_config"),
            os.path.dirname(cache_file), "build.cache",
            profiles=cache_config.get("DEFAULT", "dp.profile_name",
                                      fallback=None),
            overrides=cache_config.get("DEFAULT", "dp.overrides",
                                       fallback=None))
    return cache_config
