import math
import operator

import networkx as nx


def compute_cosine_similarity(query_vector_length, document_score_map, document_vector_lengths):
    try:
        # For every document, divide its current score by combined product of document length and query length
        # document length is the square root of the sum of squares of the weights associated with the document d
        # query length is the square root of the sum of squares of weights associated with the query q
        for document in document_score_map:
            existing_score = document_score_map.get(document)
            new_score = existing_score / (math.sqrt(document_vector_lengths[document]) * math.sqrt(query_vector_length))
            document_score_map.__setitem__(document, new_score)

    except Exception as e:
        print("Exception occurred", e)
        raise e


# Function that updates a dictionary with the given key and value
def update_document_score(document_id, score, dictionary):
    try:
        existing_score = dictionary.get(document_id, 0)
        dictionary.__setitem__(document_id, existing_score + score)
    except Exception as e:
        print("Exception occurred", e)
        raise e


# Function to get page rank scores for relevant documents returned from cosine similarity
def get_page_rank_scores(document_ids, url_page_ranks):
    try:
        result = dict()
        if url_page_ranks is None:
            return
        page_rank_results = dict()
        for document_ids in document_ids:
            page_rank_results[document_ids] = url_page_ranks[document_ids]

        result = dict(
            sorted(page_rank_results.items(), key=operator.itemgetter(1), reverse=True))
        return result
    except Exception as e:
        print("Exception occurred ", str(e))
        raise e


# Function to return the converged authority scores for the documents in expanded set
# HITS algorithm is using relevant documents from cosine similarity
def run_hits_algorithm(document_ids, code_url_map, url_object, url_code_map):
    try:
        initial_set = document_ids
        result = dict()
        if code_url_map is None:
            return result
        if url_object is None:
            return result
        if url_code_map is None:
            return result

        # expand root set by adding all pages in from link structure that is being pointed by every page in p
        G = nx.DiGraph()
        for document in initial_set:
            # get url from document id
            url = code_url_map[document]
            out_going_links = url_object[url]
            # For every outgoing link from current node, add them to root set graph
            for link in out_going_links:
                if link in url_code_map:
                    G.add_edge(document, url_code_map[link])

                    neighbor_outgoing_links = url_object[link]
                    if url in neighbor_outgoing_links:
                        G.add_edge(url_code_map[link], document)

        hubs, authorities = nx.hits(G)
        result = dict(
            sorted(authorities.items(), key=operator.itemgetter(1), reverse=True))
        return result
    except Exception as e:
        print("Exception occurred ", str(e))
        raise e
