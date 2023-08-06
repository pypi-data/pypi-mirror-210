from clickhouse_driver import Client
from tqdm.auto import tqdm

def drop_table(client, table_name, verbose=True):
    try:
        client.execute(f'DROP TABLE {table_name}')
        if verbose: print(f'DROP TABLE {table_name} sucessful')
        return True
    except Exception as e:
        if verbose: print(str(e))
        return False

def get_info(ddf):
    datas = [{'column_name': col, 'data_type': str(ddf[col].dtype)} for col in ddf.columns]
    return datas

def create_table(client, ddf, tableName, partition_by):
    info = get_info(ddf)
    _map = {
        'int64': 'Int64',
        'float64': 'Float64',
        'float32': 'Float32',
        'object': 'String',
        'datetime64[ns]': 'DateTime DEFAULT now()'  
    }
    sql_column = ", \n".join([f""""{elm['column_name']}" {_map[elm['data_type']]}""" for elm in info])
    sql_txt = f"""
        CREATE TABLE {tableName} ( 
            {sql_column}
        ) ENGINE = MergeTree
        PARTITION BY {partition_by} ORDER BY ({partition_by})
    """
    try:
        client.execute(sql_txt)
    except Exception as e:
        return False, e
    else:
        return True, f"Create table {tableName} sucessful"

def insert_df(df, connection, tableName, n_row_per_loop=1000):
    if df.shape[0] == 0:
        return None
    for column in df:
        if 'datetime' in str(df[column].dtypes):
            df[column] = df[column].dt.strftime("%Y-%m-%d %H:%M:%S")
    sql_txt = f"""INSERT INTO {tableName} VALUES"""
    _client = Client(**connection)
    for lower, upper in tqdm([(i, i+n_row_per_loop) for i in range(0, df.shape[0], n_row_per_loop)]):
        _client.insert_dataframe(sql_txt, df[lower:upper])

def insert_ddf(connection, ddf, tableName, n_partition_per_block=10, n_row_per_loop=1000):
    for lower, upper in tqdm([(i, i+n_partition_per_block) for i in range(0, ddf.npartitions, n_partition_per_block)]):
        ddf.partitions[lower:upper].map_partitions(insert_df, connection=connection, tableName=tableName, n_row_per_loop=n_row_per_loop ,meta=ddf).compute()

def truncate(client, table_name, verbose=True):
    try:
        client.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")
    except Exception as e:
        if verbose: print(f"error truncate {table_name}")
        return False, e
    _sucess_msg = f"truncate {table_name} sucessful"
    if verbose: print(_sucess_msg)
    return True, _sucess_msg