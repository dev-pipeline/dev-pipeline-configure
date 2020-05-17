#!/usr/bin/python3
"""This modules configures the build system - build cache, etc...."""

import devpipeline_core.command
import devpipeline_configure.config
import devpipeline_configure.version


def _choose_build_dir(arguments):
    if arguments.build_dir:
        return arguments.build_dir
    if arguments.profile:
        return "{}-{}".format(arguments.build_dir_basename, arguments.profile)
    return arguments.build_dir_basename


def _configure(parser):
    parser.add_argument(
        "--config", help="Build configuration file", default="build.config"
    )
    parser.add_argument(
        "--profile",
        help="Build-specific profiles to use.  If more than one profile is required, separate their names with commas.",
    )
    parser.add_argument(
        "--override",
        help="Collection of override options to use.  If you require multiple types of overrides, separate the names with commas.",
    )
    parser.add_argument(
        "--build-dir",
        help="Directory to store configuration.  If specified, --build-dir-basename will be ignored.",
    )
    parser.add_argument(
        "--build-dir-basename",
        help="Basename for build directory configuration",
        default="build",
    )
    parser.add_argument(
        "--root-dir",
        help="Root directory for checkouts.  Defaults to the same path as build configuration.",
    )
    devpipeline_core.command.add_version_info(
        parser, devpipeline_configure.version.STRING
    )


def _execute(arguments):
    ex_args = {
        "profiles": arguments.profile,
        "overrides": arguments.override,
    }
    if "root_dir" in arguments:
        ex_args["src_root"] = arguments.root_dir
    config = devpipeline_configure.config.process_config(
        arguments.config, _choose_build_dir(arguments), "build.cache", **ex_args
    )
    devpipeline_core.sanitizer.sanitize(
        config, lambda n, m: print("{} [{}]".format(m, n))
    )


_CONFIGURE_COMMAND = ("Configure a project build directory.", _configure, _execute)
