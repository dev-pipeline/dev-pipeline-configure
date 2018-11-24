#!/usr/bin/python3

import os.path
import re

import devpipeline_core.config.parser
import devpipeline_core.config.paths

import devpipeline_configure.modifiers


def _read_profiles(path):
    if os.path.isfile(path):
        return devpipeline_core.config.parser.read_config(path)
    raise Exception("Unable to load profile file ({})".format(path))


_KEY_SUFFIXES = [
    (re.compile(R"([\w\.\-]+)\.prepend$"),
     devpipeline_configure.modifiers.prepend_value),
    (re.compile(R"([\w\.\-]+)\.append$"),
     devpipeline_configure.modifiers.append_value),
    (re.compile(R"([\w\.\-]+)\.override$"),
     devpipeline_configure.modifiers.override_value),
    (re.compile(R"([\w\.\-]+)\.erase$"),
     devpipeline_configure.modifiers.erase_value)
]


def _apply_each_profile(profiles, profile_list, config):
    for profile_name in profile_list:
        profile = profiles[profile_name]
        for component in config.components():
            component_config = config.get(component)
            for profile_key, profile_value in profile.items():
                for key_suffix in _KEY_SUFFIXES:
                    m = key_suffix[0].search(profile_key)
                    if m:
                        key_suffix[1](
                            component_config, m.group(1), profile_value)


_PROFILES_PATH = devpipeline_core.config.paths._make_path(
    None, "profiles.conf")


def apply_profiles(config):
    profile_list = config.get("DEFAULT").get_list("dp.profile_name")
    if profile_list:
        profiles = _read_profiles(_PROFILES_PATH)
        _apply_each_profile(profiles, profile_list, config)
