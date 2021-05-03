"""
Submitted by,
Arvind Ganesan
NETID: aganes25@uic.edu
"""
import os

project_path = r'./'
computations_path = os.path.join(project_path, 'Computations')
link_structures_path = os.path.join(project_path, 'Computations', r'urlmaps.txt')
url_to_code_map_path = os.path.join(project_path, 'Computations', 'url_code_map.json')
code_to_url_map_path = os.path.join(project_path, 'Computations', 'code_to_url_map.json')
url_maps_path = os.path.join(project_path, 'Computations', r'urlmaps.json')
file_contents_path = os.path.join(project_path, r'url_contents')
inverted_index_directory_path = os.path.join(project_path, 'Computations', r'inverted_index.p')
url_page_ranks_path = os.path.join(project_path, 'Computations', r'url_page_ranks.txt')
stop_words_file_path = os.path.join(os.getcwd(), 'Computations', r'url_page_ranks.txt')
query_path = os.path.join(project_path, 'QueryEngine', 'queries.txt')
