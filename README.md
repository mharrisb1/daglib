# ⚗️ Daglib - Lightweight DAG composition framework

[![PyPI version](https://badge.fury.io/py/daglib.svg)](https://badge.fury.io/py/daglib)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/daglib)](https://pypi.org/project/daglib/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/daglib.svg)](https://pypi.org/project/daglib/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy.readthedocs.io/en/stable/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Daglib is a lightweight alternative to Airflow and other orchestration engines. It is meant to run on a single machine and comes with many great features out of the box like task I/O, dynamic task generation, and simple testing and deployment.

It can run as a standalone application or be embedded in another application to enable more complex use cases like event-driven workflows, conditional workflows, and more.

See documentation at https://mharrisb1.github.io/daglib/

# Installation

```shell
pip install daglib
```

# Create your first DAG


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    return "Hello"


@dag.task()
def task_1b():
    return "world!"


@dag.task(final=True)
def tassk_2(task_1a, task_1b):
    print(f"{task_1a}, {task_1b}")


dag.run()
```

    Hello, world!


# Beyond the "Hello, world!" example

For a more involved example, we will create a small ETL pipeline that takes data from four source tables and creates a single reporting table. The data is driver-level information from the current 2022 Formula 1 season. The output will be a pivot table for team-level metrics.

## Source Tables

1. Team - Which team the driver belongs to for the season
2. Points - Current total Driver's World Championship points for each driver for the season
3. Wins - Current number of wins for each driver for the season
4. Podiums - Current number of times the driver finished in the top 3 for the season


```python
import pandas as pd
import daglib

# Ignore. Used to render the DataFrame correctly in the README
pd.set_option("display.notebook_repr_html", False)

dag = daglib.Dag()


@dag.task()
def team():
    return pd.DataFrame(dict(
        driver=["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        team=["Red Bull", "Ferrari", "Mercedes", "Red Bull", "Ferrari", "Mercedes"],
    )).set_index("driver")


@dag.task()
def points():
    return pd.DataFrame(dict(
        driver=["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        points=[175, 126, 77, 129, 102, 111]
    )).set_index("driver")


@dag.task()
def wins():
    return pd.DataFrame(dict(
        driver=["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        wins=[6, 2, 0, 1, 0, 0]
    )).set_index("driver")


@dag.task()
def podiums():
    return pd.DataFrame(dict(
        driver=["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        podiums=[7, 4, 2, 5, 5, 3]
    )).set_index("driver")


@dag.task()
def driver_metrics(team, points, wins, podiums):
    return team.join(points).join(wins).join(podiums)


@dag.task(final=True)
def team_metrics(driver_metrics):
    return driver_metrics.groupby("team").sum().sort_values("points", ascending=False)


dag.run()
```




              points  wins  podiums
    team
    Red Bull     304     7       12
    Ferrari      228     2        9
    Mercedes     188     0        5



## Task Graph Visualization

The DAG we created above will create a task graph that looks like the following

![task graph](https://storage.googleapis.com/daglib-image-assets/example-dag.png)
