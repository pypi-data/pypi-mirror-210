import unittest

from utils.vectors import (generate_ance_embeddings,
                           generate_minilmv2_embeddings,
                           generate_tct_colbert_embeddings)

test_passages = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
    "Proin non sapien feugiat, aliquet est ut, sollicitudin est",
    "Suspendisse et hendrerit est.",
    "Aliquam elementum neque at lacinia placerat. Duis iaculis congue viverra",
    "Nulla fermentum mi eget est bibendum, sed faucibus sapien semper.",
]


class TestVectors(unittest.TestCase):
    def test_tct_bert(self):
        vectors = generate_tct_colbert_embeddings(test_passages)

        print(vectors)

    def test_ance(self):
        vectors = generate_ance_embeddings(test_passages)

        print(vectors)

    def test_minilmv2(self):
        vectors = generate_minilmv2_embeddings(test_passages)

        print(vectors)
