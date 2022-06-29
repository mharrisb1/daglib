<center><h1> ⚗️ daglib - Lightweight DAG composition framework </h1></center>

[![python version](https://img.shields.io/static/v1?label=python&message=3.10&color=blue)](https://www.python.org/downloads/release/python-3100/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

# Installation

```shell
pip install daglib
```

# Quickstart


```python
from daglib import Dag

dag = Dag()


@dag.task()
def step_1a():
    return "Hello"


@dag.task()
def step_1b():
    return "daglib!"


@dag.task(final=True)
def step_2(step_1a, step_1b):
    return f"{step_1a}, {step_1b}"


dag.run()
```




    'Hello, daglib!'
