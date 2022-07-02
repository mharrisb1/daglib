# Testing

One of the great things about daglib is how simple it is to create unit tests. No mocking, no fixtures, etc. required. Since the tasks are defined as normal Python functions, they can be tested normally too.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1():
    return [1, 2, 3, 4, 5]


@dag.task(final=True)
def task_2(task_1):
    return [n * 2 for n in task_1]
```


```python
def test_task_2():
    assert task_2([1, 2, 3]) == [2, 4, 6]

test_task_2()
```
