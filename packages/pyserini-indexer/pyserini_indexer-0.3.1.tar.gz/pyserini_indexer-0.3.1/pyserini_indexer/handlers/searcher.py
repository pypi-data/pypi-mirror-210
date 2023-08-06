import functools
from typing import Optional

import pyserini.search.faiss as faiss
import pyserini.search.hybrid as hybrid
import pyserini.search.lucene as lucene

import pyserini_indexer.utils.models as models


@functools.lru_cache
def get_searcher(
    index_dir: str,
    *,
    dense_model: Optional[str] = None,
    sparse_model: Optional[str] = None,
    second_index_dir: Optional[str] = None,
):
    dense_searcher = None
    sparse_searcher = None

    if dense_model == models.DenseIndexes.ANCE.name:
        encoder = faiss.AnceQueryEncoder(models.ANCE_MODEL)
        dense_searcher = faiss.FaissSearcher(index_dir, encoder)
    elif dense_model == models.DenseIndexes.TCT_COLBERT.name:
        encoder = faiss.TctColBertQueryEncoder(models.TCT_BERT_MODEL)
        dense_searcher = faiss.FaissSearcher(index_dir, encoder)
    elif dense_model == models.DenseIndexes.MINILM_V2.name:
        encoder = faiss.AutoQueryEncoder(models.AUTO_MODEL)
        dense_searcher = faiss.FaissSearcher(index_dir, encoder)

    sparse_index_dir = second_index_dir or index_dir

    if sparse_model == models.SparseIndexes.BM25.name:
        sparse_searcher = lucene.LuceneSearcher(sparse_index_dir)
    elif sparse_model == models.SparseIndexes.UNICOIL.name:
        sparse_searcher = lucene.LuceneImpactSearcher(
            sparse_index_dir, models.UNICOIL_MODEL
        )

    if sparse_searcher and dense_searcher:
        return hybrid.HybridSearcher(dense_searcher, sparse_searcher)
    elif sparse_searcher:
        return sparse_searcher
    elif dense_searcher:
        return dense_searcher

    raise RuntimeError(
        "Unknown models: \nsparse{} \ndense{}".format(sparse_model, dense_model)
    )
