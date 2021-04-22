"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import json
import math
import os
import sys
import pickle
from InvertedIndex import InvertedIndex
from QueryEngine import SearchUtilities
from preprocessor import (
    Pipeline,
    CaseConverter,
    StopWordRemoval,
    Tokenizer,
    PorterStemmerHandler, RemovePunctuationHandler, RemoveNumbersHandler)

# a unique identifier to assign to a document
unique_document_id = 1
inverted_index_map = dict()
total_documents_in_the_collection = 0
document_score_map = dict()
document_vector_lengths = dict()
inverted_index_directory_path = ''


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
        # pipeline.add_step(RemoveWordsHandler())

        for file in files:
            document = ""
            with open(os.path.join(parent_path, file)) as handle:

                document = json.loads(handle.read())["content"]

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

            # if len(inverted_index_map.keys()) > 10000:
            #     break
            # Increment the variable to keep track of documents that are processed for analysis purposes
            unique_document_id += 1
        compute_document_length()

    except Exception as er:
        raise er


# Function that updates a dictionary with the given key and value
def update_document_score(document_id, score, dictionary):
    existing_score = dictionary.get(document_id, 0)
    dictionary.__setitem__(document_id, existing_score + score)


#
# # Function that reads queries, does preprocessing and fetches relevant documents
# def process_queries(queries):
#     from collections import Counter
#     import math
#     global document_score_map
#     pipeline = Pipeline()
#     pipeline.add_step(CaseConverter())
#     pipeline.add_step(Tokenizer())
#     pipeline.add_step(StopWordRemoval())
#     pipeline.add_step(PorterStemmerHandler())
#     pipeline.add_step(StopWordRemoval())
#     # pipeline.add_step(RemovePunctuationHandler())
#     # pipeline.add_step(RemoveNumbersHandler())
#     # pipeline.add_step(RemoveWordsHandler())
#     query_terms = list()
#     for index, query in enumerate(queries):
#         pipeline.set_initial_data(query)
#         pipeline.execute()
#         result = pipeline.get_result()
#         query_terms = Counter(result)
#         query_vector_length = 0
#         document_score_map.clear()
#
#         for term in query_terms:
#             # find relevant documents from inverted index for the current query term
#             inverted_index_object = inverted_index_map.get(term, None)
#             # If a term is not present in inverted index, it is of no use for retrieval
#             if inverted_index_object is None:
#                 continue
#             # Get the document frequency for the current query term
#             document_frequency = inverted_index_object.document_frequency
#             inverse_document_frequency = math.log2(total_documents_in_the_collection / document_frequency)
#             # TF-IDF is the product of TF  * IDF
#             query_tf_idf = query_terms[term] * inverse_document_frequency
#             # add the square of tf-idf to the global variable to keep track of query length
#             query_vector_length = query_vector_length + math.pow(query_tf_idf, 2)
#             # for every document containing the current query term, calculate tf-idf
#             for document in inverted_index_object.inverted_index:
#                 # calculate tf-idf for the current query term
#                 term_occurrence = document["term_frequency"]
#                 tf_idf_document = term_occurrence * inverse_document_frequency
#                 numerator_of_cosine_similarity = tf_idf_document * query_tf_idf
#                 # Keep accumulating the numerator part of cosine similarity for the corresponding document d
#                 update_document_score(document["document_id"], numerator_of_cosine_similarity, document_score_map)
#
#         SearchUtilities.compute_cosine_similarity(query_vector_length, document_score_map)
#         # get_relevant_documents(index + 1)


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
        p = Preprocessor(r"E:\IR\Project\url_contents")
        p.start_process()

        inverted_index_information = dict()
        inverted_index_information['total_docs'] = total_documents_in_the_collection
        inverted_index_information['inverted_index'] = inverted_index_map
        inverted_index_information["document_vector_lengths"] = document_vector_lengths

        pickle.dump(inverted_index_information, open("inverted_index.p", "wb"))

        # inverted_index_information = pickle.load(open("inverted_index.p", "rb"))

    except Exception as e:
        print("Exception occurred", "\n", e)
