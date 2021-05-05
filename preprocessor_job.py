"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""

import pickle

from Preprocessor.helper import (Preprocessor,
                                 total_documents_in_the_collection,
                                 inverted_index_map,
                                 document_vector_lengths,
                                 compute_page_rank
                                 )
from Utilities.Globals import file_contents_path, inverted_index_directory_path

if __name__ == '__main__':
    try:
        p = Preprocessor(file_contents_path)
        total_documents_in_the_collection = p.start_process()

        inverted_index_information = dict()
        inverted_index_information['total_docs'] = total_documents_in_the_collection
        inverted_index_information['inverted_index'] = inverted_index_map
        inverted_index_information["document_vector_lengths"] = document_vector_lengths
        print("Total documents in collection {}".format(total_documents_in_the_collection))
        # write inverted index to file system in a serialized form
        pickle.dump(inverted_index_information, open(inverted_index_directory_path, "wb"))
        # pickle_file = open(inverted_index_directory_path)
        # obj = pickle.load(pickle_file)
        compute_page_rank()

    except Exception as e:
        print("Exception occurred", "\n", e)

