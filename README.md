# Pocketwatch

Pocketwatch provides a simple stopwatch for timing any block of Python code. It
can display desktop notifications, play a chime after long runs, and optionally
collect profiling statistics.

## Installation

```bash
pip install pocketwatch
```

## Basic Usage

```python
from pocketwatch import Pocketwatch

with Pocketwatch("load data"):
    load_data()
```

The context manager logs the elapsed time when the block finishes. Notifications
and sound are disabled unless explicitly requested.

```python
with Pocketwatch(
    "big task",
    notify=True,          # show a pop-up
    notify_after=5.0,     # minimum duration for pop-up
    sound=True,           # play ding.wav
    sound_after=60.0,     # minimum duration for sound
):
    run_big_task()
```

To access the cProfile integration, call `end(return_stats=True)` at the end of
your block or use the object as a context manager and request profiling.

```python
with Pocketwatch(profile=True) as pw:
    crunch_numbers()
stats = pw.end(return_stats=True)
```

## Decorator Shortcut

A lightweight decorator mirrors the context manager. It uses the function name
as the message label and logs to the default logger.

```python
from pocketwatch.decorators import stopwatch

@stopwatch
def do_work():
    ...
```

Custom options may be supplied when decorating:

```python
@stopwatch(sound=True, notify=False)
def background_job():
    ...
```

## Features

- Drop-in context manager for timing code blocks
- Optional desktop notifications via [notifypy](https://pypi.org/project/notifypy/)
- Optional sound playback with bundled audio files
- Incremental mode to suppress output for short runs
- cProfile support with stats returned on request
- Works with Python 3.9+
- Licensed under the MIT license

