
from typing import List, Optional

from docarray.typing import NdArray
from docarray import BaseDoc, DocList
from pydantic import Field

from docarray.index import HnswDocumentIndex as HI

from chatmates.embed import HuggingFaceEmbeddings, HuggingFaceInstructEmbeddings

from chatmates.common import log

class IDoc(BaseDoc):
    text: str  # concatenation of title, overview and actors names
    dense_rep: Optional[NdArray[768]] = Field(
        is_embedding=True
    )  # vector representation of the document

    def make_rep(self, embed_fn):
        self.dense_rep = embed_fn(self.text)

    @staticmethod
    def from_part(part):
        return IDoc(text=part['text'], dense_rep=None)

class DocAsk:
    def __init__(self, index_path='./idoc_index/default') -> None:
        super().__init__()
        self.encoder = None
        self.embed_dim = 768
        self.idocs: List[IDoc] = []

        self.index = HI[IDoc](work_dir=index_path)

    
    def _embed_text(self, text):
        if self.encoder is None:
            self.encoder = HuggingFaceInstructEmbeddings()

        vector = self.encoder.embed_query(text) 
        return vector
    
    def ingest_embed_index(self, json_doc):
        self.doc = json_doc #simple list of docs (f1 | f2 | ..)*

        log('build idoc')
        self.idocs = [IDoc.from_part(part) for part in self.doc]
        log('embedding')
        for doc in self.idocs:
            doc.make_rep(self._embed_text)

        log('indexing')
        dl = DocList[IDoc](self.idocs)
        self.dl = dl
        self.index.index(dl)
        
    def query(self, query_text, limit=10):
        qrep = self._embed_text(query_text)
        store = self.index
        #vector_q = store.build_query().find(qrep).limit(10).build()
        #vector_results = store.execute_query(vector_q)
        results, scores = store.find(qrep, limit=limit, search_field='dense_rep')
        results_text = [res.text for res in results]
        res_scores = list(zip(results_text, scores))
        for res, score in res_scores:
            print(score, res)

            
        
        return res_scores

    



