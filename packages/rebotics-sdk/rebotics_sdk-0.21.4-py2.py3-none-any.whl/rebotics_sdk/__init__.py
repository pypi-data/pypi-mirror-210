# -*- coding: utf-8 -*-

"""Top-level package for rebotics_sdk."""

__author__ = """Malik Sulaimanov"""
__email__ = 'malik@retechlabs.com'
__version__ = '0.21.4'

try:
    from rebotics_sdk.cli.authenticated_provider import get_provider  # noqa: F401
except ImportError:
    pass
