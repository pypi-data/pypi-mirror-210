from clickhouse_driver import Client
from .utils.clickhouse import create_table, insert_ddf, insert_df, drop_table
import pandas as pd
import dask.dataframe as dd
from .utils import check, clickhouse

class ClickHouse:
    
    def __init__(self, connection=None, verbose=True, config={}):

        """_summary_

        Args:
            connection (dict, required): _description_. Defaults to None.
            verbose (bool, optional): _description_. Defaults to True.
            config (config, optional): _description_. Defaults to {}.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_
            e: _description_
        """
        
        if connection is None or type(connection)!= dict:
            """ 
            connection = {
                'host': 'localhost',
                'port': 9090,
                'database': 'warehouse',
                'user': 'clickhouse',
                'password': 'QWER!@#$qwer1234!@#$',
                'settings':{
                    'use_numpy': True
                },
                'secure': False
            }
            """
            raise Exception(f"plase input `connection` or but got connection {type(connection)}")
        self._verbose = verbose
        client = Client(**connection)
        try:
            client.connection.connect()
        except Exception as e:
            raise e
        self._client = client
        self._connection = connection
        
        self._n_row_per_loop = config.get('n_row_per_loop', 1000)
        self._n_partition_per_block = config.get('n_partition_per_block', 10)
        
    def get_or_createTable(self, df=None, tableName=None, partition_by=None):
        """_summary_

        Args:
            df (_type_, optional): _description_. Defaults to None.
            tableName (_type_, optional): _description_. Defaults to None.
            partition_by (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_
            e: _description_

        Returns:
            _type_: _description_
        """
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Please input `df=<dask dataframe or pandas dataframe>`, but got {type(df)}")
        if tableName is None:
            raise Exception("Please input `tableName`")
        if partition_by is None:
            raise Exception("Please input `partition_by`")
        
        if partition_by not in df.columns:
            raise Exception(f"key `{partition_by}` not found in columns, columns are {df.columns}")
        status, e = create_table(self._client, df, tableName, partition_by)
        if status == False:
            if e.code == 57 and self._verbose:
                print(f"table {tableName} already exists!")
            else:
                raise e
        return tableName
    
    def write(self, df=None, tableName=None):
        """_summary_

        Args:
            df (_type_, optional): _description_. Defaults to None.
            tableName (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Please input `df=<dask dataframe or pandas dataframe>`, but got {type(df)}")
        if tableName == None:
            raise Exception(f"Expect `tableName` type str, but got {type(tableName)} please input `tableName` str")
        
        if type(df) == dd.DataFrame:
            insert_ddf(connection=self._connection, ddf=df, tableName=tableName, 
                       n_partition_per_block=self._n_partition_per_block,
                       n_row_per_loop=self._n_row_per_loop
            )
        elif type(df) == pd.DataFrame:
            insert_df(connection=self._connection, df=df, tableName=tableName, n_row_per_loop=self._n_row_per_loop)
        else:
            return "Some thing wrong!"
    
    
    def read(self, sqlQuery=None):
        """_summary_

        Args:
            sqlQuery (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if sqlQuery is None:
            raise Exception(f"plese input `sqlQuery` str but got {type(sqlQuery)}")
        return self._client.query_dataframe(sqlQuery)
    
    def dropTable(self, tableName=None):
        """_summary_

        Args:
            tableName (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if tableName is None:
            raise Exception(f"plese input `tableName` str but got {type(tableName)}")
        return drop_table(client=self._client, table_name=tableName, verbose=self._verbose)
    
    def truncateTable(self, tableName=None):
        """_summary_

        Args:
            tableName (_type_, optional): _description_. Defaults to None.
        """
        check.check_type(variable=tableName, variableName="tableName", dtype=str)
        return clickhouse.truncate(client=self._client, table_name=tableName)