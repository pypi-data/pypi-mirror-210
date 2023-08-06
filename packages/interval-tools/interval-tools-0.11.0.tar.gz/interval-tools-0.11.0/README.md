# Python Tools for Applications of Interval Design

## Requirements

Python 3.11+

## Installation

```sh
pip install interval-tools
```

Or if you want to use [ObjectID](https://www.mongodb.com/docs/manual/reference/bson-types/#objectid) as a unique identifier in Domain-Driven Design, run

```sh
pip install "interval-tools[objectid]"
```

## Quickstart

```pycon
>>> from interval.utils import get_stream_logger
>>> import logging
>>> formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
>>> logger = get_stream_logger('interval', 'INFO', formatter=formatter)
>>> logger.info('Readability counts.')
INFO:interval:Readability counts.
```
