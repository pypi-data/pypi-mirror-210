# -*- coding: utf-8
# Copyright 2019-2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
"""An extension to route all Mercurial UI output to the logging module."""
import json
import logging
import logging.config
import sys
import traceback
from mercurial import (
    encoding,
    exthelper,
    pycompat,
)
from . import (
    sentry,
)
from .config import (
    CONFIG_SECTION,
    DEFAULT_GENERAL_FORMAT,
    DEFAULT_HG_FORMAT,
    loglevel,
)
from . import version

__version__ = pycompat.sysbytes(version.version)
testedwith = b'5.4'
minimumhgversion = b'5.2'

hg_logger = logging.getLogger('hg')
# Formats used in hg_logger usually make use of the
# extra 'repo' parameter, that events emitted through other loggers
# don't have. We'll pair hg_logger with a specific handler, and block
# propagation.
hg_logger.propagate = False

eh = exthelper.exthelper()
uisetup = eh.finaluisetup


def strmsg(*parts):
    """Convert bytes message parts to str suitable for logging.

    The methods of `ui` class all expect a variable list of arguments, each
    one being a bytes string.

    Note that logging can actually log bytes, calling `str()` on them, so that
    `logging.error(b'foo')` actually gives `ERROR:root:b'foo'`.
    This is quite suitable for a fallback. We're doing exactly that
    explicitely, calling `str()` in order to keep the typing promise.
    It's not pretty but we want primarily:

    1. the logs to be emitted in all cases
    2. the information to be usable by human beings trying to understand a bug

    So, something like `b"can't find topic 'pr\xe9parations'"`
    (that's latin-1 for préparations) is acceptable
    """
    msg = b''.join(parts).rstrip(b'\n')
    try:
        return msg.decode(pycompat.sysstr(encoding.encoding))
    except UnicodeDecodeError:
        return str(msg)


def cookextra(ui):
    # hgweb sets 'ui.forcecwd' on repo.ui to repo.root
    # ui.confisource() returns empty string if item not found
    if ui.configsource(b'ui', b'forcecwd') == b'hgweb':
        repodir = ui.config(b'ui', b'forcecwd')
    else:
        # suitable for command-line invocation (set in dispatch.py)
        repodir = ui.config(b'bundle', b'mainreporoot', default=None)

    if repodir is not None:
        try:
            repodir = pycompat.fsdecode(repodir)
        except UnicodeDecodeError:  # pragma: PY3
            # having an ugly b'' is acceptable, see `msgstr.__doc__`
            repodir = str(repodir)
    return {'repo': repodir}


def error(self, *msg, **opts):
    hg_logger.error(strmsg(*msg), extra=cookextra(self))


def warn(self, *msg, **opts):
    hg_logger.warning(strmsg(*msg), extra=cookextra(self))


def debug(self, *msg, **opts):
    hg_logger.debug(strmsg(*msg), extra=cookextra(self))


def note(self, *msg, **opts):
    hg_logger.info(strmsg(*msg), extra=cookextra(self))


def log(self, event, msgfmt, *msgargs, **opts):
    event = pycompat.sysstr(event)
    logger = logging.getLogger('hg.' + event)
    level = logging.DEBUG if event == 'extension' else logging.INFO
    logger.log(level, strmsg(msgfmt.rstrip(b'\n') % msgargs),
               extra=cookextra(self))


def format_exc_only(exc, value):
    """Rewrapping of traceback.format_exception_only, avoiding newlines.

    According to https://docs.python.org/3/library/traceback.html,
    several lines can occur in case of SyntaxError.
    """
    lines = traceback.format_exception_only(exc, value)
    main_msg = lines[-1].strip()
    if len(lines) > 1:
        return '%s: %r' % (main_msg, lines)
    return main_msg


