"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import math
import operator
import os
import sys

import numpy as np

from InvertedIndex import InvertedIndex
from preprocessing.preprocessor import (
    Pipeline,
    CaseConverter,
    StopWordRemoval,
    Tokenizer,
    RemovePunctuationHandler,
    PorterStemmerHandler,
    RemoveNumbersHandler,
    RemoveWordsHandler)

# a unique identifier to assign to a document
unique_document_id = 1
inverted_index_map = dict()
total_documents_in_the_collection = 0
document_score_map = dict()
document_vector_lengths = dict()


# Function to get the list of files from a directory
def get_files_from_directory(path: str):
    global total_documents_in_the_collection
    try:
        for root, dirs, files in os.walk(path):
            total_documents_in_the_collection = len(files)
            return files
    except Exception as e:
        raise e


# Function to read every file in dataset, tokenize the content, perform stemming and stopwords
# elimination if required
def process_files(files):
    try:
        global unique_document_id
        unique_document_id = 1
        pipeline = Pipeline()
        # Add preprocessing steps as a pipeline step. The output of each step goes to the next step
        pipeline.add_step(CaseConverter())
        pipeline.add_step(Tokenizer())
        pipeline.add_step(StopWordRemoval())
        pipeline.add_step(PorterStemmerHandler())
        # check for stop words again to make sure stemmer does not introduce a stop word
        pipeline.add_step(StopWordRemoval())
        pipeline.add_step(RemovePunctuationHandler())
        pipeline.add_step(RemoveNumbersHandler())
        pipeline.add_step(RemoveWordsHandler())

        for file in files:
            document = ""
            with open(os.path.join(dataset_path, file)) as handle:
                document = handle.read()

            pipeline.set_initial_data(document)
            # Execute the pipeline with stages defined above that does preprocessing
            pipeline.execute()
            result = pipeline.get_result()
            word_count_map = dict()

            # Create a map to store count of term frequency for every word in document d
            for word in result:
                existing_count = word_count_map.get(word, 0)
                existing_count = existing_count + 1
                word_count_map.__setitem__(word, existing_count)

            # For every unique word in map, insert an appropriate entry in inverted index
            # The key is the word and the value is a map object of document id and term frequency
            for key in word_count_map:
                inverted_index: InvertedIndex = inverted_index_map.get(key, InvertedIndex())
                # get existing object
                document_object = dict()
                document_object["document_id"] = unique_document_id
                document_object["term_frequency"] = word_count_map[key]
                inverted_index.add_document(document_object)
                inverted_index_map.__setitem__(key, inverted_index)

            # Increment the variable to keep track of documents that are processed for analysis purposes
            unique_document_id += 1

    except Exception as e:
        raise e


def read_queries(query_path):
    try:
        with open(query_path) as handle:
            return handle.read().split("\n")
    except Exception as e:
        raise e


# Function that updates a dictionary with the given key and value
def update_document_score(document_id, score, dictionary):
    existing_score = dictionary.get(document_id, 0)
    dictionary.__setitem__(document_id, existing_score + score)


def compute_cosine_similarity(query_vector_length):
    global document_score_map
    # For every document, divide its current score by combined product of document length and query length
    # document length is the square root of the sum of squares of the weights associated with the document d
    # query length is the square root of the sum of squares of weights associated with the query q
    for document in document_score_map:
        existing_score = document_score_map.get(document)
        new_score = existing_score / (math.sqrt(document_vector_lengths[document]) * math.sqrt(query_vector_length))
        document_score_map.__setitem__(document, new_score)


