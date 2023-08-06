import qdrant_client as qc
import qdrant_client.models as qmodels
from qdrant_client.models import Distance, VectorParams, Batch
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

import uuid
'''
Decisions:
- why recreate collection, keep older?

Q:
- view db? clean up with single command?
- where does it persist data?
'''
class QdrantDB:
    
    METRIC = Distance.DOT
    DIMENSION = 1536

    def __init__(self, collection_name, dimension):
        self.COLLECTION_NAME = collection_name
        self.DIMENSION = dimension
        #self.client = qc.QdrantClient(path='./qdrant-db') #QdrantClient(":memory:")
        self.client = qc.QdrantClient(url="localhost")

    def create_index(self):
        self.client.recreate_collection(
        collection_name=self.COLLECTION_NAME,
        vectors_config = VectorParams(
                size=self.DIMENSION,
                distance=self.METRIC,
            ),
        optimizers_config=qmodels.OptimizersConfigDiff(memmap_threshold=20000),
        #hnsw_config=qmodels.HnswConfigDiff(on_disk=True)
        )
    
    def add_docs_to_index(self, ids, vectors, payloads):
        ## Add vectors to collection
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=Batch(
                ids = ids,
                vectors=vectors,
                payloads=payloads
            ),
        )

    def _generate_query_filter(self, query, field_filters=None):
        """Generates a filter for the query.
        Args:
            query: A string containing the query.
            doc_types: A list of document types to search.
            block_types: A list of block types to search.
        Returns:
            A filter for the query.
        """
        #doc_types = _parse_doc_types(doc_types) #arg is str,list or None
        #block_types = _parse_block_types(block_types)
        if field_filters:
            block_types = field_filters.block_types
        else:
            block_types = []

        _filter = Filter(
            must=[
                Filter(
                    should= [
                        FieldCondition(
                            key="block_type",
                            match=MatchValue(value=bt),
                        )
                    for bt in block_types
                    ]  
                )
            ]
        )

        return _filter
    
    def query_index(self, query, query_vector, top_k=10, field_filters=None):
        #vector = embed_text(query)
       
        _filter = self._generate_query_filter(query, field_filters)
        
        results = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=_filter,
            limit=top_k,
            with_payload=True,
            #search_params=_search_params_mock, #TODO
        )

        results = [
            (
                f"{res.payload['text']}#{res.payload['start']}",
                res.score,
            )
            for res in results
        ]

        #results: (url, contents, score)*

        return results
    

def test_qd():
    '''local tests'''
    