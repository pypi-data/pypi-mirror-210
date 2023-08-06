import requests
from . import check
import dask.dataframe as dd
from operator import itemgetter
import hashlib

def md5hash(x):
    return hashlib.md5(x.encode('utf-8')).hexdigest()

def get_list_datanode(meta, index, headers, base_uri, storage_options, bucketName):
    version_file_ids = meta.get('context', {}).get('version_file_id', [])
    version_file_ids = version_file_ids.values()
    version_file_ids = sorted(version_file_ids, key=itemgetter('timestamp'), reverse=False)
    
    if index < len(version_file_ids):
        version_file_id = version_file_ids[index]
        print(f"version_file_id : {version_file_id}")
        _res = requests.get(f"{base_uri}/api/v2/file/{version_file_id.get('file_id')}/", headers=headers)
        check.check_http_status_code(response=_res)
        meta = _res.json()
        return dd.read_parquet(f"s3://{bucketName}/{meta['s3_key']}", storage_options=storage_options)
    else:
        # index out of range
        raise Exception(f"list_datanode is out of range for index {index}")

def get_change_data(
        ddf_current: dd.DataFrame, 
        ddf_previous: dd.DataFrame,
    ) -> dd.DataFrame:

    ddf_current['_hash'] = ddf_current.astype(str).values.sum(axis=1)
    ddf_current['_hash'] = ddf_current['_hash'].apply(md5hash, meta=('_hash', 'object'))   

    if ddf_previous is not None:
        # already have landing of this table
        ddf_previous['_hash'] = ddf_previous.astype(str).values.sum(axis=1)
        ddf_previous['_hash'] = ddf_previous['_hash'].apply(md5hash, meta=('_hash', 'object'))
        previous_hash_index = ddf_previous['_hash'].unique().compute()        
        ddf_change = ddf_current[~ddf_current['_hash'].isin(previous_hash_index)]
    else:
        ddf_change = ddf_current
        
    ddf_change = ddf_change.drop(columns=['_hash'])

    return ddf_change