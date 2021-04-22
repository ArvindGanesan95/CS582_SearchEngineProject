import json
import math
import operator
from collections import Counter
import SearchUtilities
from Preprocessor.preprocessor import (CaseConverter,
                                       Tokenizer,
                                       StopWordRemoval,
                                       PorterStemmerHandler,
                                       Pipeline, RemovePunctuationHandler, RemoveNumbersHandler
                                       )


class QueryEngine:
    queries = None
    query_path = list()
    document_score_map = dict()
    document_vector_lengths = dict()
    inverted_index_map = dict()
    total_documents_in_collection = 0

    def __init__(self, path):
        self.query_path = path
        self.queries = self.read_queries(self.query_path)
        self.document_score_map = dict()
        self.document_vector_lengths = dict()
        self.load_inverted_index()

    def execute_queries(self):
        for query in self.queries:
            self.process_query(query)

    def get_queries(self):
        return self.queries

    def process_query(self, query):

        pipeline = Pipeline()
        pipeline.add_step(CaseConverter())
        pipeline.add_step(Tokenizer())
        pipeline.add_step(StopWordRemoval())
        pipeline.add_step(PorterStemmerHandler())
        pipeline.add_step(StopWordRemoval())
        pipeline.add_step(RemovePunctuationHandler())
        pipeline.add_step(RemoveNumbersHandler())

        pipeline.set_initial_data(query)
        pipeline.execute()
        result = pipeline.get_result()
        query_terms = Counter(result)
        query_vector_length = 0
        self.document_score_map.clear()

        for term in query_terms:
            # find relevant documents from inverted index for the current query term
            inverted_index_object = self.inverted_index_map.get(term, None)
            # If a term is not present in inverted index, it is of no use for retrieval
            if inverted_index_object is None:
                continue
            # Get the document frequency for the current query term
            document_frequency = inverted_index_object.document_frequency
            inverse_document_frequency = math.log2(self.total_documents_in_collection / document_frequency)
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
                SearchUtilities.update_document_score(document["document_id"], numerator_of_cosine_similarity,
                                                      self.document_score_map)

        SearchUtilities.compute_cosine_similarity(query_vector_length,
                                                  self.document_score_map, self.document_vector_lengths)
        # Sort the cosine similarity values in decreasing order
        result = dict(
            sorted(self.document_score_map.items(), key=operator.itemgetter(1), reverse=True))

        print("Ranks ", "\n", result)

    def read_queries(self, query_path):
        try:
            with open(query_path) as handle:
                self.queries = handle.read().split("\n")
        except Exception as e:
            raise e

    def load_inverted_index(self):

        with open(r'E:\IR\Project - Copy\Preprocessor\inverted_index.txt') as handle:
            inverted_index_information = json.load(handle)
            self.inverted_index_map = inverted_index_information['inverted_index']
            self.total_documents_in_collection = inverted_index_information['total_docs']
            self.document_vector_lengths = inverted_index_information["document_vector_lengths"]
