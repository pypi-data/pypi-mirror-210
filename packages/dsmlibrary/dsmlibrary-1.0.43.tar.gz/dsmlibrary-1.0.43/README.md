# DSM Library

## DataNode
0. init DataNode
```python
from dsmlibrary.datanode import DataNode 

data = DataNode(token)
```
1. upload file
```python
data.upload_file(directory_id=<directory_id>, file_path='<file_path>', description="<description(optional)>")
```

2. download file
```python
data.download_file(file_id=<file_id>, download_path="<place download file save> (default ./dsm.tmp)")
```
3. get file
```python
meta, file = data.get_file(file_id="<file_id>")
# meta -> dict
# file -> io bytes
```
```python
# example read csv pandas
 
meta, file = data.get_file(file_id="<file_id>")
df = pd.read_csv(file)
...
``` 
4. read df
```python
df = data.read_df(file_id="<file_id>")
# df return as pandas dataframe
```

6. read ddf

* ```.parquet must use this function```

```python
ddf = data.read_ddf(file_id="<file_id>")
# ddf return as dask dataframe
```

7. write parquet file
```python
df = ... # pandas dataframe or dask dataframe

data.write(df=df, directory=<directory_id>, name="<save_file_name>", description="<description>", replace=<replace if file exists. default False>, profiling=<True or False default False>, lineage=<list of file id. eg [1,2,3]>)
```

8. writeListDataNode

```python
df = ... # pandas dataframe or dask dataframe
data.writeListDataNode(df=df, directory_id=<directory_id>, name="<save_file_name>", description="<description>", replace=<replace if file exists. default False>, profiling=<True or False default False>, lineage=<list of file id. eg [1,2,3]>)
```

9. get file id
```python
file_id = data.get_file_id(name=<file name>, directory_id=<directory id>)
# file_id return int fileID
```

10. get directory id
```
directory_id = data.get_directory_id(parent_dir_id=<directory id>, name=<file name>)
# directory_id return int directoryID
```

11. get get_file_version
```use for listDataNode```

```python
fileVersion = data.get_file_version(file_id=<file id>)
# return dict `file_id` and `timestamp`
```


## Clickhouse
1. imoprt data to clickhouse

```python
from dsmlibrary.clickhouse import ClickHouse

ddf = ... # pandas dataframe or dask dataframe

## to warehouse
table_name = <your_table_name>
partition_by = <your_partition_by>

connection = { 
  'host': '', 
  'port': , 
  'database': '', 
  'user': '', 
  'password': '', 
  'settings':{ 
     'use_numpy': True 
  }, 
  'secure': False 
}

warehouse = ClickHouse(connection=connection)

tableName = warehouse.get_or_createTable(ddf=ddf, tableName=table_name, partition_by=partition_by)
warehouse.write(ddf=ddf, tableName=tableName)
```

2. query data from clickhouse
```python
query = f""" 
    SELECT * FROM {tableName} LIMIT 10 
""" 
warehouse.read(sqlQuery=query)

```

3. drop table
```python
warehouse.dropTable(tableName=table_name)
```

- optional
```use for custom config insert data to clickhouse```
```python
config = {
  'n_partition_per_block': 10,
  'n_row_per_loop': 1000
}
warehouse = ClickHouse(connection=connection, config=config)
```

4. truncate table
```
warehouse.truncateTable(tableName=table_name)
```

# API
## dsmlibrary
### dsmlibrary.datanode.DataNode
- upload_file
- download_file
- read_df
- read_ddf
- write
- get_file_id

### dsmlibrary.clickhouse.ClickHouse
- get_or_createTable
- write
- read
- dropTable

# Use for pipeline 

```
data = DataNode(apikey="<APIKEY>")
```

use api key for authenticate

## MDM
1. semantic similarity
```
pip install "dsmlibrary[mdm]"
```

see example [here](./example/mdm_example.ipynb)