def log_traceback(self, exc=None, force=False):
    """print exception traceback if traceback printing enabled or forced.
     only to call in exception handler.

    Adapted from mercurial.ui.ui.traceback at version 5.9.2.

    Besides from diverting through the `logging` standard facility,
    we take care of avoiding inner newlines, using reprs liberally.
    This is not pretty, but it is more exploitable than multiple lines
    entangled with unrelated logs on busy servers (basic logging good
    practices).

    :returns: boolean telling if traceback was emitted.
    """
    if self.tracebackflag or force:
        if exc is None:
            exc = sys.exc_info()
        cause = getattr(exc[1], 'cause', None)
        extra = cookextra(self)

        exc_tb = traceback.format_tb(exc[2])
        if cause is not None:
            cause_tb = traceback.format_tb(cause[2])
            cause_msg = format_exc_only(cause[0], cause[1])

            # exclude frame where 'exc' was chained and rethrown from exc_tb
            exc_tb = exc_tb[:-1]
            hg_logger.error("%s Inner cause traceback "
                            "(most recent call last): %r "
                            "Catch and reraise traceback (same): %r",
                            cause_msg, cause_tb, exc_tb,
                            extra=extra)
        else:
            exc_msg = format_exc_only(exc[0], exc[1])
            hg_logger.error("%s Traceback (most recent call last): %r",
                            exc_msg, exc_tb,
                            extra=extra)
    return self.tracebackflag or force


_missing = object()


class MissingRepoFilter(logging.Filter):
    """A Filter to add repo=None to records that don't have repos.

    With formats using the 'repo' extra parameter, it leads to an error
    if that parameter is not explicitely passed while logging.

    This is cumbersome for direct callers of `hg_logger` that don't have
    repository information.
    """

    def filter(self, record):
        if getattr(record, 'repo', _missing) is _missing:
            record.repo = None
        return True


@eh.uisetup
def _uisetup(ui):
    logger = logging.getLogger(__name__)
    level = ui.configwith(loglevel, CONFIG_SECTION, b'level', default=b'INFO')
    # here maybe we could try strfromlocal, but that can raise.
    fmt = pycompat.sysstr(
        ui.config(CONFIG_SECTION, b'format', default=DEFAULT_GENERAL_FORMAT))

    general_fmt = fmt.replace('%(repo)s', '')
    datefmt = "%Y-%m-%d %H:%M:%S %z"

    conf = dict(level=level,
                format=general_fmt,
                datefmt=datefmt)
    fpath = ui.config(CONFIG_SECTION, b'file', default=None)
    if fpath is not None:
        conf['filename'] = pycompat.fsdecode(fpath)
    logging.basicConfig(**conf)

    if general_fmt != fmt:
        logger.warning("Had to replace format %r by %r for non-Mercurial "
                       "logging because the 'repo' key can't be used outside "
                       "of the Mercurial context. "
                       "You may want to make separate configurations using "
                       "The 'format' and 'hg_format' settings.",
                       fmt, general_fmt)
    if fpath is None:
        hg_handler = logging.StreamHandler()
    else:
        hg_handler = logging.FileHandler(fpath)
    hg_handler.setFormatter(
        logging.Formatter(
                fmt=pycompat.sysstr(
                    ui.config(CONFIG_SECTION, b'hg_format',
                              default=DEFAULT_HG_FORMAT)),
                datefmt=datefmt)
    )
    hg_handler.addFilter(MissingRepoFilter())
    hg_logger.addHandler(hg_handler)

    jsonconf = ui.config(CONFIG_SECTION, b'config.json', default=None)
    logger.info("jsonconf=%r", jsonconf)
    if jsonconf:
        with open(jsonconf) as conffile:
            conf_dict = json.load(conffile)
        logging.config.dictConfig(conf_dict)

    iniconf = ui.config(CONFIG_SECTION, b'config.ini', default=None)
    if iniconf is not None:
        logging.config.fileConfig(iniconf)

    if ui.config(CONFIG_SECTION, b'sentry.dsn', default=False):
        sentry.setup(ui)

    cls = ui.__class__
    cls.error = error
    cls.warn = warn
    cls.debug = debug
    cls.note = note
    cls.log = log
    cls.traceback = log_traceback
    ui.log(b"logging",
           b"Diverted all output to the standard Python logging module")
