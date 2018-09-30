#!/usr/bin/python3
"""This modules configures the build system - build cache, etc...."""

import devpipeline_core.command
import devpipeline_core.config.sanitizer
import devpipeline_configure.config
import devpipeline_configure.version


class Configure(devpipeline_core.command.Command):

    """This class manages the configuration of the project."""

    def __init__(self):
        super().__init__(prog="dev-pipeline configure",
                         description="Configure a project")
        self.add_argument("--config", help="Build configuration file",
                          default="build.config")
        self.add_argument("--profile",
                          help="Build-specific profiles to use.  If more than "
                               "one profile is required, separate their names "
                               "with commas.")
        self.add_argument("--override",
                          help="Collection of override options to use.  If you"
                               " require multiple types of overrides, separate"
                               " the names with commas.")
        self.add_argument("--build-dir",
                          help="Directory to store configuration.  If "
                               "specified, --build-dir-basename will be "
                               "ignored.")
        self.add_argument("--build-dir-basename",
                          help="Basename for build directory configuration",
                          default="build")
        self.set_version(devpipeline_configure.version.STRING)

        self.build_dir = None
        self.config = None
        self.overrides = None
        self.profile = None

    def setup(self, arguments):
        if arguments.build_dir:
            self.build_dir = arguments.build_dir
        else:
            if arguments.profile:
                self.build_dir = "{}-{}".format(
                    arguments.build_dir_basename, arguments.profile)
            else:
                self.build_dir = arguments.build_dir_basename
        self.profile = arguments.profile
        self.config = arguments.config
        if arguments.override:
            self.overrides = arguments.override
        else:
            self.overrides = ""

    def process(self):
        config = devpipeline_configure.config.process_config(
            self.config,
            self.build_dir,
            "build.cache",
            profiles=self.profile,
            overrides=self.overrides)
        devpipeline_core.config.sanitizer.sanitize(
            config, lambda n, m: print("{} [{}]".format(m, n)))


def main(args=None):
    # pylint: disable=missing-docstring
    configure = Configure()
    devpipeline_core.command.execute_command(configure, args)


_CONFIGURE_COMMAND = (main, "Configure a project bulid directory.")

if __name__ == '__main__':
    main()
