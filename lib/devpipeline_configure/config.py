#!/usr/bin/python3

"""A module to manage configuring a project."""

import os.path
import os

import devpipeline_core.paths
import devpipeline_core.plugin
import devpipeline_configure.cache
import devpipeline_configure.local
import devpipeline_configure.packages
import devpipeline_configure.parser
import devpipeline_configure.profiles
import devpipeline_configure.overrides
import devpipeline_configure.version


def split_list(values, split_string=","):
    """
    Convert a delimited string to a list.

    Arguments
    values -- a string to split
    split_string -- the token to use for splitting values
    """
    return [value.strip() for value in values.split(split_string)]


def _is_cache_dir_appropriate(cache_dir, cache_file):
    """
    Determine if a directory is acceptable for building.

    A directory is suitable if any of the following are true:
      - it doesn't exist
      - it is empty
      - it contains an existing build cache
    """
    if os.path.exists(cache_dir):
        files = os.listdir(cache_dir)
        if cache_file in files:
            return True
        return not bool(files)
    return True


def _add_default_options(config, state):
    for key, value in state.items():
        config["DEFAULT"][key] = value


def _apply_import(section_config, import_config):
    for key in import_config:
        if key not in section_config:
            section_config[key] = import_config.get(key, raw=True)


def _handle_imports(config):
    for section in config.sections():
        section_config = config[section]
        import_info = devpipeline_configure.packages.get_package_info(section_config)
        if import_info:
            _apply_import(
                section_config,
                devpipeline_configure.packages.get_package_config(
                    section_config, *import_info
                ),
            )
            section_config["dp.import_name"] = import_info[0]
            section_config["dp.import_version"] = import_info[1]


def _create_cache(raw_path, cache_dir, cache_file):
    if _is_cache_dir_appropriate(cache_dir, cache_file):
        config = devpipeline_configure.parser.read_config(raw_path)
        abs_path = os.path.abspath(raw_path)
        root_state = {
            "dp.build_config": abs_path,
            "dp.src_root": os.path.dirname(abs_path),
            "dp.version": format(devpipeline_configure.version.ID, "02x"),
            "dp.config_dir": os.path.join(os.path.expanduser("~"), ".dev-pipeline.d"),
        }
        root_state["dp.build_root"] = os.path.join(os.getcwd(), cache_dir)
        _add_default_options(config, root_state)
        _handle_imports(config)
        return config
    raise Exception("{} doesn't look like a dev-pipeline folder".format(cache_dir))


def _write_config(config, cache_dir):
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    config.write()


def _set_list(config, kwargs_key, config_key, **kwargs):
    values = kwargs.get(kwargs_key)
    if values:
        config["DEFAULT"][config_key] = values


_CONFIG_MODIFIERS = [
    lambda config, **kwargs: _set_list(config, "profiles", "dp.profile_name", **kwargs),
    lambda config, **kwargs: _set_list(config, "overrides", "dp.overrides", **kwargs),
]

_COMPONENT_MODIFIERS = devpipeline_core.plugin.query_plugins(
    "devpipeline.config_modifiers"
)


def _add_package_options(cache):
    for name, mod_fn in _COMPONENT_MODIFIERS.items():
        del name
        mod_fn(cache)


def _consolidate_envs(cache):
    for name, config in cache.items():
        del name
        env_list = config.get_list("dp.env_list")
        if env_list:
            env_dict = {}
            for env in env_list:
                env_dict[env] = None
            config.set("dp.env_list", ",".join(env_dict.keys()))


_VALUE_MODIFIERS = [
    devpipeline_configure.local.consolidate_local_keys,
    devpipeline_configure.profiles.apply_profiles,
    devpipeline_configure.overrides.apply_overrides,
    _consolidate_envs,
]


def _handle_value_modifiers(config):
    for modifier_fn in _VALUE_MODIFIERS:
        modifier_fn(config)


def process_config(raw_path, cache_dir, cache_file, **kwargs):
    """
    Read a build configuration and create it, storing the result in a build
    cache.

    Arguments
    raw_path -- path to a build configuration
    cache_dir -- the directory where cache should be written
    cache_file -- The filename to write the cache.  This will live inside
                  cache_dir.
    **kwargs -- additional arguments used by some modifiers
    """
    config = _create_cache(raw_path, cache_dir, cache_file)
    for modifier in _CONFIG_MODIFIERS:
        modifier(config, **kwargs)
    # pylint: disable=protected-access
    cache = devpipeline_configure.cache._CachedConfig(
        config, os.path.join(cache_dir, cache_file)
    )
    _handle_value_modifiers(cache)
    _add_package_options(cache)
    _write_config(cache, cache_dir)
    return cache
