# daglib: Lightweight DAG composition framework

Created as a lighter alternative to Airflow, Prefect, Dagster and other fully-featured orchestration engines, daglib offers intuitive task creation, task ordering, and task execution for small-to-medium sized workflows.

It can run as a standalone application or be embedded in another application to enable more complex use cases like event-driven workflows, conditional workflows, and more.

## Features

- Lightweight (meant to be deployed on a single machine)
- Create tasks from standard Python functions
- Task I/O
- Fully embeddable in any Python application
- Dynamic task spawning
- Easy to test

## Use Cases

daglib can be used as a lightweight alternative to almost any use case that other orchestration engines are used for such as:

- ETL/ELT
- Batch workflows
- Lightweight ML pipelines

In addition to the common orchestration use cases, daglib unlocks some additional use cases given its ability to be embedded in other applications:

- Event-driven workflows (usually done by invoking a DAG with an API endpoint)
- Single container workflows using services such as Google Cloud Run Jobs

## Installation

```shell
pip install daglib
```

For visualizing the DAG to work, you must also specify to install `graphiv` as an extra dependency

```shell
pip install "daglib[graphiv]"
```

## Example


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    return "Hello"


@dag.task()
def task_1b():
    return "daglib!"


@dag.task(final=True)
def tassk_2(task_1a, task_1b):
    print(f"{task_1a}, {task_1b}")


dag.run()
```

    Hello, daglib!


# User Guide
```{toctree}
---
maxdepth: 2
---

00_getting_started
01_types_of_tasks
02_testing
03_retry_tasks
04_profiling
```
