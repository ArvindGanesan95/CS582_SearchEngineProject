import json
import math
import operator
import os
import pickle
from collections import Counter
from QueryEngine import SearchUtilities
from Preprocessor.preprocessor import (CaseConverter,
                                       Tokenizer,
                                       StopWordRemoval,
                                       PorterStemmerHandler,
                                       Pipeline, RemovePunctuationHandler, RemoveNumbersHandler
                                       )


class QueryEngine:
    queries = None
    query_path = os.path.join(r'E:\IR\Project - Copy', 'Utilities', 'queries.txt')
    document_score_map = dict()
    document_vector_lengths = dict()
    inverted_index_map = dict()
    total_documents_in_collection = 0
    url_code_map = None
    url_page_ranks_map = None
    url_outgoing_links_map = None
    url_code_map_path = r'../Computations/url_code_map.json'
    url_page_ranks_path = r'../Computations/url_page_ranks.txt'
    inverted_index_path = r'../Computations/inverted_index.p'
    url_outgoing_links_map_path = r'../Computations/urlmaps.txt'
    code_url_map_path = r'../Computations/code_to_url_map.json'
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

    def execute_queries(self):
        for query in self.queries:
            self.process_query(query)

    def get_queries(self):
        return self.queries

    def process_query(self, query, ranking_algorithm):

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
        print("Ranks ", "\n", result)

        top_pages = result

        if len(result.keys()) > 0 and ranking_algorithm is not None:

            if ranking_algorithm == "pagerank":
                page_rank_result = SearchUtilities.get_page_rank_scores(result, self.url_page_ranks)
                for page in page_rank_result:
                    top_pages[page] += page_rank_result[page]

            elif ranking_algorithm == "hits":
                hits_result = SearchUtilities.run_hits_algorithm(result,
                                                                 self.code_url_map, self.url_outgoing_links_map,
                                                                 self.url_code_map)
                try:
                    for page in hits_result:
                        if page not in top_pages:
                            top_pages[page] = 0
                        else:
                            top_pages[page] += hits_result[page]
                except Exception as e:
                    print("Exception", e)

        final_result = list()
        top_pages = dict(
            sorted(top_pages.items(), key=operator.itemgetter(1), reverse=True))
        for key in top_pages:
            final_result.append(self.code_url_map[key])

        return final_result

    def read_queries(self, query_path):
        queries = []
        try:
            with open(query_path) as handle:
                queries = handle.read().split("\n")
        except Exception as e:
            print("Exception occurred", str(e))
        finally:
            return queries

    def load_inverted_index(self):
        try:
            inverted_index_information = pickle.load(open(self.inverted_index_path, "rb"))
            self.inverted_index_map = inverted_index_information['inverted_index']
            self.total_documents_in_collection = inverted_index_information['total_docs']
            self.document_vector_lengths = inverted_index_information["document_vector_lengths"]
        except Exception as e:
            print("Exception occurred", str(e))

    def load_code_url_map(self):
        code_url_map = None
        try:
            with open(self.code_url_map_path) as handle:
                code_url_map = json.load(handle)
        except Exception as e:
            print("Exception occurred", str(e))
        finally:
            return code_url_map

    def load_url_code_map(self):
        url_code_map = None
        try:
            with open(self.url_code_map_path) as handle:
                url_code_map = json.load(handle)
        except Exception as e:
            print("Exception occurred", str(e))
        finally:
            return url_code_map

    def load_page_ranks(self):
        url_page_ranks = None
        try:
            with open(self.url_page_ranks_path) as handle:
                url_page_ranks = json.loads(handle.read())
        except Exception as e:
            print("Exception occurred", str(e))
        finally:
            return url_page_ranks

    def load_url_outgoing_links_map(self):
        url_links_map = None
        try:
            with open(self.url_outgoing_links_map_path) as handle:
                url_links_map = json.loads(handle.read())
        except Exception as e:
            print("Exception occurred", str(e))
        finally:
            return url_links_map

# q = QueryEngine()
# ranks = q.process_query("UIC courses")
