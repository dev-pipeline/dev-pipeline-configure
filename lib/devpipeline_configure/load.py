#!/usr/bin/python3

import os
import os.path

import devpipeline_core.sanitizer

import devpipeline_configure.cache
import devpipeline_configure.config
import devpipeline_configure.overrides
import devpipeline_configure.parser
import devpipeline_configure.profiles


def find_config():
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
    raw_mtime = os.path.getmtime(config.get("DEFAULT").get("dp.build_config"))
    return cache_mtime < raw_mtime


def _updated_software(config, cache_mtime):
    # pylint: disable=unused-argument
    config_version = config.get("DEFAULT").get("dp.version", fallback="0")
    return devpipeline_configure.version.ID > int(config_version, 16)


def _profiles_changed(config, cache_mtime):
    default_config = config.get("DEFAULT")
    profile_list = default_config.get_list("dp.profile_name")
    if profile_list:
        if os.path.isdir(
            devpipeline_configure.profiles.get_root_profile_path(default_config)
        ):
            for profile in profile_list:
                for name, component_config in config.items():
                    del name
                    profile_path = devpipeline_configure.profiles.get_individual_profile_path(
                        component_config, profile
                    )
                    if os.path.isfile(profile_path):
                        if cache_mtime < os.path.getmtime(profile_path):
                            return True
        else:
            profile_path = devpipeline_configure.profiles.get_profile_path(config)
            if os.path.isfile(profile_path):
                return cache_mtime < os.path.getmtime(profile_path)
    return False


def _check_specific_override(
    override_name, applied_overrides, component_config, component_name, cache_mtime
):
    override_path = devpipeline_configure.overrides.get_override_path(
        component_config, override_name, component_name
    )
    if override_name in applied_overrides:
        if not os.path.isfile(override_path):
            # has it been removed?
            return True
        raw_mtime = os.path.getmtime(override_path)
        if cache_mtime < raw_mtime:
            # is it newer?
            return True
    elif os.path.isfile(override_path):
        # is it a new file?
        return True
    return False


def _overrides_changed(config, cache_mtime):
    default_config = config.get("DEFAULT")
    override_list = default_config.get_list("dp.overrides")
    for component_name, component_config in config.items():
        applied_overrides = component_config.get_list("dp.applied_overrides")
        # see if the applied overrides have been deleted
        for override_name in override_list:
            if _check_specific_override(
                override_name,
                applied_overrides,
                component_config,
                component_name,
                cache_mtime,
            ):
                return True
    return False


_OUTDATED_CHECKS = [
    _raw_updated,
    _updated_software,
    _profiles_changed,
    _overrides_changed,
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
        cache_file = find_config()
    cache_config = devpipeline_configure.parser.read_config(cache_file)
    cache = devpipeline_configure.cache._CachedConfig(cache_config, cache_file)
    if force or _is_outdated(cache_file, cache):
        cache = devpipeline_configure.config.process_config(
            cache_config.get("DEFAULT", "dp.build_config"),
            os.path.dirname(cache_file),
            "build.cache",
            profiles=cache_config.get("DEFAULT", "dp.profile_name", fallback=None),
            overrides=cache_config.get("DEFAULT", "dp.overrides", fallback=None),
            src_root=cache_config.get("DEFAULT", "dp.src_root"),
        )
        devpipeline_core.sanitizer.sanitize(
            cache, lambda n, m: print("{} [{}]".format(m, n))
        )
    return cache
