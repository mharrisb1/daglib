# Additional Task Dependencies

We've seen the standard way of defining task dependencies by passing the task name (function name) as an argument in the task that depends on it. This enables optional I/O between the tasks.

You can specify additional dependencies to the task using the `depende_on` argument. When you use this feature, you must add the ability for the function to take a variable number of non-keyword arguments (e.g. `*args` or an equivalent).


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    print("Running task_1a")


@dag.task()
def task_1b():
    print("Running task_1b")


@dag.task(depends_on=[task_1a, task_1b], final=True)
def task_2(*tasks):
    print("Running task_2")
```


```python
dag.run()
```

    Running task_1aRunning task_1b
    
    Running task_2



```python
dag.visualize()
```




    
![png](06_additional_task_dependencies_files/06_additional_task_dependencies_3_0.png)
    



You can also access the output values of a task added to `depends_on`.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1a():
    return 1


@dag.task()
def task_1b():
    return 2


@dag.task(depends_on=[task_1a, task_1b], final=True)
def task_2(*tasks):
    return sum(tasks)
```


```python
dag.run()
```




    3




```python
dag.visualize()
```




    
![png](06_additional_task_dependencies_files/06_additional_task_dependencies_7_0.png)
    




```python

```
