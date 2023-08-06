# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging
from mercurial import pycompat

CONFIG_SECTION = b'logging'

# default formats have same type as if it were obtained from `ui.config()`
DEFAULT_GENERAL_FORMAT = (
    "[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s"
)
DEFAULT_HG_FORMAT = (
    b"[%(asctime)s] [%(process)d] [%(levelname)s] "
    b"repo:%(repo)s "
    b"[%(name)s] %(message)s"
)


def loglevel(levelname):
    """A converter from string representation.

    This is meant to be usable with `ui.configwith`.
    """
    return getattr(logging, pycompat.sysstr(levelname).strip().upper())
