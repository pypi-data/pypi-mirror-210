# pyserini-indexer

Helper application for building index files that uses pyserini

### Prerequisites
* python 3.9 (pytorch + faiss are only working under this version unfortunaly ☹️ )
* if you would want to create/search using learnable 
Sparse indexes (UNICOIL), you would need CUDA support (pyserini requires here CUDA for backend 😞)

### Indexing methods:
* Sparse:
    * BM25 - traditional not-learnable indexing technique
    * UNICOIL - uses LuceneImpact underneath
* Dense:
    * MINILM_V2 - smallest model available
    * ANCE
    * TCT_COLBERT - biggest (0.5 gb) and provides best results

### Backend support
By default **all** indexing methods use CPU. If you would want to change this behaviour, set environment variable **USE_GPU** to some value.

Example usage
1. Create BM25 sparse index directory
```python
python pyserini-indexer BM25 index_input -o tests/indexes/bm25
```

2. Create dense index directory
```python
python pyserini-indexer MINILM_V2 index_input -o tests/indexes/minilm_v2
```
