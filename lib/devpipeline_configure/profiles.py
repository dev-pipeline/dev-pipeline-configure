#!/usr/bin/python3

import os.path
import re

import devpipeline_core.paths
import devpipeline_configure.parser

import devpipeline_configure.modifiers


def get_profile_path(config):
    return devpipeline_core.paths.make_path(config.get("DEFAULT"), "profiles.conf")


def _read_profiles(configuration):
    path = get_profile_path(configuration)
    if os.path.isfile(path):
        return devpipeline_configure.parser.read_config(path)
    raise Exception("Unable to load profile file ({})".format(path))


_KEY_SUFFIXES = [
    (
        re.compile(r"([\w\.\-]+)\.prepend$"),
        devpipeline_configure.modifiers.prepend_value,
    ),
    (re.compile(r"([\w\.\-]+)\.append$"), devpipeline_configure.modifiers.append_value),
    (
        re.compile(r"([\w\.\-]+)\.override$"),
        devpipeline_configure.modifiers.override_value,
    ),
    (re.compile(r"([\w\.\-]+)\.erase$"), devpipeline_configure.modifiers.erase_value),
]


def _apply_single_profile(component_config, profile):
    for profile_key, profile_value in profile.items():
        for key_suffix in _KEY_SUFFIXES:
            match = key_suffix[0].search(profile_key)
            if match:
                key_suffix[1](component_config, match.group(1), profile_value)


def _apply_each_profile(profiles, profile_list, config):
    for profile_name in profile_list:
        profile = profiles[profile_name]
        for name, component_config in config.items():
            del name
            _apply_single_profile(component_config, profile)


def get_root_profile_path(config):
    return devpipeline_core.paths.make_path(config, "profiles.d")


def get_individual_profile_path(config, profile_name):
    return devpipeline_core.paths.make_path(
        config, "profiles.d", "{}.conf".format(profile_name)
    )


def _apply_individual_profile(profile_path, full_config):
    profile_config = devpipeline_configure.parser.read_config(profile_path)
    for name, component_config in full_config.items():
        del name
        devpipeline_configure.modifiers.apply_config_modifiers(
            profile_config, component_config
        )


def _apply_profiles(full_config, profile_list):
    default_config = full_config.get("DEFAULT")
    for profile in profile_list:
        _apply_individual_profile(
            get_individual_profile_path(default_config, profile), full_config
        )


def apply_profiles(config):
    profile_list = config.get("DEFAULT").get_list("dp.profile_name")
    if profile_list:
        if os.path.isdir(get_root_profile_path(config.get("DEFAULT"))):
            _apply_profiles(config, profile_list)
        else:
            profiles = _read_profiles(config)
            _apply_each_profile(profiles, profile_list, config)
