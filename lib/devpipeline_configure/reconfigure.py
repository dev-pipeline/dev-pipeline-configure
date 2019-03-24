#!/usr/bin/python3
"""This modules configures the build system - build cache, etc...."""

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


class Reconfigure(devpipeline_core.command.Command):

    """This class reconfigures an existing project."""

    def __init__(self):
        super().__init__(
            prog="dev-pipeline reconfigure",
            description="Reconfigure a project, optionally with additional "
            "parameters",
        )
        self.add_argument("--profiles", help="Comma-separated list of profiles to use.")
        self.add_argument(
            "--overrides", help="Comma-separated list of overrides to use."
        )
        self.add_argument(
            "--append",
            help="Append provided profiles/overrides instead of replacing",
            action="store_true",
        )
        self.set_version(devpipeline_configure.version.STRING)

    def process(self, arguments):
        config_file = devpipeline_configure.load.find_config()
        cache_config = devpipeline_configure.parser.read_config(config_file)
        profiles = _calculate_value(
            cache_config, "dp.profile_name", arguments, "profiles"
        )
        overrides = _calculate_value(
            cache_config, "dp.overrides", arguments, "overrides"
        )

        cache = devpipeline_configure.config.process_config(
            cache_config.get("DEFAULT", "dp.build_config"),
            os.path.dirname(config_file),
            "build.cache",
            profiles=profiles or None,
            overrides=overrides or None,
        )
        devpipeline_core.sanitizer.sanitize(
            cache, lambda n, m: print("{} [{}]".format(m, n))
        )


def main(args=None):
    # pylint: disable=missing-docstring
    reconfigure = Reconfigure()
    devpipeline_core.command.execute_command(reconfigure, args)


_RECONFIGURE_COMMAND = (main, "Reconfigure a project bulid directory.")

if __name__ == "__main__":
    main()
