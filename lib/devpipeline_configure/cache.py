#!/usr/bin/python3

"""Manage and provide access to cached configuration."""

import os.path

import devpipeline_core.sanitizer

import devpipeline_configure.config
import devpipeline_configure.overrides
import devpipeline_configure.profiles
import devpipeline_configure.parser


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
    raw_mtime = os.path.getmtime(config.get("DEFAULT").get("dp.build_config"))
    return cache_mtime < raw_mtime


def _updated_software(config, cache_mtime):
    # pylint: disable=unused-argument
    config_version = config.get("DEFAULT").get("dp.version", fallback="0")
    return devpipeline_configure.version.ID > int(config_version, 16)


def _profiles_changed(config, cache_mtime):
    default_config = config.get("DEFAULT")
    if "dp.profile_name" in default_config:
        profile_path = devpipeline_configure.profiles.get_profile_path(config)
        if os.path.isfile(profile_path):
            return cache_mtime < os.path.getmtime(profile_path)
        return True
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


class _CachedComponetKeys:
    # pylint: disable=too-few-public-methods
    def __init__(self, component):
        self._iter = iter(component)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iter)


class _CachedComponent:
    def __init__(self, component, main_config):
        self._component = component
        self._main_config = main_config

    @property
    def name(self):
        """Retrieve the component's name"""
        return self._component.name

    def get(self, key, raw=False, fallback=None):
        """
        Get a string value from the componnet.

        Arguments:
        key - the key to retrieve
        raw - Control whether the value is interpolated or returned raw.  By
              default, values are interpolated.
        fallback - The return value if key isn't in the component.
        """
        return self._component.get(key, raw=raw, fallback=fallback)

    def get_list(self, key, fallback=None, split=","):
        """
        Retrieve a value in list form.

        The interpolated value will be split on some key (by default, ',') and
        the resulting list will be returned.

        Arguments:
        key - the key to return
        fallback - The result to return if key isn't in the component.  By
                   default, this will be an empty list.
        split - The key to split the value on.  By default, a comma (,).
        """
        fallback = fallback or []
        raw = self.get(key, None)
        if raw:
            return [value.strip() for value in raw.split(split)]
        return fallback

    def set(self, key, value):
        """
        Set a value in the component.

        Arguments:
        key - the key to set
        value - the new value
        """
        if self._component.get(key, raw=True) != value:
            self._component[key] = value
            self._main_config.dirty = True

    def __iter__(self):
        return _CachedComponetKeys(self._component)

    def __contains__(self, item):
        return item in self._component

    def __delitem__(self, key):
        del self._component[key]

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)


class _CachedComponentIterator:
    # pylint: disable=too-few-public-methods
    def __init__(self, sections, main_config):
        self._iter = iter(sections)
        self._main_config = main_config

    def __iter__(self):
        return self

    def __next__(self):
        component = next(self._iter)
        return (component, self._main_config.get(component))


class _CachedConfig:
    def __init__(self, config, cache_path):
        self._config = config
        self._cache_path = cache_path
        self.dirty = False

    def keys(self):
        """Get a list of component names provided by a configuration."""
        return self._config.sections()

    def items(self):
        return _CachedComponentIterator(self._config.sections(), self)

    def get(self, component):
        """Get a specific component to operate on"""
        return _CachedComponent(self._config[component], self)

    def write(self):
        """Write the configuration."""
        if self.dirty:
            with open(self._cache_path, "w") as output_file:
                self._config.write(output_file)

    def __iter__(self):
        return iter(self._config)

    def __contains__(self, item):
        return item in self._config


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
    cache_config = devpipeline_configure.parser.read_config(cache_file)
    cache = _CachedConfig(cache_config, cache_file)
    if force or _is_outdated(cache_file, cache):
        cache = devpipeline_configure.config.process_config(
            cache_config.get("DEFAULT", "dp.build_config"),
            os.path.dirname(cache_file),
            "build.cache",
            profiles=cache_config.get("DEFAULT", "dp.profile_name", fallback=None),
            overrides=cache_config.get("DEFAULT", "dp.overrides", fallback=None),
        )
        devpipeline_core.sanitizer.sanitize(
            cache, lambda n, m: print("{} [{}]".format(m, n))
        )
    return cache
