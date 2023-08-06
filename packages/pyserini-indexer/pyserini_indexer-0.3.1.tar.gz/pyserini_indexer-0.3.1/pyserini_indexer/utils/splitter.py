"""
This file includes a simple heuristic-based splitter. 

Splitter is a program that "splits" long human generated 
text into smaller chunks. Machine learning models used for indexing
have limited input for example 256 "words". To fit very long text, for example a
book you need to split it so that it could be provided to the model.


Those generated text chunks are also called "passages".

The models I am talking about are called also "encoder models".

The output of those models are called dense indexes (dense because they in
theory should contain the semantic meaning of whole text 
and not some arbitrary features)
"""
import itertools
import re


def interlace_strings(array: list[str], joints: list[str]) -> str:
    assert len(array) == len(joints) + 1, "All joins should match"

    return "".join(
        itertools.islice(
            itertools.chain.from_iterable(itertools.zip_longest(array, joints)),
            None,
            len(array) + len(joints),
        )
    )


def redundant_splitter(
    text: str, /, max_characters: int = 512, max_sentences: int = 3
) -> list[str]:
    pattern = "(\. )|(\n{2,})"

    splitted = re.split(pattern, text)[::3]
    joints = [it[0] for it in re.finditer(pattern, text)]

    passages = []

    for idx, sentence in enumerate(splitted):
        current_passage = sentence[:max_characters]

        for inner_idx, end_sent in enumerate(splitted[idx + 1 :]):
            if inner_idx + 1 > max_sentences:
                break

            next_chunk = joints[idx + inner_idx] + end_sent

            if len(current_passage) + len(next_chunk) >= max_characters:
                break

            current_passage += next_chunk

        passages.append(current_passage)

    return passages
