import io
import time
import string
import inspect
import requests
import os
import datetime
import pandas as pd
import dask.dataframe as dd
from operator import itemgetter

from .base import bucket_name, Base
from .dataset import DatasetManager
from .utils.requests import check_http_status_code
from .utils import check, listDatanode

def append_slash(txt):
    if txt[-1] != '/':
        txt += '/'
    return txt

class DataNode(DatasetManager):
    def write(self, df=None, directory=None, name=None, description="", 
              replace=None, profiling=False, lineage=None,
              **kwargs):
        """
        _summary_

        Args:
            df (dask or pandas DataFrame, required): _description_. Defaults to None.
            directory (int, required): _description_. Defaults to None.
            name (str, required): _description_. Defaults to None.
            description (str, optional): _description_. Defaults to "".
            replace (bool, optional): _description_. Defaults to None.
            profiling (bool, optional): _description_. Defaults to False.
            lineage (list, optional): _description_. Defaults to None.
            
        Returns:
            dict: status
        """
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Invalid type expect ddf(dask dataframe) or df(pandas dataframe), Please input `df=`, but got {type(df)}")
        if name == None or type(name) != str:
            raise Exception(f"Please input data `name`=<str>, but got {type(name)}")
        if directory == None or type(directory) != int:
            raise Exception(f"Please input data `directory`=<int>, but got {type(directory)}")
        if description=="" or type(description)!=str:
            description = f"data {name}"
            
        name = f'{name}.parquet'
        replace = self._check_fileExists(directory, name) if replace is None else replace
        _res = requests.post(f'{self._discovery_api}/file/', headers=self._jwt_header,
                                json={
                                    "name": name,
                                    "description": description,
                                    "directory": directory,
                                    "is_use": False,
                                    "replace": replace
                                }
                            )
        if _res.status_code != 201:
            raise Exception(f"can not create directory in discovery {_res.json()}")
        meta = _res.json()
        
        if 'append' in kwargs and kwargs['append']:
            overwrite_parquet = False
        else:
            overwrite_parquet = True
        
        df.to_parquet(f"s3://{bucket_name}/{meta['key']}",
            storage_options=self._storage_options,
            engine="pyarrow",
            overwrite=overwrite_parquet,  # force delete old file
            **kwargs
        )

        _file_already = check.check_file_already(discovery_api=self._discovery_api, file_id=meta.get('id'), header=self._jwt_header)
        
        # create profiling & data dict
        if profiling and _file_already:
            requests.get(f"{self._discovery_api}/file/{meta['id']}/createDatadict/", headers=self._jwt_header)
            requests.get(f"{self._discovery_api}/file/{meta['id']}/createProfileling/", headers=self._jwt_header)
        
        _response = {
            'sucess': True,
            'file_id': meta['id'],
            'path': meta['path']
        }
        
        if (lineage != None and len(lineage) > 0) and _file_already:
            check.check_lists_int(data=lineage, dataName="lineage")
            r = requests.post(f"{self._discovery_api}/file/{meta['id']}/setLineage/", 
                              headers=self._jwt_header,
                              json={
                                  'lineage': lineage
                              }
            )
            try:
                check.check_http_status_code(r)
            except Exception as e:
                _response.update({
                    'lineage_msg': str(e),
                    'lineage': False
                })
            else:
                _response.update({
                    'lineage': "created",
                    'lineage': True
                })
        return _response
    

    def _write_listfile(self, type, file_name, file_id, directory_id, lineage, description):
        _file_id = file_id
        name = f'{file_name}.{type}'
        _is_file_exists = self._check_fileExists_no_ask(directory_id, name)
        
        if description == "":
            description = name
            
        timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")     
        if not _is_file_exists:

            _res = requests.post(f'{self._discovery_api}/file/', headers=self._jwt_header,
                                    json={
                                        "name": name,
                                        "description": description,
                                        "directory": directory_id,
                                        "is_use": True,
                                        "replace": _is_file_exists,
                                        "context": {
                                            "version_file_id" : {
                                                _file_id: {
                                                    'timestamp': timestamp,
                                                    'file_id': _file_id
                                                }
                                            }
                                        }
                                    }
                                )
        else:
            list_datanode_id = self.get_file_id(name=name, directory_id=directory_id)
            _res = requests.get(f'{self._discovery_api}/file/{list_datanode_id}/',  headers=self._jwt_header)
            check.check_http_status_code(response=_res)
            meta = _res.json()
            version_file_id = meta.get('context', {}).get('version_file_id', {})
            version_file_id.update({
                _file_id: {
                    'timestamp': timestamp,
                    'file_id': _file_id
                }
            })
            __res = requests.patch(f'{self._discovery_api}/file/{list_datanode_id}/',  headers=self._jwt_header,
                                  json={
                                      'context':{
                                          'version_file_id': version_file_id
                                      }
                                  }
            )
            check.check_http_status_code(response=__res)
        check.check_http_status_code(response=_res)
        meta = _res.json()
        _file_already = check.check_file_already(discovery_api=self._discovery_api, file_id=meta.get('id'), header=self._jwt_header)
        if (lineage != None and len(lineage) > 0) and _file_already:
            check.check_lists_int(data=lineage, dataName="lineage")
            r = requests.post(f"{self._discovery_api}/file/{meta['id']}/setLineage/", 
                              headers=self._jwt_header,
                              json={
                                  'lineage': lineage
                              }
            )
            try:
                check.check_http_status_code(r)
            except Exception as e:
                meta.update({
                    'lineage_msg': str(e),
                    'lineage': False
                })
            else:
                meta.update({
                    'lineage': "created",
                    'lineage': True
                })
        
        return {
            'status': 'sucess',
            'file_id': meta.get('id'),
            'path': meta['path']
        }

    def writeListFile(self, directory_id=None, file_path=None, description="", lineage=None, replace=None):
        original_file_name = os.path.basename(file_path)
        original_file_name, file_extension = original_file_name.split('.')

        timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        file_name = f"{original_file_name}-{timestamp}.{file_extension}"
        

        _response = self.upload_file(
                directory_id=directory_id, 
                file_path=file_path, 
                file_name=file_name,
                description=description, 
                replace=True,
            )
        _file_id = _response.get('id', 0)

        res = self._write_listfile(
            type='listFile', 
            file_name=original_file_name,
            file_id=_file_id, 
            directory_id=directory_id, 
            lineage=lineage,
            description=description,
        )

        return res
        

    def writeListDataNode(self, df=None, directory_id=None, name=None, description="", 
              replace=None, profiling=False, lineage=None,
              **kwargs):
        """_summary_

        Args:
            df (_type_, optional): _description_. Defaults to None.
            directory_id (_type_, optional): _description_. Defaults to None.
            name (_type_, optional): _description_. Defaults to None.
            description (str, optional): _description_. Defaults to "".
            replace (_type_, optional): _description_. Defaults to None.
            profiling (bool, optional): _description_. Defaults to False.
            lineage (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        _response = self.write(df=df, directory=directory_id, name=f"{name}-{timestamp}", replace=replace, description=description, profiling=profiling, lineage=lineage)
        _file_id = _response.get('file_id', 0)

        res = self._write_listfile(
            type='listDataNode', 
            file_name=name,
            file_id=_file_id, 
            directory_id=directory_id, 
            lineage=lineage,
            description=description,
        )

        return res
    
    def get_file(self, file_id=None):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            e: _description_

        Returns:
            _type_: _description_
        """
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Some thing wrong, {txt}")
        meta = _res.json()
        try:
            response = self.client.get_object(bucket_name=bucket_name, object_name=meta['s3_key'])
        except Exception as e:
            raise e
        else:
            meta.update({
                'owner': meta['owner']['user']
            })
            meta = {key: value for key,value in meta.items() if key in ['owner', 'name', 'description', 'path', 'directory', 'human_size']}
            return meta, io.BytesIO(response.data)
        
    
    def read_ddf(self, file_id=None, index=0, extra_param={}):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.
            index (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            e: _description_

        Returns:
            _type_: _description_
        """
        
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        check_http_status_code(_res)
        meta = _res.json()
        meta.update({
            'key': append_slash(meta['s3_key'])
        })
        _f_type = meta['type']['name']
        if _f_type == "parquet":
            return dd.read_parquet(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options, **extra_param)
        elif _f_type == "csv":
            return dd.read_csv(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options, **extra_param)
        elif _f_type == "sql-query":
            r = requests.get(f"{self._base_discovery_api}/api/v2/file/{meta['id']}/getSqlQuery/", headers=self._jwt_header)
            check_http_status_code(r)
            r = requests.get(f"{self._base_discovery_api}/api/sql/query/{r.json()['id']}/", headers=self._jwt_header)
            check_http_status_code(r)
            data = r.json()
            _database = DatabaseManagement(
                token=self.token, 
                apikey=self.apikey, 
                dataplatform_api_uri=self._base_discovery_api,
                object_storage_uri=self._base_minio_url,
            )
            database_id = data['database']
            database_meta, schema = _database.get_database_schema(database_id=database_id)
            
            where_condition = extra_param.get('where_condition', '')

            exec(f"""
{schema}
from sqlalchemy import sql
{data['query']+where_condition}
            """, globals())
            
            # to reorder metadata for dask
            reordered_meta = {item['column']: item['type'] for item in data['meta']}                        
            con_str = database_meta['sqlalchemy_uri']
            updated_reordered_meta = _database._get_order_meta_data(reordered_meta, data['pk_column'], query, con_str)
            updated_reordered_meta = {item['column']: item['type'] for item in updated_reordered_meta}  
              
            return _database.read_sql_query(database_id=database_id, query_function=query, pk_column=data['pk_column'], meta=updated_reordered_meta)
        elif _f_type == "listDataNode":
            return listDatanode.get_list_datanode(meta=meta, index=index, headers=self._jwt_header, 
                                                  base_uri=self._base_discovery_api, storage_options=self._storage_options,
                                                  bucketName=bucket_name
            )
        return Exception(f"Can not read file extension {_f_type}, support [parquet, csv]")
        
    def read_df(self, file_id=None):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Some thing wrong, {txt}")
        meta = _res.json()
        meta.update({
            'key': append_slash(meta['s3_key'])
        })
        _f_type = meta['type']['name']
        if _f_type == "parquet":
            return pd.read_parquet(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        elif _f_type == "csv":
            return pd.read_csv(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        return Exception(f"Can not read file extension {_f_type}, support [parquet, csv]")
    
    def get_file_id(self, name=None, directory_id=None):
        """_summary_

        Args:
            name (_type_, optional): _description_. Defaults to None.
            directory_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=name, variableName="name", dtype=str)
        check.check_type(variable=directory_id, variableName="directory_id", dtype=int)
        r = requests.post(f"{self._discovery_api}/file/get-file-id/", headers=self._jwt_header, 
                          json={
                              'name': name,
                              'directory': directory_id
                          }
        )
        check_http_status_code(r)
        return r.json().get('id')
    
    def get_directory_id(self, parent_dir_id=None, name=None):
        """_summary_

        Args:
            parent_dir_id (_type_, optional): _description_. Defaults to None.
            name (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=parent_dir_id, variableName="parent_dir_id", dtype=int)
        check.check_type(variable=name, variableName="name", dtype=str)
        res = requests.post(f"{self._discovery_api}/directory/get_directory_id/", headers=self._jwt_header,
                          json={
                                    'parent_dir': parent_dir_id,
                                    'name': name
                          }
        )
        check.check_http_status_code(response=res)
        return res.json().get('id')
    
    def get_file_version(self, file_id=None):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=file_id, variableName="file_id", dtype=int)
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        check.check_http_status_code(response=_res)
        meta = _res.json()
        version_file_ids = meta.get('context', {}).get('version_file_id', {})
        version_file_ids = version_file_ids.values()
        version_file_ids = sorted(version_file_ids, key=itemgetter('timestamp'), reverse=False)
        return version_file_ids
    
    
    def get_update_data(self, file_id=None):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        check_http_status_code(_res)
        meta = _res.json()
        meta.update({
            'key': append_slash(meta['s3_key'])
        })
        _f_type = meta['type']['name']
        
        if _f_type == "listDataNode":
            
            ddf_current = listDatanode.get_list_datanode(
                meta=meta, 
                index=-1, 
                headers=self._jwt_header,
                base_uri=self._base_discovery_api,
                storage_options=self._storage_options,
                bucketName=bucket_name
            )
            
            try:
            
                ddf_previous = listDatanode.get_list_datanode(
                    meta=meta, 
                    index=-2, 
                    headers=self._jwt_header,
                    base_uri=self._base_discovery_api,
                    storage_options=self._storage_options,
                    bucketName=bucket_name
                )
            except Exception as e:
                if self._verbose: print(e)
                ddf_previous = None
            
            return listDatanode.get_change_data(ddf_current, ddf_previous)
    
        return Exception(f"Can not read file extension {_f_type}, support only [listDataNode]")
    
    
    
    
class DatabaseManagement(Base):
    def _get_connection_str(self, con_id=None):
        '''Get sqlalchemy connection string
        
        Args:
        ...
        '''
        if type(con_id) != int:
            raise Exception(f"Expect `con_id`=<int> but got {type(con_id)}, please input `con_id` eg con_id=0")
        r = requests.get(f"{self._base_discovery_api}/api/sql/database/{con_id}/", headers=self._jwt_header)
        if r.status_code > 500:
            return r.content
        elif r.status_code >= 400:
            return r.json()
        data = r.json()
        if 'sqlalchemy_uri' in data:
            return data['sqlalchemy_uri']
        return f"Some thing wrong!, {data}"
    
    def get_table_schema(self, table_id=None):
        """_summary_

        Args:
            table_id (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        
        if type(table_id) != int:
            raise Exception(f"Expect `table_id`=<int> but got {type(table_id)}, please input `table_id` eg table_id=0")
        r = requests.get(f"{self._base_discovery_api}/api/sql/table/{table_id}/", headers=self._jwt_header)
        if r.status_code >= 404:
            return r.content, ""
        elif r.status_code >= 400:
            return r.json(), ""
        meta = r.json()
        schema = meta.pop('schema_code')
        return meta, schema

    def get_database_schema(self, database_id=None):
        """_summary_

        Args:
            database_id (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=database_id, variableName="database_id", dtype=int)
        r = requests.get(f"{self._base_discovery_api}/api/sql/database/{database_id}/", headers=self._jwt_header)
        check.check_http_status_code(response=r)
        meta = r.json()
        schema = meta.pop('schema_code')
        return meta, schema

    def check_permission(self, con_id, table, column):
        '''Check table and column accesing permission from con_id
        
        Args:
        ...
        '''
        pass


    def check_query_permission(self, query, con_id):
        '''Check table and column accesing permission from sqlalchemy query   
        
        Args:
        ...
        '''
        for column in query.column_descriptions:
            table_name = column['expr'].table.name
            
            # check permission by using column['name'] and table_name
            if not self.check_permission(con_id=con_id, table=table_name, column=column['name']):
                raise Exception(f"You don't have permission in table={table_name}, column={column['name']}")  
    
    def _create_pandas_meta(self, meta, pk_column):
        meta_dask = pd.DataFrame(columns=list(meta.keys()))
        if meta[pk_column] == 'Int64':
            meta[pk_column] = 'int64'
        meta_dask = meta_dask.astype(meta)
        meta_dask = meta_dask.set_index(pk_column)
        return meta_dask
    
    def _get_order_meta_data(self, meta, pk_column, query_function, con_str):
        possible_divisions = self._get_possible_str_division()
        if meta[pk_column] in ['str', 'string']:
            ddf = dd.read_sql_query(sql=query_function(),  con=con_str, index_col=pk_column, divisions=possible_divisions)
        else:
            ddf = dd.read_sql_query(sql=query_function(),  con=con_str, index_col=pk_column, npartitions=1)
        columns_order = ddf.columns                    
        
        # to reorder metadata for dask          
        try:
            # reordered_meta = [ {'column': column, 'type': meta[column] } for column in columns_order]
            reordered_meta = []
            for column in columns_order:
                if column in meta:
                    reordered_meta.append({'column': column, 'type': meta[column] })
                else:
                    print(f'Warning! column "{column}" exist in data source but not exist in reflection schema, so it will be auto cast to "string". If you want to use data type same as data source, please regenreate reflection schema')
                    reordered_meta.append({'column': column, 'type': 'string' })
            
            reordered_meta.append({'column': pk_column, 'type': meta[pk_column]}) # add pk meta at the end
        except KeyError as ke:
            raise KeyError(f"{ke}. This column is exist in data source but not exist in reflection schema. Maybe this is a new column in data source. Please check your reflection schema file and regenreate it")
        return reordered_meta

    
    def write_sql_query(self, query_function=None, directory_id=None, database_id=None, pk_column=None, 
                        meta=None, name=None, desciption=None, replace=None, *args, **kwargs):
        """_summary_

        Args:
            query_function (_type_, optional): _description_. Defaults to None.
            directory_id (_type_, optional): _description_. Defaults to None.
            database_id (_type_, optional): _description_. Defaults to None.
            pk_column (_type_, optional): _description_. Defaults to None.
            meta (_type_, optional): _description_. Defaults to None.
            name (_type_, optional): _description_. Defaults to None.
            desciption (_type_, optional): _description_. Defaults to None.
            replace (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        
        if query_function is None or (inspect.isfunction(query_function)==False and type(query_function)!=str):
            raise Exception(f"Expect `query`=<function>/<str> but got {type(query_function)}, please input `query`")
        
        if directory_id == None or type(directory_id) != int:
            raise Exception(f"Please input data `directory`=<int>, but got {type(directory_id)} eg directory_id=0")
        
        if database_id == None or type(database_id) != int:
            raise Exception(f"Please input data `database_id`=<int>, but got {type(database_id)} eg database_id=0")
        
        if pk_column == None or type(pk_column) != str:
            raise Exception(f"Please input data `con_id`=<str>, but got {type(pk_column)} eg pk_column='id' ")
        
        if meta == None or type(meta) != dict:
            raise Exception(f"Please input data `meta`=<dict>, but got {type(meta)} eg meta='{{'id':'Int64'}}' ")
        
        if name == None or type(name) != str:
            raise Exception(f"Please input data `name`=<str>, but got {type(name)} eg name='myData' ")
        
        if desciption == None:
            desciption = f"query of {name}"
    
        _replace = self._check_fileExists(directory_id, name) if replace is None else replace
        
        database_meta, schema = self.get_database_schema(database_id=database_id)
        con_str = database_meta['sqlalchemy_uri']
        
        if inspect.isfunction(query_function):            
            query_function_str = inspect.getsource(query_function)
            query_function_function = query_function
        elif type(query_function) == str:
            query_function_str = query_function
            
            exec(f"""
{schema}
from sqlalchemy import sql
{query_function}
            """, globals())
            query_function_function = query        
        # import pdb; pdb.set_trace()
        # print(pk_column)
        
        reordered_meta = self._get_order_meta_data(
            meta=meta, 
            pk_column=pk_column, 
            query_function=query, 
            con_str=con_str,
        )
#         possible_divisions = self._get_possible_str_division()
#         if meta[pk_column] in ['str', 'string']:
#             ddf = dd.read_sql_query(sql=query(),  con=con_str, index_col=pk_column, npartitions=1, divisions=possible_divisions)
#         else:
#             ddf = dd.read_sql_query(sql=query(),  con=con_str, index_col=pk_column, npartitions=1)
#         columns_order = ddf.columns                    
        
#         # to reorder metadata for dask
#         # reordered_meta = [ {'column': column, 'type': type } for column, type in meta.items()]        
#         reordered_meta = [ {'column': column, 'type': meta[column] } for column in columns_order]
#         reordered_meta.append({'column': pk_column, 'type': meta[pk_column]}) # add pk meta at the end

        res = requests.post(f"{self._base_discovery_api}/api/sql/query/", headers=self._jwt_header,
                          json={
                                "directory": directory_id,
                                "database": database_id,
                                "name": name,
                                "description": desciption,
                                "pk_column": pk_column,
                                "query": query_function_str,
                                "meta": reordered_meta,
                                "replace": _replace
                          }
        )
        check_http_status_code(res)
        return res.json() if res.status_code < 500 else res.content
    
    def _get_possible_str_division(self):
        possible_divisions = list('0123456789' + string.ascii_lowercase + string.ascii_uppercase)
        possible_divisions.sort()
        return possible_divisions
    
    def read_sql_query(self, database_id=None, query_function=None, pk_column=None, meta=None):
        """_summary_

        Args:
            table_id (_type_, optional): _description_. Defaults to None.
            query_function (_type_, optional): _description_. Defaults to None.
            pk_column (_type_, optional): _description_. Defaults to None.
            meta (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if database_id == None or type(database_id) != int:
            raise Exception(f"Please input data `database_id`=<int>, but got {type(database_id)} eg database_id=0")
        
        if query_function is None or inspect.isfunction(query_function) == False:
            raise Exception(f"Expect `query`=<function> but got {type(query_function)}, please input `query`")
        
        if pk_column == None or type(pk_column) != str:
            raise Exception(f"Please input data `con_id`=<str>, but got {type(pk_column)} eg pk_column='id' ")
        
        if meta == None or type(meta) != dict:
            raise Exception(f"Please input data `meta`=<dict>, but got {type(meta)} eg meta='{{'id':'Int64'}}' ")
        
        database_meta, schema = self.get_database_schema(database_id=database_id)
        con_str = database_meta['sqlalchemy_uri']
        df_meta = self._create_pandas_meta(meta=meta, pk_column=pk_column)
        if meta[pk_column] in ['str', 'string']:
            possible_divisions = self._get_possible_str_division()
            ddf = dd.read_sql_query(
                sql=query_function(), 
                con=con_str, 
                index_col=pk_column, 
                meta=df_meta, 
                divisions=possible_divisions
            )
        else:            
            ddf = dd.read_sql_query(
                sql=query_function(), 
                con=con_str, 
                index_col=pk_column, 
                meta=df_meta, 
                bytes_per_chunk="300 MB"
                # npartitions=1,  # temporary force partition to 1 because of max connection of source limit
            )
        
        return ddf
    
    
    