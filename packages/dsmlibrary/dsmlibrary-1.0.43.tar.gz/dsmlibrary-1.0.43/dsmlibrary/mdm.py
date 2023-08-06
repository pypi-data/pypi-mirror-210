import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

class MDM:
    def __init__(self, master_data: pd.DataFrame, text_column: str, model_name=None, model_type='text_distance'):
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
        
        self.master_data = master_data
        self.text_column = text_column
        if model_type == "semantic_similarity":
            if model_name == None:
                model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
            
            self.model = SentenceTransformer(model_name)
            
            self.master_data_encoded = self.encode_text()
        elif model_type == 'text_distance':
            pass
    
    def encode_text(self):
        text_list = self.master_data[self.text_column].values
        return self.model.encode(text_list, convert_to_tensor=True)
    
    def get_topn_similarity(self, text_list, topn=20):
        X = self.model.encode(text_list, convert_to_tensor=True)
        cos_sim = util.cos_sim(X, self.master_data_encoded)
        cos_sim_np = cos_sim.numpy()
        
        indexs = np.argsort(cos_sim_np, axis=1)   
        n_master = indexs.shape[0]
             
        des_topn_indexs = np.fliplr(indexs)[:, :topn]        
        sorted_score = cos_sim_np[np.arange(n_master)[:,None], des_topn_indexs]
        return des_topn_indexs, sorted_score
        
    
        
