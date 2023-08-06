import enum
import os

TCT_BERT_MODEL = os.getenv("TCT_BERT_MODEL", "castorini/tct_colbert-v2-hnp-msmarco-r2")
ANCE_MODEL = os.getenv("ANCE_MODEL", "castorini/ance-msmarco-doc-maxp")
AUTO_MODEL = os.getenv("AUTO_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
UNICOIL_MODEL = os.getenv("AUTO_MODEL", "castorini/unicoil-msmarco-passage")


class DenseIndexes(enum.Enum):
    ANCE = enum.auto()
    TCT_COLBERT = enum.auto()
    MINILM_V2 = enum.auto()


class SparseIndexes(enum.Enum):
    BM25 = enum.auto()  # no ML here
    UNICOIL = enum.auto()
