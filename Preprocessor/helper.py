"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import json
import math
import operator
import os

import networkx as nx

from InvertedIndex import InvertedIndex
from Preprocessor.preprocessor import (
    Pipeline,
    CaseConverter,
    StopWordRemoval,
    Tokenizer,
    PorterStemmerHandler,
    RemovePunctuationHandler,
    RemoveNumbersHandler,
)
from Utilities.Globals import (
    url_to_code_map_path,
    link_structures_path,
    url_page_ranks_path,
)

inverted_index_map = dict()
total_documents_in_the_collection = 0
document_score_map = dict()
document_vector_lengths = dict()


# Write a decorator function to handle exceptions. This makes adding try/catch clauses
# to be written in one place instead of adding them to each and every required position
def exception_handler(func):
    def exception_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except Exception as e:
            print(f"Exception in {func.__name__} :: ", e)
            raise e

    return exception_function


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

        # Create an instance of directed graph using NetworkX library
        G = nx.DiGraph()

        # For each of the url that acts as a parent node in the graph, get the outgoing links
        # ,get the unique id for each of outgoing link and parent node,  and add an edge between the
        # parent and outgoing link.
        for url in url_outgoing_map.keys():

            url_id_source = url_code_map[url]
            links = url_outgoing_map[url]
            for neighbor in links:
                if neighbor in url_code_map:
                    url_id_destination = url_code_map[neighbor]
                    G.add_edge(url_id_source, url_id_destination)

                    neighbor_outgoing_links = url_outgoing_map[neighbor]
                    # Check if there is an edge from outgoing link to parent link
                    if url in neighbor_outgoing_links:
                        G.add_edge(url_id_destination, url_id_source)
        # Compute page rank using NetworkX library
        page_ranks = nx.pagerank(G)
        result = dict(
            sorted(page_ranks.items(), key=operator.itemgetter(1), reverse=True)
        )

        # Write the results to file system
        with open(url_page_ranks_path, "w") as handle:
            handle.write(json.dumps(result))

    except Exception as e:
        print("Exception occurred ", str(e))
        raise e


# Function to get the list of files from a directory
def get_files_from_directory(path):
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
                document_object["document_id"] = file.split(".")[0]
                document_object["term_frequency"] = word_count_map[key]
                inverted_index.add_document(document_object)
                inverted_index_map.__setitem__(key, inverted_index)

        compute_document_length()

    except Exception as er:
        raise er


# Function that updates a dictionary with the given key and value
@exception_handler
def update_document_score(document_id, score, dictionary):
    existing_score = dictionary.get(document_id, 0)
    dictionary.__setitem__(document_id, existing_score + score)


@exception_handler
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

    @exception_handler
    def start_process(self):
        files = get_files_from_directory(self.dataset_path)
        if len(files) == 0:
            raise Exception("Files not present in given path {}".format(self.dataset_path))
        process_files(files, self.dataset_path)
        return total_documents_in_the_collection
