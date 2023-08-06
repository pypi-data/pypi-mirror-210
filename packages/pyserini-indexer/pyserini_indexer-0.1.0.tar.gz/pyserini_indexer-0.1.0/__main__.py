import argparse
import os
import subprocess

import indexes


def parse_enum(value):
    try:
        return indexes.SparseIndexes[value]
    except ValueError:
        pass

    try:
        return indexes.DenseIndexes[value]
    except ValueError:
        pass

    raise argparse.ArgumentTypeError(f"Invalid tokenizer!: {value}")


def index_document(tokenizer_model, document_file, output_file):
    # Your indexing logic goes here
    # Use the provided tokenizer model and document file to index the document
    # Save the indexed document to the output file if provided
    print(f"Indexing document using tokenizer model: {tokenizer_model}")
    print(f"Document file: {document_file}")

    if not os.path.exists(output_file):
        os.mkdir(output_file)

    cmd_builder = indexes.commands[tokenizer_model]
    cmd = cmd_builder(document_file, output_file)

    print(f"COMMAND:\n {cmd}")
    print("=================\n")

    try:
        result = subprocess.check_output(cmd).decode()
    except subprocess.CalledProcessError as exc:
        result = f"Status : FAIL {exc.returncode} {exc.output}"

    print(result)


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Command-line application for indexing documents."
    )

    tokenizers = [it for it in indexes.SparseIndexes] + [
        it for it in indexes.DenseIndexes
    ]

    # Add the command line arguments
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

    # Parse the command line arguments
    args = parser.parse_args()

    # Call the index_document function with the provided arguments
    if args.tokenizer_model and args.document_dir:
        index_document(args.tokenizer_model, args.document_dir, args.output_directory)


if __name__ == "__main__":
    main()
