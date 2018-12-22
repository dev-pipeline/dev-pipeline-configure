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


class Configure(devpipeline_core.command.Command):

    """This class manages the configuration of the project."""

    def __init__(self):
        super().__init__(
            prog="dev-pipeline configure", description="Configure a project"
        )
        self.add_argument(
            "--config", help="Build configuration file", default="build.config"
        )
        self.add_argument(
            "--profile",
            help="Build-specific profiles to use.  If more than one profile is required, separate their names with commas.",
        )
        self.add_argument(
            "--override",
            help="Collection of override options to use.  If you require multiple types of overrides, separate the names with commas.",
        )
        self.add_argument(
            "--build-dir",
            help="Directory to store configuration.  If specified, --build-dir-basename will be ignored.",
        )
        self.add_argument(
            "--build-dir-basename",
            help="Basename for build directory configuration",
            default="build",
        )
        self.set_version(devpipeline_configure.version.STRING)

        self.build_dir = None
        self.config = None
        self.overrides = None
        self.profile = None

    def setup(self, arguments):
        self.build_dir = _choose_build_dir(arguments)
        self.profile = arguments.profile
        self.config = arguments.config
        self.overrides = arguments.override

    def process(self):
        config = devpipeline_configure.config.process_config(
            self.config,
            self.build_dir,
            "build.cache",
            profiles=self.profile,
            overrides=self.overrides,
        )
        devpipeline_core.sanitizer.sanitize(
            config, lambda n, m: print("{} [{}]".format(m, n))
        )


def main(args=None):
    # pylint: disable=missing-docstring
    configure = Configure()
    devpipeline_core.command.execute_command(configure, args)


_CONFIGURE_COMMAND = (main, "Configure a project bulid directory.")

if __name__ == "__main__":
    main()
