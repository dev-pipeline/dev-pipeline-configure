#!/usr/bin/python3
"""This modules configures the build system - build cache, etc...."""

import argparse
import os.path

import devpipeline_core.command
import devpipeline_configure.cache
import devpipeline_configure.config
import devpipeline_configure.load
import devpipeline_configure.version


def _optional_append(original, new):
    if original and new:
        return "{},{}".format(original, new)
    return original or new


def _calculate_value(config, config_key, arguments, key):
    original = config.get("DEFAULT", config_key, fallback="")
    if key in arguments:
        # this feels hacky; there's gotta be a better way to access
        # the value through a programatic key
        new = arguments.__dict__.get(key)
        if arguments.append:
            return _optional_append(original, new)
        return new
    return original


def _configure(parser):
    parser.add_argument(
        "--profiles",
        help="Comma-separated list of profiles to use.",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--overrides",
        help="Comma-separated list of overrides to use.",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--append",
        help="Append provided profiles/overrides instead of replacing",
        action="store_true",
    )
    devpipeline_core.command.add_version_info(
        parser, devpipeline_configure.version.STRING
    )


def _execute(arguments):
    config_file = devpipeline_configure.load.find_config()
    cache_config = devpipeline_configure.parser.read_config(config_file)
    profiles = _calculate_value(cache_config, "dp.profile_name", arguments, "profiles")
    overrides = _calculate_value(cache_config, "dp.overrides", arguments, "overrides")

    cache = devpipeline_configure.config.process_config(
        cache_config.get("DEFAULT", "dp.build_config"),
        os.path.dirname(config_file),
        "build.cache",
        profiles=profiles or None,
        overrides=overrides or None,
        src_root=cache_config.get("DEFAULT", "dp.src_root"),
    )
    devpipeline_core.sanitizer.sanitize(
        cache, lambda n, m: print("{} [{}]".format(m, n))
    )


_RECONFIGURE_COMMAND = ("Reconfigure a project build directory.", _configure, _execute)
