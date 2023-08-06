# Mercurial logs through the `logging` module

This extension redirects most user feedback meant for terminals to the
Python `logging` module of the standard library.

This is intended intended primarily for server-side use cases, and is unlikely
to be useful for client-side operation.

Indeed on a server, many messages are useful for the systems administrator
only, and would be unwanted pollution if seen by the client.
A notable exception is `ui.status` which is really used
to report back meaningful information over the wire.

Using logging is more robust and flexible than using flags such as
`ui.debug` and redirecting `stderr`. It also provides integration with
Sentry (see below). Many other logs aggregation systems that have a `logging`
handler could be directly used.

At the time of this writing, it has the side effect to disable other extensions
meant for logs, such as `blackbox`.

## Installation

Install with `pip` or `pip3`:

```
   pip install hgext-loggingmod
   pip3 install "hgext-loggingmod>=0.2.0"
```

Then, in your HGRC, include this:

```ini
[extensions]
loggingmod =
```

## Configuration

All parameters are to be set within the `[logging]` hgrc section.

### Basic configuration

These are applied first, using mostly
[`logging.basicConfig`](https://docs.python.org/library/logging.html?highlight=basicconfig#logging.basicConfig)

Example (these are the default values):

```ini
[logging]
level = info
format = [%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s
hg_format = [%(asctime)s] [%(process)d] repo:%(repo)s [%(levelname)s] [%(name)s] %(message)s
```

#### Logging to a file

```ini
[logging]
file = /var/log/mercurial.log
```

#### Format

The `format` string is a regular logging format string, see
[LogRecord attributes](https://docs.python.org/library/logging.html#logrecord-attributes) for a full list of the keys that can be used there.

The `hg_format` string is also a regular logging format string, but it
can additionally make use of the **`repo` parameter**: the full path to the
current repository on the file system, if relevant to the given log record.
This format is used in the `hg` logger and its descendants, such as
`hg.logging`, `hg.discovery` etc.

The times will include the timezone by default.

### Advanced configuration through files

#### JSON

This is the most complete, as it leverages [`dictConfig()`](https://docs.python.org/library/logging.config.html#logging.config.dictConfig)

```
[logging]
config.json = /etc/hg-logging.json
```

The basic configuration above is done first nevertheless, but it is wiped out
unless one uses the `incremental` keyword.

### INI

This is forwarded to [`fileConfig()`](https://docs.python.org/3/library/logging.config.html#logging.config.fileConfig)

```
[logging]
config.ini = /etc/hg-logging.ini
```

## Using with Sentry

### Prerequisites

The `sentry_sdk` package should be importable from the Mercurial process, see
[Sentry install instructions](https://docs.sentry.io/platforms/python/#integrating-the-sdk)

In our experience, `pip install sentry-sdk` has not been enough, we had to also
install [Brotli](https://pypi.org/project/Brotli/) as well. Your mileage may
vary.


In doubt, [test it first](https://docs.sentry.io/platforms/python/#verifying-your-setup)

### Activation

To forward logs to Sentry, just specify the DSN in the hgrc:

```[ini]
[logging]
sentry.dsn = https://<key>@sentry.example.net/<project>
```

Warning : don't use quotes above.

### Basic configuration

The Sentry default integration catches all logging calls, and is orthogonal
to the regular `logging` configuration, except for the logger levels.

This extension has several knobs to tweak it.
Here's an example

```ini
[logging]
sentry.ignore_loggers = discovery extension

# these are the default values:
sentry.event_level = error
sentry.breadcrumb_level = info
```

### Fine configuration

Instead of the flat configuration as above, you can disable the blanket
integration and resort to explicit configuration with the `config.json`
directive and Sentry's handlers

```ini
[logging]
config.json = /etc/hg-config-with-sentry.conf
sentry.dsn = https://<key>@sentry.example.net/<project>
sentry.default_integration = false
```

Of course, this also disables the `sentry.event_level` and
`sentry.breadcrumbs_level` config items.

At the time of this writing, these handlers are

- `sentry_sdk.integrations.logging.EventHandler`
- `sentry_sdk.integrations.logging.BreadCrumbHandler`

See also: [Handler classes](https://docs.sentry.io/platforms/python/logging/#handler-classes) in Sentry documentation
