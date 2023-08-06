import requests
from .utils import check
from .datanode import DataNode

def find_parents(lineages, src_file_id):
    edges = lineages.get('edges', [])
    parents = [elm.get('target') for elm in edges if elm.get('source')==src_file_id]
    return parents

class TransferDataNode:
    def __init__(self, datanode_src=None, datanode_dst=None, verbose=True) -> None:
        check.check_type(variable=datanode_src, variableName="datanode_src", dtype=DataNode)
        check.check_type(variable=datanode_dst, variableName="datanode_dst", dtype=DataNode)
        self._datanode_src = datanode_src
        self._datanode_dst = datanode_dst
        self._verbose = verbose
        if self._verbose: print("Init TransferDataNode sucessful!")
    
    def copy_datanode(self, file_id, dst_dir_id):
        r = requests.get(f"{self._datanode_src._base_discovery_api}/api/v2/file/{file_id}/", headers=self._datanode_src._jwt_header)
        check.check_http_status_code(response=r)
        data = r.json()
        # print(data)
        # print(f"{data.get('id')} - {data.get('name')}")
        _dtype = data.get('type').get('name')
        if _dtype == "parquet":
            df = self._datanode_src.read_ddf(file_id=file_id)
            print(df)
            meta = self._datanode_dst.write(
                df=df,
                directory=dst_dir_id,
                name=data.get('name'),
                description=data.get('description'),
                replace=True,
                profiling=True
            )
            return meta.get('file_id')
        

    def copy_parent(self, lineages, parent_id, dst_dir_id):
        parents = find_parents(lineages=lineages, src_file_id=parent_id)
        print(parents)
        if parents == []:
            _parent_id = self.copy_datanode(file_id=parent_id, dst_dir_id=dst_dir_id)
            return [_parent_id]
        _parent_id = []
        for parent in parents:
            _parent_id += self.copy_parent(lineages=lineages, parent_id=parent, dst_dir_id=dst_dir_id)
            datanode_id = self.copy_datanode(file_id=parent, dst_dir_id=dst_dir_id)
            if datanode_id == None:
                continue
            _parent_id += [datanode_id]
            print(f"datanode id : {datanode_id} | parent : {_parent_id}")
            self._set_lineage(file_id=datanode_id, parent_ids=_parent_id)
        return _parent_id
    
    def _set_lineage(self, file_id, parent_ids):
        if parent_ids != []:
            parent_ids = [elm for elm in parent_ids if elm != None and elm != file_id]
            r = requests.post(f"{self._datanode_dst._base_discovery_api}/api/v2/file/{file_id}/setLineage/",
                            headers=self._datanode_dst._jwt_header,
                            json={
                                'lineage': parent_ids
                            }
            )
            check.check_http_status_code(response=r)
        
    
    def transfer(self, src_file_id=None, dst_dir_id=None):
        check.check_type(variable=src_file_id, variableName="src_file_id", dtype=int)
        check.check_type(variable=dst_dir_id, variableName="dst_dir_id", dtype=int)
        r = requests.get(f"{self._datanode_src._base_discovery_api}/api/v2/file/{src_file_id}/getLineage/", headers=self._datanode_src._jwt_header)
        check.check_http_status_code(response=r)
        lineages = r.json()
        _parents = self.copy_parent(lineages=lineages, parent_id=src_file_id, dst_dir_id=dst_dir_id)
        _datanode = self.copy_datanode(file_id=src_file_id, dst_dir_id=dst_dir_id)
        print(f"file : {_datanode} | parents : {_parents}")
        self._set_lineage(file_id=_datanode, parent_ids=_parents)