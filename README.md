# move-imports

A script to move imports to the top of the module. Suppose a module with inline import like this

```python
import requests
from math import sin
import datetime as dt

BASE_SCENARIO = """
    ##########
    # Accounts

"""

def foo():
    from math import (
        sin, cos as cos_
    )
    return sin(1), cos_(0)


def bar():
    from math import tan
    return tan(1)
```

Executing

```
$ move-imports path/to_refactor.py --isort --rewrite
```

will produce

```python
import datetime as dt
from math import cos as cos_, sin, tan

import requests

BASE_SCENARIO = """
    ##########
    # Accounts

"""

def foo():
    return sin(1), cos_(0)


def bar():
    return tan(1)
```

## Install

```
$ pip --user install move-imports
```

or the development version, directly from the git repo

```
$ pip --user install git+https://github.com/mgaitan/move-imports
```

If you want apply `--isort` for postprocessing, install it

```
$ pip --user install isort
```

## Skip cases

To keep an inline import you could add a comment in the same line or above
the stament with "avoid circular import" or "noqa".

```python

  def foo():
    # avoid circular import
    import baz
```

```python

  def foo():
    import baz  # noqa
```


## Incremental refactoring

Sometimes inline imports statements are there for a reason. Circular imports, optional dependendencies, etc.

To manage this, it's useful to go step by step, checking a changed module
is ok before to move to the next one.

With a combination of `--start-from-last` and `--limit-to LIMIT_TO`
arguments you could incrementally refactor a whole package.

For instance, calling repeteadly the following command

```
$ move-imports --isort --rewrite --start-from-last --limit-to=1 tests/billing/**/*.py
```

will recursively traverse `tests/billing/` refactoring one module at a time. Thus, the worflow would be:

- run,
- test,
- optionally revert and skip problematic imports or modify manually
- repeat


## Running tests

Clone the repo and install pytest

```
$ pytest
```


## Command line interface

```
$ move-imports --help
usage: move-imports [-h] [--start-from-last] [--limit-to LIMIT_TO] [--debug]
                    [--rewrite] [--isort]
                    [paths [paths ...]]

positional arguments:
  paths                Path/s to refactor. Glob supported enclosed in quotes

optional arguments:
  -h, --help           show this help message and exit
  --start-from-last    Incremental refactor
  --limit-to LIMIT_TO  Stop processing after N files. Use with --start-from-
                       last
  --debug              Make verbose output
  --rewrite            write the result to source's path
  --isort              apply isort
```

## Acknowledgement

Thanks to [Shiphero](https://shiphero.com) for give me the time to do this.