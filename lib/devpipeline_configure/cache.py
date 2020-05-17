#!/usr/bin/python3

"""Manage and provide access to cached configuration."""


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

    def keys(self):
        return self._component.keys()

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

    def write(self, force=False):
        """Write the configuration."""
        if self.dirty or force:
            with open(self._cache_path, "w") as output_file:
                self._config.write(output_file)

    def __iter__(self):
        return iter(self._config)

    def __contains__(self, item):
        return item in self._config
