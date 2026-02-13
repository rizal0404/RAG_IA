from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss


class FaissStore:
    def __init__(self, index_path: str, dim: int):
        self.index_path = Path(index_path)
        self.dim = dim
        self.index = self._load_index()

    def _load_index(self) -> faiss.Index:
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        return faiss.IndexFlatL2(self.dim)

    def save(self) -> None:
        faiss.write_index(self.index, str(self.index_path))

    def add(self, embeddings: List[List[float]]) -> List[int]:
        vecs = np.array(embeddings).astype("float32")
        start_id = self.index.ntotal
        self.index.add(vecs)
        ids = list(range(start_id, start_id + vecs.shape[0]))
        self.save()
        return ids

    def search(self, embedding: List[float], k: int) -> Tuple[List[int], List[float]]:
        if self.index.ntotal == 0:
            return [], []
        vec = np.array([embedding]).astype("float32")
        distances, indices = self.index.search(vec, k)
        idxs = indices[0].tolist()
        dists = distances[0].tolist()
        filtered = [(i, d) for i, d in zip(idxs, dists) if i != -1]
        if not filtered:
            return [], []
        ids, dist = zip(*filtered)
        return list(ids), list(dist)

