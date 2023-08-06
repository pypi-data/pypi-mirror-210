import os

from pyserini.encode import (AnceDocumentEncoder, AutoDocumentEncoder,
                             TctColBertDocumentEncoder)

from .models import ANCE_MODEL, AUTO_MODEL, TCT_BERT_MODEL

USE_GPU = os.getenv("USE_GPU", None)

device = "cuda:0" if USE_GPU else "cpu"


def generate_tct_colbert_embeddings(texts: list[str]):
    encoder = TctColBertDocumentEncoder(TCT_BERT_MODEL, device=device)

    return encoder.encode(texts)


def generate_ance_embeddings(texts: list[str]):
    encoder = AnceDocumentEncoder(ANCE_MODEL, device=device)

    return encoder.encode(texts)


def generate_minilmv2_embeddings(texts: list[str]):
    encoder = AutoDocumentEncoder(AUTO_MODEL, device=device)

    return encoder.encode(texts)
