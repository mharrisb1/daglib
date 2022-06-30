# ⚗️ daglib - Lightweight DAG composition framework

[![python version](https://img.shields.io/static/v1?label=python&message=3.10&color=blue)](https://www.python.org/downloads/release/python-3100/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy.readthedocs.io/en/stable/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

daglib is a lightweight alternative to Airflow and other orchestration engines. It is meant to run on a single machine and comes with many great features out of the box like task I/O, dynamic task generation, and simple testing and deployment.

It can run as a standalone application or be embedded in another application to enable more complex use cases like event-driven workflows, conditional workflows, and more.

See documentation at https://mharrisb1.github.io/daglib/

# Installation

```shell
pip install daglib
```

# Quickstart

For this example we will create a small ETL pipeline that takes data from four source tables and creates a single reporting table. The example calculate team metrics so far in the 2022 F1 season.

## Source Tables

1. Team - Which team the driver belongs too for the season
2. Points - Current total Driver's World Championship points for each driver for the season
3. Wins - Current number of wins for each driver for the season
4. Podiums - Current number of times the driver finished in the top 3 for the season


```python
import pandas as pd
import daglib

pd.set_option("display.notebook_repr_html", False)

dag = daglib.Dag()


@dag.task()
def team():
    return pd.DataFrame({
        "driver": ["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        "team": ["Red Bull", "Ferrari", "Mercedes", "Red Bull", "Ferrari", "Mercedes"],
    }).set_index("driver")


@dag.task()
def points():
    return pd.DataFrame({
        "driver": ["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        "points": [175, 126, 77, 129, 102, 111]
    }).set_index("driver")


@dag.task()
def wins():
    return pd.DataFrame({
        "driver": ["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        "wins": [6, 2, 0, 1, 0, 0]
    }).set_index("driver")


@dag.task()
def podiums():
    return pd.DataFrame({
        "driver": ["Max", "Charles", "Lewis", "Sergio", "Carlos", "George"],
        "podiums": [7, 4, 2, 5, 5, 3]
    }).set_index("driver")


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

![task graph](https://00f74ba44b9cef42bdc6b9550fa999f19192579012-apidata.googleusercontent.com/download/storage/v1/b/daglib-image-assets/o/example-dag.png?jk=AFshE3Xtl-77nV3svojx6QWO5QbuPyYxXn6IrQSuEoRdQ0wBd0L6uTj5OQ-DTGjHGcb_gXBbJLqwUIVlEVLuB8zVJxRqgLVLA7_A8qA7-OTbQaoFMI4zv4y-tCmUKzGiy8ypB5DWjjKAbCEy_zpIz2IaE16v53cMB0jeWgws6IC0nUijhGmHOGH2qipWrsYgvek8ie_Xv02gy3GqpUpSlT05ynGbVbsuCZhUYChJyGrm0iosnWxBFn4PaewitOgcGRbioBf9knJ5uIokYQNYYLfwbnDQosuqjm4NWki4oZp4zI3Z9I2hMh2gSL-6RxSQ5bb69fX6tb-WaAi9cqV_Fm7kDJ0uWlGUmKOZUYxgwFXXQlgqVNp-mvKIrpNJuGEQsxUwUBCshwNySV_fMPMYHtsF9vIWbCO1Ji6HfUT-MbIfXmPS7gTVyaz2NT7519csHmS8FE22mzS2MMVC8P9vByEpflKh0y0KBHINE5lyBzSolyrh-G9O0g2ui6dsR-R1MNAjSsxfMqdPNhoQdQeLYMaDyi1h0BfExpRoVcr9bni2eStgeZEXQE_HLhX86YMRW6PuWGBCd3YQVsh3yQfgQQWsBjnYhSgPjDksntEjSH2ZID4Vl01PEfs93HvJgvq8iPhKU3WfXh2SfgPm-1e8xzFVLHZmwti5Vr24QXUSlQy_ZgxOSI1d1IYQi0sZHRwwaDiQefcKYBplLqqWIoyyaC7J-W3_HjyScnjkDDdnzG2u_s1GSLPZIqJYpz4rgVkX3NqQwA5CalhX-3JyMFUQjZ8KazY8DxKCn_J6XlelHsDBWgK9vT0e8tVa5xEV7ngv8xZMrGgebKELVpTifFVMs583TQa5uCDWd8nggskQVdVeP5Ut716ksvUGb-C_Lud8pdO4WMHmKE1gLPOlDGscCCEdwO4DJjOGNjQ3JhZJAFFpsu0CRUc_NiXFn3GPlIbD06C6zTxrohdkpM6woOJt6Z68DRDPBlClNx0pIbcuo7W_hf14g35L&isca=1)
