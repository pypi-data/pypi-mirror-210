import enum
import os

NUM_THREADS = os.getenv("NUM_THREADS", "2")


class DenseIndexes(enum.Enum):
    ANCE = enum.auto()
    DISTILBERT = enum.auto()
    DPR = enum.auto()
    CONTRIEVER = enum.auto()
    TCT_COLBERT = enum.auto()


class SparseIndexes(enum.Enum):
    BM25 = enum.auto()  # no ML here
    UNICOIL = enum.auto()


def build_bm25_command(inp, out):
    return [
        "python",
        "-m",
        "pyserini.index.lucene",
        "--collection",
        "JsonCollection",
        "--input",
        inp,
        "--index",
        out,
        "--generator",
        "DefaultLuceneDocumentGenerator",
        "--threads",
        NUM_THREADS,
        "--storePositions",
        "--storeDocvectors",
        "--storeRaw",
    ]


def build_unicoil_command(inp, out):
    return [
        "python",
        "-m",
        "pyserini.encode",
        "input",
        "--corpus",
        inp,
        "--fields",
        "contents",
        "output",
        "--embeddings",
        out,
        "encoder",
        "--encoder",
        "castorini/unicoil-msmarco-passage",
        "--fields",
        "contents",
        "--batch",
        "32",
    ]


commands = {
    SparseIndexes.BM25: build_bm25_command,
    SparseIndexes.UNICOIL: build_unicoil_command
}
