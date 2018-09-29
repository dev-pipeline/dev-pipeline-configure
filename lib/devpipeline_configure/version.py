#!/usr/bin/python3

MAJOR = 0
MINOR = 3
PATCH = 0

ID = (MAJOR << 24) | (MINOR << 16) | (PATCH << 8)

STRING = "{}.{}.{}".format(MAJOR, MINOR, PATCH)