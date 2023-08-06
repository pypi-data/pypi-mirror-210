[![PyPI version](https://badge.fury.io/py/plogger.svg)](https://badge.fury.io/py/plogger)
[![Build Status](https://travis-ci.org/c-pher/plogger.svg?branch=master)](https://travis-ci.org/c-pher/plogger)
[![Coverage Status](https://coveralls.io/repos/github/c-pher/plogger/badge.svg?branch=master)](https://coveralls.io/github/c-pher/plogger?branch=master)


## Plogger

Plogger - a simple high level logger wrapper to log into console/file with different level. Used built-in logger module.

## Installation
For most users, the recommended method to install is via pip:
```cmd
pip install plogger
```

## Import and usage

```python
from plogger import logger

log = logger('NAME')
log.info('Test message')
```

```python
import plogger

log = plogger.logger('NAME')
log.info('Log it as INFO')
```

## Result

```cmd
2022-10-10 18:17:46 | INFO      | NAME                 26 | <module> | Log it as INFO
```

## Usage

- As standalone logger function:

```python
import plogger

logger = plogger.logger('NAME', level=10)

logger.info('Test message')
logger.error('Test message')
logger.warning('Test message')
logger.debug('Test message')
```

```
2022-10-10 18:18:44 | INFO      | NAME                 27 | <module> | Test message
2022-10-10 18:18:44 | ERROR     | NAME                 28 | <module> | Test message
2022-10-10 18:18:44 | WARNING   | NAME                 29 | <module> | Test message
2022-10-10 18:18:44 | DEBUG     | NAME                 30 | <module> | Test message
```

## Changelog

##### 1.0.8 (26.05.2022)

- time format changed. microseconds added (2023-05-26 18:24:28.389)
- class obsolete

##### 1.0.7 (10.10.2022)

- Method/function name added into log

##### 1.0.6 (16.04.2022)

- Enable/disable logging fixed

##### 1.0.5.post0 (4.04.2022)

- minor changes in log entry format

##### 1.0.5 (4.04.2022)

- Console log will be colorized.
- use_color=True param added
- Line number added to the log

##### 1.0.4 (28.03.2022)

- added log level selection with the "level" param
- log level entry aligned

##### 1.0.3 (29.01.2022)

Fixed entries duplicating. Added handlers cleaning

##### 1.0.2 (25.01.2022)

console_output=sys.stderr by default

##### 1.0.1 (10.01.2022)

Added console_output=sys.stdout param

##### 1.0.0 (26.01.2020)

Added logger() function