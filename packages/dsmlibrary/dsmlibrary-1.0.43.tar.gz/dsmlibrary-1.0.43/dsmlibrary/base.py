import os
import requests
import time

from minio import Minio

defind_clear_output = False
try:
    from IPython.display import clear_output
    defind_clear_output = True
except:
    pass

discovery = os.environ.get('discovery_url', "https://discovery.data.storemesh.com")

_base_discovery_api = os.environ.get('BASE_DISCOVERY_API', "https://api.discovery.data.storemesh.com")
_internal_base_discovery_api = os.environ.get('INTERNAL_BASE_DISCOVERY_API',"http://discovery-backend:8000")

_external_api_minio = os.environ.get('external_api_minio',"")
_internal_api_minio = os.environ.get('internal_api_minio',"")

_base_object_storage_url = os.environ.get('base_minio_url', "api.minio.data.storemesh.com")
bucket_name = os.environ.get('bucketname', 'dataplatform')

class Base:
    def __init__(self, token=None, verbose=True, dataplatform_api_uri=_base_discovery_api, object_storage_uri=_base_object_storage_url, object_storage_secue=None, apikey=None):
        """_summary_

        Args:
            token (str, required): token get from discovery. Defaults to None.
            verbose (bool, optional): display logging. Defaults to True.
            dataplatform_api_uri (str, optional): dataplatform uri. Defaults to "https://api.discovery.data.storemesh.com".

        Raises:
            Exception `Please enter your token from dsmOauth`: Invalid token
            Exception `Can not connect to DataPlatform`: Some thing wrong connection with dataplatform
            Exception `Can not get objectstorage user`: Some thing wrong connection with objectstorage
        """
        
        self._verbose = verbose
        _internal = os.environ.get('internal', None) == "true"
        self._internal = _internal
        self._base_minio_url = _base_object_storage_url
        if self._internal:
            base_discovery_api = _internal_base_discovery_api
        else:
            base_discovery_api = dataplatform_api_uri
            self._base_minio_url = object_storage_uri
        self._base_discovery_api = base_discovery_api
        self._discovery_api = f"{base_discovery_api}/api/v2"
        
        if (token is None) and (apikey is None):
            print(f"Please get token from {self._base_discovery_api.replace('api.','')}")
            token = input("Your Token : ")
            if defind_clear_output:
                time.sleep(2)
                clear_output()
        if (token in [None, '']) and apikey == None:
            raise Exception('Please enter your token from discovery')
        self._jwt_header = {
            'Authorization': f'Bearer {token}'
        }
        if apikey != None:
            self._jwt_header = {
                'Authorization': f'Api-Key {apikey}'
            }
        _res = requests.get(f"{base_discovery_api}/api/v2/account/me/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Can not connect to DataPlatform, {txt}")
        self.token = token
        self.apikey = apikey
        self._tmp_path = 'dsm.tmp'
        os.makedirs(self._tmp_path, exist_ok=True)
        _res = requests.get(f"{base_discovery_api}/api/minio/minio-user/me/", headers=self._jwt_header)
        if _res.status_code != 200:
            raise Exception("Can not get objectstorage user")
        data = _res.json()
        self._minio_access = data['access']
        self._minio_secret = data['secret']
        
        if object_storage_secue != None:
            secure_url = object_storage_secue
            _scheme = "https" if object_storage_secue else "http"
        else:
            secure_url = not _internal
            _scheme = "http" if self._internal else "https"
            
        self.client = Minio(
            self._base_minio_url,
            access_key=self._minio_access,
            secret_key=self._minio_secret,
            secure=secure_url
        )
        
        self._storage_options = {
            'key': self._minio_access,
            'secret': self._minio_secret,
            'client_kwargs':{
                'endpoint_url': f"{_scheme}://{self._base_minio_url}"
            },
            'use_listings_cache': False,
            'default_fill_cache': False,
        }
        if self._verbose: print("Init DataNode sucessful!")
        
    def _replace_minio_api(self, url):
        return url.replace('https', 'http').replace(_external_api_minio, _internal_api_minio)
    
    def _check_fileExists(self, directory, name):
        _res = requests.get(f"{self._discovery_api}/directory/{directory}/fileExists/?filename={name}", headers=self._jwt_header)
        if _res.status_code == 200:
            replace = False
        elif _res.status_code == 302:
            replace = input(f"File {name} alrady exists, do you want to replace y/n : ").replace(' ', '').lower() == "y"
        else:
            status = _res.json() if _res.status_code < 500 else ""
            raise Exception(f"check file exists error {status}")
        return replace
    
    def _check_fileExists_no_ask(self, directory, name):
        _res = requests.get(f"{self._discovery_api}/directory/{directory}/fileExists/?filename={name}", headers=self._jwt_header)
        if _res.status_code == 200:
            is_exist = False
        elif _res.status_code == 302:
            is_exist = True
        else:
            status = _res.json() if _res.status_code < 500 else ""
            raise Exception(f"check file exists error {status}")
        return is_exist