# Function that reads queries, does preprocessing and fetches relevant documents
def process_queries(queries):
    from collections import Counter
    import math
    global document_score_map
    pipeline = Pipeline()
    pipeline.add_step(CaseConverter())
    pipeline.add_step(Tokenizer())
    pipeline.add_step(StopWordRemoval())
    pipeline.add_step(PorterStemmerHandler())
    pipeline.add_step(StopWordRemoval())
    pipeline.add_step(RemovePunctuationHandler())
    pipeline.add_step(RemoveNumbersHandler())
    pipeline.add_step(RemoveWordsHandler())
    query_terms = list()
    for index, query in enumerate(queries):
        pipeline.set_initial_data(query)
        pipeline.execute()
        result = pipeline.get_result()
        query_terms = Counter(result)
        query_vector_length = 0
        document_score_map.clear()

        for term in query_terms:
            # find relevant documents from inverted index for the current query term
            inverted_index_object = inverted_index_map.get(term, None)
            # If a term is not present in inverted index, it is of no use for retrieval
            if inverted_index_object is None:
                continue
            # Get the document frequency for the current query term
            document_frequency = inverted_index_object.document_frequency
            inverse_document_frequency = math.log2(total_documents_in_the_collection / document_frequency)
            # TF-IDF is the product of TF  * IDF
            query_tf_idf = query_terms[term] * inverse_document_frequency
            # add the square of tf-idf to the global variable to keep track of query length
            query_vector_length = query_vector_length + math.pow(query_tf_idf, 2)
            # for every document containing the current query term, calculate tf-idf
            for document in inverted_index_object.inverted_index:
                # calculate tf-idf for the current query term
                term_occurrence = document["term_frequency"]
                tf_idf_document = term_occurrence * inverse_document_frequency
                numerator_of_cosine_similarity = tf_idf_document * query_tf_idf
                # Keep accumulating the numerator part of cosine similarity for the corresponding document d
                update_document_score(document["document_id"], numerator_of_cosine_similarity, document_score_map)

        compute_cosine_similarity(query_vector_length)
        # get_relevant_documents(index + 1)


# Function to compute the sum of squares of tf-idf for every term the document has from inverted index
def compute_document_length():
    for word in inverted_index_map:
        # object that contains the document frequency property and list of documents along with term frequency
        inverted_index_object = inverted_index_map.get(word, None)
        if inverted_index_object is None:
            continue
        # Document frequency for word
        document_frequency = inverted_index_object.document_frequency
        # IDF is log2 (N / DFi )
        inverse_document_frequency = math.log2(total_documents_in_the_collection / document_frequency)
        documents = inverted_index_object.inverted_index
        for document in documents:
            # Get the Term Frequency for the current word from the document d
            term_frequency = document['term_frequency']
            # TF-IDF for document d for the current word is the product of Term frequency and IDF
            document_tf_idf = term_frequency * inverse_document_frequency
            new_score = math.pow(document_tf_idf, 2)
            # Update the document d with the calculated square of tf-idf for the current word
            update_document_score(document['document_id'], new_score, document_vector_lengths)


class Preprocessor:
    dataset_path = None
    inverted_index_map = None
    queries = None

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.inverted_index_map = dict()
        self.queries = read_queries()

    def start_process(self):
        files = get_files_from_directory(dataset_path)
        if len(files == 0):
            raise Exception("Files not present in given path {}".format(dataset_path))
        process_files(files, inverted_index_map)

    def get_processed_data(self):
        return self.inverted_index_map


class QueryEngine:
    queries = None
    query_path = list()

    def __init__(self, path):
        self.queries = read_queries()
        self.query_path = path

    def read_queries(self):
        global queries
        try:
            with open(self.query_path) as handle:
                queries = handle.read().split("\n")
        except Exception as e:
            raise e

    def execute_queries(self):
        process_queries(self.queries)


def main():
    global dataset_path
    try:
        dataset_path = input("Type the dataset absolute directory path of and hit enter key\n")
        if dataset_path == "":
            print("No value given for dataset path")
            sys.exit()
        files = get_files_from_directory(dataset_path)
        if len(files) == 0:
            print(f"No files present in the directory `${dataset_path}`")
            sys.exit()

        process_files(files)
        compute_document_length()
        read_queries()
        read_relevant_documents()
        process_queries()
        get_average_precision()
        get_average_recall()

    except Exception as e:
        print("Error " + str(e))
