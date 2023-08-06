import argparse
import os

from .handlers import commands
from .utils.models import DenseIndexes, SparseIndexes


def parse_enum(value):
    try:
        return SparseIndexes[value]
    except KeyError:
        pass

    try:
        return DenseIndexes[value]
    except KeyError:
        pass

    raise argparse.ArgumentTypeError(f"Invalid tokenizer!: {value}")


def index_document(tokenizer_model, document_file, output_file) -> None:
    print(f"Indexing document using tokenizer model: {tokenizer_model}")
    print(f"Document file: {document_file}")

    if not os.path.exists(output_file):
        os.mkdir(output_file)

    cmd_builder = commands[tokenizer_model]
    cmd_builder(document_file, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Command-line application for indexing documents."
    )

    tokenizers = [it for it in SparseIndexes] + [it for it in DenseIndexes]

    parser.add_argument(
        "tokenizer_model",
        type=parse_enum,
        choices=tokenizers,
        help="Name of the tokenizer model",
    )
    parser.add_argument(
        "document_dir", type=str, help="Name of the file with the document to index"
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        type=str,
        help="Name of the output directory (optional)",
        default="output_indexes",
    )

    parser.add_argument(
        "-s", "--sparse", type=str, help="List all sparse methods available"
    )
    parser.add_argument(
        "-d", "--dense", type=str, help="List all dense tokenizers available"
    )

    args = parser.parse_args()

    if args.tokenizer_model and args.document_dir:
        index_document(args.tokenizer_model, args.document_dir, args.output_directory)


if __name__ == "__main__":
    main()
