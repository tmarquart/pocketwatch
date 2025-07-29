# Pocketwatch

Pocketwatch is a small stopwatch utility for Python code blocks.

```python
from pocketwatch import Pocketwatch

with Pocketwatch("load data"):
    ...
```

## Bonus: Quick Stopwatch Decorator

A lightweight decorator is available for convenience:

```python
from pocketwatch.decorators import stopwatch

@stopwatch
def do_work():
    ...
```

This uses the function name as the label and logs the time. Pop-up is enabled by default.
