"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""


# Represents a posting list of documents used for inverted index
class InvertedIndex:
    inverted_index: list[dict] = list()
    document_frequency: int = 0

    def __init__(self):
        self.inverted_index = list()
        self.document_frequency = 0

    # Add a document entry of {doc_id, term frequency} to inverted index
    def add_document(self, document: dict):
        self.inverted_index.append(document)
        self.document_frequency = self.document_frequency + 1
