#!/usr/bin/python3

"""Manage and provide access to cached configuration."""

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

    def get_list(self, key, fallback=None, split=','):
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
        if self._component.get(key) != value:
            self._component[key] = value
            self._main_config.dirty = True

    def __iter__(self):
        return _CachedComponetKeys(self._component)


class _CachedComponentIterator:
    # pylint: disable=too-few-public-methods
    def __init__(self, sections, main_config):
        self._iter = iter(sections)
        self._main_config = main_config

    def __iter__(self):
        return self

    def __next__(self):
        component = next(self._iter)
        return _CachedComponent(component, self._main_config)


class _CachedConfig:
    def __init__(self, config, cache_path):
        self._config = config
        self._cache_path = cache_path
        self.dirty = False

    def components(self):
        """Get a list of component names provided by a configuration."""
        return self._config.sections()

    def get(self, component):
        """Get a specific component to operate on"""
        return _CachedComponent(self._config[component], self)

    def write(self):
        """Write the configuration."""
        if self.dirty:
            with open(self._cache_path, 'w') as output_file:
                self._config.write(output_file)

    def __iter__(self):
        return _CachedComponentIterator(self._config.sections(), self)

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
    return _CachedConfig(cache_config, cache_file)
