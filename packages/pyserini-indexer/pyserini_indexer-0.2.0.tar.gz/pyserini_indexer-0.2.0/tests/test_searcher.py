import pathlib
import unittest

import utils.models as models
from handlers.searcher import get_searcher

index_dir = pathlib.Path("tests/indexes")

query = "What is ribosomal frameshifting?"
expected_id = "5dk231qs"


class TestSearcher(unittest.TestCase):
    def test_search_ance(self):
        searcher = get_searcher(index_dir / "ance", dense_model="ANCE")
        hits = searcher.search(query)

        self.assertEqual(hits[0].docid, expected_id)

    def test_search_minilmv2(self):
        searcher = get_searcher(index_dir / "minilm_v2", dense_model="MINILM_V2")
        hits = searcher.search(query)

        self.assertEqual(hits[0].docid, expected_id)

    def test_search_tct_colbert(self):
        searcher = get_searcher(index_dir / "tct_colbert", dense_model="TCT_COLBERT")
        hits = searcher.search(query)

        self.assertEqual(isinstance(hits[0].docid, str))

    def test_search_bm25(self):
        searcher = get_searcher(str(index_dir / "bm25"), sparse_model="BM25")
        hits = searcher.search(query)

        self.assertEqual(hits[0].docid, expected_id)

    def test_search_unicoil(self):
        searcher = get_searcher(str(index_dir / "unicoil"), sparse_model="UNICOIL")
        hits = searcher.search(query)

        self.assertEqual(hits[0].docid, expected_id)

    def test_hybrid_model(self):
        searcher = get_searcher(
            index_dir / "minilm_v2",
            sparse_model="BM25",
            dense_model="MINILM_V2",
            second_index_dir=str(index_dir / "bm25"),
        )
        hits = searcher.search(query)

        self.assertEqual(hits[0].docid, expected_id)
