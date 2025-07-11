import numpy as np
import faiss

class VectorStoreMemory:
    def __init__(self, dim=128):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []
        self.vector_dim = dim

    def ingest(self, config):
        vectors = config.get("embedding") or config.get("vectors")
        if isinstance(vectors, list) and vectors and isinstance(vectors[0], dict) and "vector" in vectors[0]:
            for vobj in vectors:
                embedding = np.array(vobj["vector"], dtype=np.float32).reshape(1, -1)
                if embedding.shape[1] == self.vector_dim:
                    self.index.add(embedding)
        elif isinstance(vectors, list) and all(isinstance(x, (float, int)) for x in vectors):
            embedding = np.array(vectors, dtype=np.float32).reshape(1, -1)
            if embedding.shape[1] == self.vector_dim:
                self.index.add(embedding)
