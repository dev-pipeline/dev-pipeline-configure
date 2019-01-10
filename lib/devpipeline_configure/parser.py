#!/usr/bin/python3

"""Manage reading and writing configurations to disk."""

import configparser


def _make_parser():
    return configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())


def read_config(path):
    """
    Read a configuration from disk.

    Arguments
    path -- the loation to deserialize
    """
    parser = _make_parser()
    if parser.read(path):
        return parser
    raise Exception("Failed to read {}".format(path))
