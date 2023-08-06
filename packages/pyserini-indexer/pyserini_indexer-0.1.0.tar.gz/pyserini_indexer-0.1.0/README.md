# pyserini-indexer

Helper application for building index files that uses pyserini

### Prerequisites
* python 3.9 (pytorch + faiss are only working under this version unfortunaly ☹️ )
* CUDA support (pyserini requires CUDA for backend 😞)

Example usage
```python
python main.py UNICOIL in_index/out.jsonl -o unicoil
```