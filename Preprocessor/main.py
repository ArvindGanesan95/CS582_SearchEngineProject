"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import json
import math
import operator
import os
import pickle

import networkx as nx

from InvertedIndex import InvertedIndex
from preprocessor import (
    Pipeline,
    CaseConverter,
    StopWordRemoval,
    Tokenizer,
    PorterStemmerHandler, RemovePunctuationHandler, RemoveNumbersHandler)

inverted_index_map = dict()
total_documents_in_the_collection = 0
document_score_map = dict()
document_vector_lengths = dict()
inverted_index_directory_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', r'inverted_index.p')
link_structures_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', r'urlmaps.txt')
url_to_code_map_path = os.path.join(r'E:\IR\Project - Copy', 'Computations', 'url_code_map.json')
url_contents_path = os.path.join(r'E:\IR\Project - Copy', 'url_contents')
url_page_ranks_path = r'../Computations/url_page_ranks.txt'


def compute_page_rank():
    try:
        url_code_map = None
        with open(url_to_code_map_path) as handle:
            url_code_map = json.load(handle)

        if url_code_map is None:
            print("No url to code map found. Cannot run page rank")
            return
        url_outgoing_map = dict()
        with open(link_structures_path) as handle:
            url_outgoing_map = json.loads(handle.read())

        if url_outgoing_map is None:
            print("No url to outgoing links map found. Cannot run page rank")
            return

        G = nx.DiGraph()

        for url in url_outgoing_map.keys():

            url_id_source = url_code_map[url]
            links = url_outgoing_map[url]['links']
            for neighbor in links:
                if neighbor in url_code_map:
                    url_id_destination = url_code_map[neighbor]
                    G.add_edge(url_id_source, url_id_destination)

                    neighbor_outgoing_links = url_outgoing_map[neighbor]['links']
                    if url in neighbor_outgoing_links:
                        G.add_edge(url_id_destination, url_id_source)

        page_ranks = nx.pagerank(G)
        result = dict(
            sorted(page_ranks.items(), key=operator.itemgetter(1), reverse=True))

        with open(url_page_ranks_path, "w+") as handle:
            handle.write(json.dumps(result))

    except Exception as e:
        print("Exception occurred ", str(e))


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
def process_files(files, parent_path):
    try:
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
        # pipeline.add_step(RemoveWordsHandler())

        for file in files:
            document = ""
            with open(os.path.join(parent_path, file)) as handle:

                document = json.loads(handle.read())["content"]
            print("Processing file {}".format(file))
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
                document_object["document_id"] = file
                document_object["term_frequency"] = word_count_map[key]
                inverted_index.add_document(document_object)
                inverted_index_map.__setitem__(key, inverted_index)

        compute_document_length()

    except Exception as er:
        raise er


# Function that updates a dictionary with the given key and value
def update_document_score(document_id, score, dictionary):
    existing_score = dictionary.get(document_id, 0)
    dictionary.__setitem__(document_id, existing_score + score)


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

    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.inverted_index_map = dict()

    def start_process(self):
        files = get_files_from_directory(self.dataset_path)
        if len(files) == 0:
            raise Exception("Files not present in given path {}".format(self.dataset_path))
        process_files(files, self.dataset_path)
        return


if __name__ == '__main__':
    try:
        p = Preprocessor(url_contents_path)
        p.start_process()

        inverted_index_information = dict()
        inverted_index_information['total_docs'] = total_documents_in_the_collection
        inverted_index_information['inverted_index'] = inverted_index_map
        inverted_index_information["document_vector_lengths"] = document_vector_lengths

        # write inverted index to file system
        pickle.dump(inverted_index_information, open(inverted_index_directory_path, "wb"))

        compute_page_rank()

    except Exception as e:
        print("Exception occurred", "\n", e)
