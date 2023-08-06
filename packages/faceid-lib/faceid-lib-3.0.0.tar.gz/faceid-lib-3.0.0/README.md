# picaso-engine ML faceid workflow

## Overview

This is a helper library for picaso-engine ML faceid workflow product. The idea of this library is to wrap all reusable code to simplify and improve workflow implementation.

Supported functionality:

- API to communicate with RabbitMQ for event receiver/producer
- Workflow call helper
- Logger call helper
- Rate-limiting strategies
- Computing vector similarity helper (ex. Face Similarity Search)

## Author
picaso-engine ML (https://pypi.org/project/faceid-lib/), Dani Gunawan

## Instructions
Version number should be updated in __init__.py and pyproject.toml

1. Install Poetry

```
pip install poetry
```

2. Add pika and requests libraries

```
poetry add pika
poetry add requests
```

3. Build

```
poetry lock --no-update
poetry install
poetry build
```

4. Publish to TestPyPI

```
poetry publish -r testpypi
```

5. Install from TestPyPI

```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple  faceid-lib
```

6. Publish to PyPI

```
poetry publish
```

7. Install from PyPI

```
pip install faceid-lib
```

8. Test imported library from CMD

```
python -m faceid_lib
```

9. Import EventReceiver

```
from faceid_lib.events.event_receiver import EventReceiver
```

10. Import EventProducer

```
from faceid_lib.events.event_producer import EventProducer
```

11. Import FastAPILimiter, RateLimiter

```
from faceid_lib.ratelimiter import FastAPILimiter
from faceid_lib.ratelimiter.depends import RateLimiter
```

## Structure

```
.
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── faceid_lib
│   ├── __init__.py
│   ├── __main__.py
│   ├── events
│       ├── __init__.py
│       ├── event_producer.py
│       └── event_receiver.py
│   ├── ratelimiter
│       ├── __init__.py
│       └── depends.py
│   ├── logger
│       ├── __init__.py
│       └── logger_helper.py
│   ├── workflow
│       ├── __init__.py
│       └── workflow_helper.py
│   ├── vector_similarity
│       ├── __init__.py
│       ├── v1
│           ├── __init__.py
│           └── power.py
└── README.md
```

## Changelogs 2.0.0 - 2.0.1 (2023-05-02)
- compute similarity helper

## Changelogs 1.0.9 (2022-06-14)
- modify response & handler

## Changelogs 1.0.5 (2021-10-24)
- downgrade pika version to 1.1.0

## Changelogs 1.0.4 (2021-10-24)
- enhancment rate limiting

## License
Licensed under the Apache License, Version 2.0. Copyright 2020-2021 picaso-engine ML, Dani Gunawan.
