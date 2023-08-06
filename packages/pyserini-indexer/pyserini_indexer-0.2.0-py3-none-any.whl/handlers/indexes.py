import functools
import itertools
import json
import os
import subprocess
from typing import (  # we use python 3.9 so typings are bit outdated :/
    Callable, Dict, List, Union)

import faiss
import numpy as np
import tqdm

import utils.models as models
import utils.vectors as vectors
from utils.splitter import redundant_splitter

NUM_THREADS = os.getenv("NUM_THREADS", "2")


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
        models.UNICOIL_MODEL,
        "--fields",
        "contents",
        "--batch",
        "32",
    ]


def build_faiss_index(embeddings_fn, inp, out):
    faiss.omp_set_num_threads(int(NUM_THREADS))

    vectors_combined = []
    docid_filename = os.path.join(out, "docid")
    index_filename = os.path.join(out, "index")

    files = os.listdir(inp)

    with open(docid_filename, "w") as docid_file:
        for filename in files:
            with open(os.path.join(inp, filename), "r") as f:
                for line in tqdm.tqdm(f.readlines()):
                    json_line = json.loads(line)
                    splitted = redundant_splitter(json_line["contents"])
                    vectors = embeddings_fn(splitted)

                    docid = json_line["id"]

                    docid_file.write(
                        "".join(itertools.repeat(f"{docid}\n", vectors.shape[0]))
                    )

                    vectors_combined.append(vectors)

    vectors_combined = np.concatenate(vectors_combined)
    index = faiss.IndexFlatIP(vectors_combined.shape[1])
    index.add(vectors_combined)

    faiss.write_index(index, index_filename)


def build_command(command_builder_fn: Callable[[str, str], List[str]], inp, out):
    cmd = command_builder_fn(inp, out)

    print(f"COMMAND:\n {cmd}")
    print("=================\n")

    try:
        result = subprocess.check_output(cmd).decode()
    except subprocess.CalledProcessError as exc:
        result = f"Status : FAIL {exc.returncode} {exc.output}"

    print(result)


commands: Dict[
    Union[models.SparseIndexes, models.DenseIndexes], Callable[[str, str], None]
] = {
    models.SparseIndexes.BM25: functools.partial(build_command, build_bm25_command),
    models.SparseIndexes.UNICOIL: functools.partial(
        build_command, build_unicoil_command
    ),
    models.DenseIndexes.MINILM_V2: functools.partial(
        build_faiss_index, vectors.generate_minilmv2_embeddings
    ),
    models.DenseIndexes.TCT_COLBERT: functools.partial(
        build_faiss_index, vectors.generate_tct_colbert_embeddings
    ),
    models.DenseIndexes.ANCE: functools.partial(
        build_faiss_index, vectors.generate_ance_embeddings
    ),
}
