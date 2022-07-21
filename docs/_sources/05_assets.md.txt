# Assets

For retrieving data assets in a repeatable way, you can use define an `asset`. Technically, assets are just minimalistic tasks that accept no inputs. The real benefit to having this subset of tasks as their own object is for project organization.

An example of using this in the wild could be to have a project layout like:

```
workflows/
    |
    |__ workflow1.py
    |__ workflow2.py
assets/
    |
    |__ postgres.py
    |__ snowflake.py
```


```python
from daglib import asset, Dag


@asset
def table():
    return [
        (1, 2, 3, 4, 5),  # row 1
        (6, 7, 8, 9, 10),  # row 2
        (11, 12, 13, 14, 15),  # row 3
        (16, 17, 18, 19, 20),  # row 4
        (21, 22, 23, 24, 25),  # row 5
        (26, 27, 28, 29, 30),  # row 6
    ]


table()
```




    [(1, 2, 3, 4, 5),
     (6, 7, 8, 9, 10),
     (11, 12, 13, 14, 15),
     (16, 17, 18, 19, 20),
     (21, 22, 23, 24, 25),
     (26, 27, 28, 29, 30)]




```python
dag1 = Dag(name="dag1")
dag1.add_asset(table)


@dag1.task(final=True)
def count_rows(table):
    return len(table)
```


```python
dag1.run()
```




    6




```python
dag1.visualize()
```




    
![png](05_assets_files/05_assets_4_0.png)
    




```python
dag2 = Dag(name="dag2")
dag2.add_asset(table)


@dag2.task(final=True)
def count_cols(table):
    return len(table[0])
```


```python
dag2.run()
```




    5




```python
dag2.visualize()
```




    
![png](05_assets_files/05_assets_7_0.png)
    




```python
dag3 = Dag(name="dag3")
dag3.add_asset(table)


@dag3.task(final=True)
def get_table_shape(table):
    return len(table), len(table[0])
```


```python
dag3.run()
```




    (6, 5)




```python
dag3.visualize()
```




    
![png](05_assets_files/05_assets_10_0.png)
    


