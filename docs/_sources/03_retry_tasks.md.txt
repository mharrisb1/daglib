# Retry Tasks

To retry tasks, you should use [Tenacity](https://tenacity.readthedocs.io/en/latest/). Make sure that the Tenacity retry decorator is below the Daglib task decorator for the task to be registered correctly.


```python
import random

import daglib
import tenacity

dag = daglib.Dag()


@dag.task(final=True)
@tenacity.retry()  # retry forever
def unreliable_task():
    if random.randint(1, 10) > 1:
        print("Retrying task")
        raise IOError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"
```


```python
dag.run()
```

    Retrying task
    Retrying task
    Retrying task
    Retrying task
    Retrying task





    'Awesome sauce!'



Please see the [Tenacity](https://tenacity.readthedocs.io/en/latest/) documentation on usage.


```python
import random

import daglib
from tenacity import retry, stop_after_attempt, wait_fixed

dag = daglib.Dag()


@dag.task(final=True)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))  # retry 3 times waiting 1 second between tries
def unreliable_task():
    if random.randint(2, 10) > 1:
        print("Retrying task")
        raise IOError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"
```


```python
try:
    dag.run()
except tenacity.RetryError:
    print("Never succeeded :(")
```

    Retrying task
    Retrying task
    Retrying task
    Never succeeded :(

