# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""Sentry support."""
import logging
from mercurial import (
    demandimport,
    pycompat,
)
import sentry_sdk  # won't break if not install, thanks to demandimport


from .config import (
    CONFIG_SECTION,
    loglevel,
)


logger = logging.getLogger(__name__)


def setup(ui):
    # Sentry has lots of conditional imports.
    # We could list them, but
    # 1) Our current use-cases for Sentry are well-managed long running
    #    processes, for which demandimport is less useful
    # 2) it would be brittle, prone to break upon sentry_sdk changes
    demandimport.disable()
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.logging import ignore_logger
    for logger_name in ui.configlist(
            CONFIG_SECTION, b'sentry.ignore_loggers', default=()):
        ignore_logger(pycompat.sysstr(logger_name))

    if not ui.configbool(CONFIG_SECTION, b'sentry.default_integration',
                         default=True):
        integrations = False
    else:
        integrations = [
            LoggingIntegration(
                level=ui.configwith(loglevel, CONFIG_SECTION,
                                    b'sentry.breadcrumb_level',
                                    default='INFO'),
                event_level=ui.configwith(loglevel, CONFIG_SECTION,
                                          b'sentry.event_level',
                                          default='ERROR'),
            )]

    sentry_sdk.init(
        dsn=pycompat.sysstr(ui.config(CONFIG_SECTION, b'sentry.dsn')),
        integrations=integrations,
    )

    logger.info("Setup done")
