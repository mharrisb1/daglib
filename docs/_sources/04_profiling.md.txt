# Profiling

To collect metrics on task runs you can set the `profile` flag in the Dag object constructor to true.


```python
import time

import daglib

dag = daglib.Dag(name="example", description="This is an example DAG", profile=True)


@dag.task()
def task_1():
    """Do some stuff"""
    time.sleep(1)
    return [1, 2, 3]


@dag.task(final=True)
def task_2(task_1):
    """Do some other stuff"""
    return list(map(lambda x: x * 2, task_1))
```


```python
dag.run()
```




    [2, 4, 6]



Records containing profiling data for the tasks executed in the DAG run will be written as AVRO records. The files are saved under a file path matching the following pattern:

```
meta/profiling/{Dag.name}/{Dag.run_id}.avro
```


```python
from pathlib import Path

list(Path("meta/profiling/").rglob("*.avro"))
```




    [PosixPath('meta/profiling/example/run_5d508d060.avro')]



## Query Profiling Data

To access profiling records, you can query the `MetaDB`. Profiling records are available under the `profiling` table.


```python
from pathlib import Path

from daglib.metadata import MetaDB

db = MetaDB()
```


```python
db.query("""
SELECT *
FROM profiling
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>dag_name</th>
      <th>dag_description</th>
      <th>run_id</th>
      <th>task_name</th>
      <th>task_description</th>
      <th>task_runtime</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>example</td>
      <td>This is an example DAG</td>
      <td>run_5d508d060</td>
      <td>task_1</td>
      <td>Do some stuff</td>
      <td>1.005017</td>
    </tr>
    <tr>
      <th>1</th>
      <td>example</td>
      <td>This is an example DAG</td>
      <td>run_5d508d060</td>
      <td>task_2</td>
      <td>Do some other stuff</td>
      <td>0.000002</td>
    </tr>
  </tbody>
</table>
</div>



### Drop all data from Metadata DB


```python
db.drop()  # drops all files and directories in the metadata directory

list(Path("meta/profiling/").rglob("*.avro"))

db.query("""
SELECT *
FROM profiling
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>dag_name</th>
      <th>dag_description</th>
      <th>run_id</th>
      <th>task_name</th>
      <th>task_description</th>
      <th>task_runtime</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



### Conducting Analytics on Profiling Data

Records for all runs where profiling is enabled will be saved to the metadata directory. All records are loaded to the `profiling` table.


```python
import time
import random

import daglib

for _ in range(5):  # create and run the DAG 5 times
    dag = daglib.Dag(name="example2", description="This is another example DAG", profile=True)


    @dag.task()
    def task_1():
        """Do some stuff"""
        time.sleep(random.randint(1, 3))
        return [1, 2, 3]


    @dag.task(final=True)
    def task_2(task_1):
        """Do some other stuff"""
        return list(map(lambda x: x * random.randint(1, 10), task_1))


    print(dag.run())
```

    [4, 8, 9]
    [9, 4, 15]
    [3, 6, 3]
    [7, 20, 24]
    [5, 16, 21]



```python
db = daglib.metadata.MetaDB()

db.query("""
SELECT AVG(task_runtime) AS avg_task_runtime
FROM profiling
""")
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>avg_task_runtime</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1.002517</td>
    </tr>
  </tbody>
</table>
</div>




```python
db.drop()
```


```python

```
