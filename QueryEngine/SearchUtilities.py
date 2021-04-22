import math


def compute_cosine_similarity(query_vector_length, document_score_map, document_vector_lengths):
    # For every document, divide its current score by combined product of document length and query length
    # document length is the square root of the sum of squares of the weights associated with the document d
    # query length is the square root of the sum of squares of weights associated with the query q
    for document in document_score_map:
        existing_score = document_score_map.get(document)
        new_score = existing_score / (math.sqrt(document_vector_lengths[document]) * math.sqrt(query_vector_length))
        document_score_map.__setitem__(document, new_score)


# Function to compute the sum of squares of tf-idf for every term the document has from inverted index
def compute_document_length(inverted_index_map, total_documents_in_the_collection, document_vector_lengths):
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


# Function that updates a dictionary with the given key and value
def update_document_score(document_id, score, dictionary):
    existing_score = dictionary.get(document_id, 0)
    dictionary.__setitem__(document_id, existing_score + score)
