# Getting Started

You can register any arbitrary Python function as a task by using the task decorator.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task():
    return 1
```

To return values, you must mark one or more tasks as `final`. This tells the orchestration engine what to return.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task():
    return 1


# will return empty tuple
dag.run()
```




    ()




```python
import daglib

dag = daglib.Dag()


@dag.task(final=True)
def task():
    return 1


dag.run()
```




    1



You can specify multiple return values by marking more than one task as final. The result from the DAG run will be e tuple of all results.


```python
import daglib

dag = daglib.Dag()


@dag.task(final=True)
def task_1():
    return 6


@dag.task(final=True)
def task_2():
    return 3


dag.run()
```




    (6, 3)



You can pass the output of one task to another as adding the name of the task as a argument in the descendant task.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1():
    return 6


@dag.task(final=True)
def task_2(task_1):
    return task_1 * 3


dag.run()
```




    18



A task can take the outputs of multiple tasks as inputs


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    return 6


@dag.task()
def task_1b():
    return 3


@dag.task(final=True)
def task_2(task_1a, task_1b):
    return task_1a * task_1b


dag.run()
```




    18



To visualize the task graph being computed, you can call `visualize()` on the DAG object.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    return 6


@dag.task()
def task_1b():
    return 3


@dag.task(final=True)
def task_2(task_1a, task_1b):
    return task_1a * task_1b


dag.visualize()
```





![png](00_getting_started_files/00_getting_started_12_0.png)
