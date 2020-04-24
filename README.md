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

Directly from the git repo

```
$ pip --user install git+https://github.com/mgaitan/move-imports
```

If you want apply `--isort` install it

```
$ pip --user install isort
```

## Running tests

Clone the repo and install pytest

```
$ pytest
```


## Command line interface

```
$ move-imports --help
usage: move-imports [-h] [--limit-to LIMIT_TO] [--rewrite] [--isort]
                    [paths [paths ...]]

positional arguments:
  paths                Path/s to refactor. Glob supported enclosed in quotes

optional arguments:
  -h, --help           show this help message and exit
  --limit-to LIMIT_TO  Stop processing after N files
  --rewrite            write the result to source's path
  --isort              apply isort
```

## Acknowledgement

Thanks to [Shiphero](https://shiphero.com) to give me the time to do this.