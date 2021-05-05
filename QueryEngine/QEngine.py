"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""

import json
import math
import operator
import pickle
from collections import Counter

from Preprocessor.preprocessor import (CaseConverter,
                                       Tokenizer,
                                       StopWordRemoval,
                                       PorterStemmerHandler,
                                       Pipeline, RemovePunctuationHandler, RemoveNumbersHandler
                                       )
from QueryEngine import SearchUtilities
from Utilities.Globals import (url_to_code_map_path,
                               code_to_url_map_path,
                               url_page_ranks_path,
                               inverted_index_directory_path as inverted_index_path,
                               link_structures_path as url_outgoing_links_map_path,
                               query_path

                               )


class QueryEngine:
    queries = None
    query_path = query_path
    document_score_map = dict()
    document_vector_lengths = dict()
    inverted_index_map = dict()
    total_documents_in_collection = 0
    url_code_map = None
    url_page_ranks_map = None
    url_outgoing_links_map = None
    code_url_map = None

    def __init__(self, path=None):

        self.document_score_map = dict()
        self.document_vector_lengths = dict()
        self.load_inverted_index()
        self.queries = self.read_queries(self.query_path)
        self.code_url_map = self.load_code_url_map()
        self.url_page_ranks = self.load_page_ranks()
        self.url_outgoing_links_map = self.load_url_outgoing_links_map()
        self.url_code_map = self.load_url_code_map()

    # Function to process a given query with an optional parameter of ranking algorithm
    def process_query(self, query, ranking_algorithm=None):

        try:
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

            result = self.document_score_map
            print("Ranks ", "\n", len(result.keys()))

            top_pages = result

            if len(result.keys()) > 0 and ranking_algorithm is not None:

                if ranking_algorithm == "pagerank":
                    page_rank_result = SearchUtilities.get_page_rank_scores(result.keys(), self.url_page_ranks)
                    # 2 * (cosine - score * pagerank) / (cosine - score + pagerank)
                    heuristic_1 = dict()
                    heuristic_2 = dict()
                    max_doc_score = max(top_pages.values())
                    # heuristic 1 performs linear addition using page rank multiplier constant
                    # heuristic_2 adds 25% to page rank and takes 50% from cosine similarity, if cosine similarity
                    # is a dominating factor ( >75% of page rank). If not, the values are added linearly
                    for page in page_rank_result:
                        heuristic_1[page] = max_doc_score + top_pages[page] + (page_rank_result[page] * 2)
                    for page in page_rank_result:
                        if page_rank_result[page] > 0:
                            percent_difference = (top_pages[page] - page_rank_result[page] /
                                                  page_rank_result[page]) * 100
                            if percent_difference > 75:
                                improved_page_rank = page_rank_result[page] + page_rank_result[page] * 0.25
                                heuristic_2[page] = top_pages[page] * 0.50 + improved_page_rank
                            else:
                                heuristic_2[page] = max_doc_score + top_pages[page] + page_rank_result[page] * 2
                        else:
                            heuristic_2[page] = max_doc_score + top_pages[page] + page_rank_result[page] * 2
                    # check which heuristic yielded better total ranking score of relevant documents
                    if sum(heuristic_1.values()) >= sum(heuristic_2.values()):
                        top_pages = heuristic_1
                    else:
                        top_pages = heuristic_2

                elif ranking_algorithm == "hits":
                    hits_result = SearchUtilities.run_hits_algorithm(result,
                                                                     self.code_url_map, self.url_outgoing_links_map,
                                                                     self.url_code_map)

                    heuristic_1 = dict()
                    heuristic_2 = dict()
                    try:
                        # for page in hits_result:
                        #     if page not in top_pages:
                        #         heuristic_1[page] = 0
                        #     else:
                        #         heuristic_1[page] = top_pages[page] + hits_result[page]

                        for page in hits_result:
                            if page not in top_pages:
                                heuristic_2[page] = 0
                            else:
                                if hits_result[page] > 0:
                                    percent_difference = (top_pages[page] - hits_result[page] /
                                                          hits_result[page]) * 100
                                    if percent_difference > 75:
                                        improved_hits_score = hits_result[page] + hits_result[page] * 0.25
                                        heuristic_2[page] = (top_pages[page] * 0.50) + improved_hits_score
                                    else:
                                        heuristic_2[page] = top_pages[page] + hits_result[page] * 5
                                else:
                                    heuristic_2[page] = top_pages[page] + hits_result[page] * 5

                        # check which heuristic yielded better total ranking score of relevant documents
                        if sum(heuristic_1.values()) >= sum(heuristic_2.values()):
                            top_pages = heuristic_1
                        else:
                            top_pages = heuristic_2

                    except Exception as e:
                        print("Exception", e)

            final_result = list()
            temp = dict(
                sorted(top_pages.items(), key=operator.itemgetter(1), reverse=True))
            for key in temp:
                final_result.append(self.code_url_map[key])

            return final_result

        except Exception as e:
            print("Exception occurred ", e)
            raise e

    # Function to read queries from a text file
    def read_queries(self, query_path):
        queries = []
        try:
            with open(query_path) as handle:
                queries = handle.read().split("\n")
            return queries
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

    # Function to load inverted index
    def load_inverted_index(self):
        try:
            inverted_index_information = pickle.load(open(inverted_index_path, "rb"))
            self.inverted_index_map = inverted_index_information['inverted_index']
            self.total_documents_in_collection = inverted_index_information['total_docs']
            self.document_vector_lengths = inverted_index_information["document_vector_lengths"]
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

    # Function to load uniqueID->url map
    def load_code_url_map(self):
        code_url_map = None
        try:
            with open(code_to_url_map_path) as handle:
                code_url_map = json.load(handle)
            return code_url_map
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

    # Function to load url->uniqueID map
    def load_url_code_map(self):
        url_code_map = None
        try:
            with open(url_to_code_map_path) as handle:
                url_code_map = json.load(handle)
            return url_code_map
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

    # Function to load page rank scores of the collection link structure
    def load_page_ranks(self):
        url_page_ranks = None
        try:
            with open(url_page_ranks_path) as handle:
                url_page_ranks = json.loads(handle.read())
            return url_page_ranks
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

    # Function to load the adjacency list representation of downloaded web pages
    def load_url_outgoing_links_map(self):
        url_links_map = None
        try:
            with open(url_outgoing_links_map_path) as handle:
                url_links_map = json.loads(handle.read())
            return url_links_map
        except Exception as e:
            print("Exception occurred", str(e))
            raise e

# q = QueryEngine()
# ranks = q.process_query("Compute")
