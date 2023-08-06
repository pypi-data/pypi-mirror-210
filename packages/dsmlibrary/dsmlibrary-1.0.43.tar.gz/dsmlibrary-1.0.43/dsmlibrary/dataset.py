import os
import requests
from tqdm.auto import tqdm
from tqdm.utils import CallbackIOWrapper

from .base import Base
from .utils import check, dataset
class DatasetManager(Base):

    def upload_file(self, directory_id=None, file_path=None, file_name=None, description="", lineage=None, replace=None):
        """_summary_

        Args:
            directory_id (_type_, optional): _description_. Defaults to None.
            file_path (_type_, optional): _description_. Defaults to None.
            description (str, optional): _description_. Defaults to "".
            lineage (_type_, optional): _description_. Defaults to None.

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
        if type(file_path) != str :
            raise Exception(f"file_path expect `str` but got {type(file_path)}, or please input `file_path='<path>'`")
        elif not os.path.exists(file_path):
            raise Exception(f"file {os.path.abspath(file_path)} not found")
        if directory_id == None:
             raise Exception("please input directory, like `directory=<id>`")
        _res = requests.get(f"{self._discovery_api}/directory/{directory_id}",  headers=self._jwt_header)
        if _res.status_code == 404:
            raise Exception(f"directory {directory_id} not found or your dose not has permission to access directory")
        
        if file_name:
            f_name = file_name
        else:
            f_name = os.path.basename(file_path)
            
        replace = self._check_fileExists(directory_id, f_name) if replace is None else replace
        
        if description == "":
            description = f"file {f_name}"
            
        _res = requests.post(f"{self._discovery_api}/file/", headers=self._jwt_header,
                             data={
                                 'name': f_name,
                                 'description': description,
                                 'directory': int(directory_id),
                                 'size': os.path.getsize(file_path),
                                 'replace': replace
                             }
                )
        if not _res.status_code in [200, 201]:
            txt = ""
            if _res.status_code < 500:
                txt = _res.json()
            raise Exception(f"{_res.status_code}, {txt}")
        data = _res.json()
        if self._internal:
            data['url'] = self._replace_minio_api(data['url'])
        file_size = os.stat(file_path).st_size
        with open(file_path, 'rb') as f:
            with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                _res = requests.put(data['url'], data=wrapped_file, verify=False)
        if _res.status_code == 200:
            _uploaded = True
        else:
            if self._verbose: print(_res.content.decode())
            raise Exception("Some thing wrong with datastore")
        data.update({
            'uploaded': _uploaded,
        })
        data = {key: value for key, value in data.items() if key in ['uploaded', 'id', 'msg', 'path']}
        
        if lineage != None:
            check.check_lists_int(data=lineage, dataName="lineage")
            r = requests.post(f"{self._discovery_api}/file/{data['id']}/setLineage/", 
                                headers=self._jwt_header,
                                json={
                                    'lineage': lineage
                                }
            )
            try:
                check.check_http_status_code(r)
            except Exception as e:
                data.update({
                    'lineage_msg': str(e),
                    'lineage': False
                })
            else:
                data.update({
                    'lineage': "created",
                    'lineage': True
                })
            
        
        return data
    
    def download_file(self, file_id=None, download_path=None):
        """_summary_

        Args:
            file_id (_type_, optional): _description_. Defaults to None.
            download_path (_type_, optional): _description_. Defaults to None.

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if file_id == None:
             raise Exception("please input file_id")
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/",  headers=self._jwt_header)
        if _res.status_code != 200:
            raise Exception(f"File response code {_res}")
        meta = _res.json()
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/download/",  headers=self._jwt_header)
        if _res.status_code != 200:
            raise Exception("some thing wrong in datastore")
            
        _url = _res.json()['url']
        if self._internal:
            _url = self._replace_minio_api(_url)
            
        _res = requests.get(_url)
        f_path = os.path.join(self._tmp_path, meta['name'])
        if download_path != None:
            if (not os.path.exists(download_path)) or (not os.path.isdir(download_path)):
                raise Exception("`download_path` is not existx or is not directory")
            else:
                f_path = os.path.join(self._tmp_path, meta['name'])
            
        
        total_size_in_bytes= int(_res.headers.get('content-length', 0))
        if self._verbose: print(f"total size : {total_size_in_bytes} B")
        block_size = 1024 #1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        
        with open(f_path, 'wb') as f:
            for data in _res.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
        
        meta.update({
            'download_sucess': os.path.exists(f_path),
            'f_path': f_path
        })
        return meta
    
    def createDataset(self, name=None, tags=None):
        """_summary_

        Args:
            name (_type_, optional): _description_. Defaults to None.
            tags (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=name, variableName="name", dtype=str)
        check.check_type(variable=tags, variableName="tags", dtype=list, child=str)
        
        tags_ids = dataset.get_tag_ids(base_uri=self._base_discovery_api, tags=tags, header=self._jwt_header)
        
        r = requests.post(f"{self._base_discovery_api}/api/v2/dataset/", headers=self._jwt_header,
                          json={
                              'name': name,
                              'title': name,
                              'tag': tags_ids
                          }
        )
        check.check_http_status_code(response=r)
        return r.json()
    
    def createDirectory(self, directory_id=None, name=None, description=None):
        """_summary_

        Args:
            directory_id (_type_, optional): _description_. Defaults to None.
            name (_type_, optional): _description_. Defaults to None.
            description (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        check.check_type(variable=directory_id, variableName="directory_id", dtype=int)
        check.check_type(variable=name, variableName="name", dtype=str)
        check.check_type(variable=description, variableName="description", dtype=str)
        
        r = requests.post(f"{self._base_discovery_api}/api/v2/directory/", headers=self._jwt_header,
                          json={
                              "name": name,
                              "description": description,
                              "parent_dir": directory_id
                          }
        )
        check.check_http_status_code(response=r)
        return r.json()
    
    def get_meta_file(self, file_id):
        _res = requests.get(f'{self._discovery_api}/file/{file_id}/',  headers=self._jwt_header)
        if _res.status_code > 200:
            raise Exception(f'Cannot read meta data of file_id {file_id}')
        return _res.json()