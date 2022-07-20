# Wait for other tasks

If your task depends on a task finishing but not the output of the task you can use the `wait_for` argument when defining your task.


```python
import daglib

dag = daglib.Dag()


@dag.task()
def task_1():
    print("Do this first")


@dag.task(wait_for=[task_1], final=True)
def task_2(*tasks):
    print("Then do this")
```


```python
dag.run()
```

    Do this first
    Then do this



```python
dag.visualize()
```




    
![png](03_wait_for_other_tasks_files/03_wait_for_other_tasks_3_0.png)
    



Make not of the `*tasks` argument to the task. This is needed because the name of the task, `task_1` will be passed to `task_2` as an argument and we need to handle this without an error. Future releases of Daglib will deal with this issue.
