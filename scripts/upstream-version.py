#!/usr/bin/env python3
"""
get latest upstream version from PyPI

This script can be used by apkg to check for latest upstream version
using upstream.version_script config option.
"""
from apkg.util.upstreamversion import version_from_pypi

# apkg expects last stdout line to contain the upstream version string
print(version_from_pypi('apkg'))
