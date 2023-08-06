# simple-wait
Simple wait

[![tests](https://github.com/gil9red/simple-wait/actions/workflows/run-tests.yml/badge.svg)](https://github.com/gil9red/simple-wait/actions/workflows/run-tests.yml)
[![upload to pypi](https://github.com/gil9red/simple-wait/actions/workflows/python-publish.yml/badge.svg)](https://github.com/gil9red/simple-wait/actions/workflows/python-publish.yml)
[![pypi](https://img.shields.io/pypi/v/simple-wait.svg)](https://pypi.org/project/simple-wait/)
[![pypi python versions](https://img.shields.io/pypi/pyversions/simple-wait.svg)](https://pypi.org/project/simple-wait/)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://pypi.org/project/black/)
[![License](https://img.shields.io/badge/license-MIT-black.svg)](https://opensource.org/licenses/MIT)

## Example
```python
from datetime import datetime
from simple_wait import wait


print("Start wait")
wait(seconds=5)
print("Finish wait")

while True:
    print()
    print("Current datetime:", datetime.now())
    print()
    wait(minutes=1, seconds=30)
```

```python
import traceback
from simple_wait import wait


while True:
    try:
        # Process
        ...
        
        wait(hours=8)

    except:
        print(traceback.format_exc())
        wait(minutes=15)
```

## Installation
You can install with:
```
pip install simple-wait
```

Install or upgrade:
```
pip install --upgrade simple-wait
```

Install or update from github:
```
pip install git+https://github.com/gil9red/simple-wait
```

## Description

Parameters `wait` function:

| Name                   | Type                 | Default                                        |
|------------------------|----------------------|------------------------------------------------|
| days                   | `int`                | `0`                                            |
| seconds                | `int`                | `0`                                            |
| microseconds           | `int`                | `0`                                            |
| milliseconds           | `int`                | `0`                                            |
| minutes                | `int`                | `0`                                            |
| hours                  | `int`                | `0`                                            |
| weeks                  | `int`                | `0`                                            |
| progress_bar           | `Iterable[str]`      | `("&#124;", "/", "-", "\\")`                   |
| delay_seconds          | `float`              | `1`                                            |
| log_pattern_progress   | `str`                | `"[{progress_bar}] Time left to wait: {left}"` |
| log_pattern_cancel     | `str`                | `"\nWaiting canceled\n"`                       |
| log_pattern_clear_line | `str`                | `"\r" + " " * 100 + "\r"`                      |
| log                    | `TextIOWrapper`      | `sys.stdout`                                   |
| is_need_stop           | `Callable[[], bool]` | `lambda: False`                                |
