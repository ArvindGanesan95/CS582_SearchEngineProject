# SpidySearch

A search engine is developed that allows the user to search the uic domain starting from the url  https://www.cs.uic.edu/ . This code is part of the final project of CS-582 Information Retrieval Course at UIC. The engine uses vector space model and uses TF-IDF and Cosine Similarity as the weighing and similarity measures.

The search engine also includes two intelligent components which allows the user to apply PageRank or HITS algorithm along with Cosine Similarity.


# System Requirements
A windows or Linux machine (Ubuntu) can be used with at least 4 GB ram. 
**Note** : The program was tested on Windows 10 Home edition and Ubuntu 20.04.2 LTS
The link to the Ubuntu distribution is  : https://ubuntu.com/download/desktop
## Software Requirements
- PyCharm 2020.3 (For development purposes in an IDE)
- Python 3.9.1 . Make sure that PIP is installed and environment path of pip and python  is set. If 'pip' is not found in ubuntu, it could be installed from https://linuxize.com/post/how-to-install-pip-on-ubuntu-20.04/. Python 3.9 and above can be installed from https://linuxize.com/post/how-to-install-python-3-9-on-ubuntu-20-04/

## Python Modules Required

The modules given below are required to run the program. The modules and the pip install commands are given below. These modules are also present in the file called requirements.txt 

	- beautifulsoup4==4.9.3  : pip install beautifulsoup4==4.9.3
	- fastcounter==1.0.1  : pip install fastcounter==1.0.1
	- Flask==1.1.2   : pip install Flask==1.1.2
	- networkx==2.5.1  : pip install networkx==2.5.1
	- nltk==3.6.2  : pip install nltk==3.6.2
	- requests==2.25.1  : pip install requests==2.25.1
	- urllib3==1.26.4 : pip install urllib3==1.26.4
	- numpy : pip install numpy==1.20.2
	
# Running the program

There are 3 major modules in the source code: Web Crawler, Preprocessor and UI.



## To Run Search Engine :

Flask server is used to render the UI using HTML/CSS. The user query is fetched and is passed to the query engine which brings the relevant documents. The file called "app.py" can be used to launch the server and render the ui. By default, **port 8081** is used. If the port is already in use , change it to a unused port number.

> python app.py

This launches the server process. Go to localhost:8081 port in the browser and play with the search engine.

## To Run Web Crawler : 
There is a file called "crawler_job.py" (in the root directory), which is like a wrapper for WebCrawler.py file(inside Crawler directory). Run the file using the command given below without quotes. 
> python crawler_job.py 

The crawler accepts the following parameters : 
- **root_url** : the start url of crawler. Here it is https://www.cs.uic.edu/ 
- **base_url** : the domain that the crawled urls must be confined to. Here it is "uic.edu"
- **pages_to_crawl** : By default, it is set to 3000. It can be overridden to user specified value. The crawler guarantees that #pages_to_crawl based are crawled. Due to multithreading the crawler may stop with some more files than specified. 
- **number_of_worker_threads**: Specifies number worker threads to run in parallel. Maximum limit is 20. By default, 20 worker threads are spawned

The crawler also creates an adjacency list representation of urls and its outgoing links to be used for PageRank and HITS algorithm computation

**Note** The Crawler takes around 15 minutes to download 3000 pages.


## To Run Preprocessor :
There is a file called "preprocessor_job.py" (in the root directory) , which acts as a wrapper for helper.py file(inside Preprocessor directory). Run the fiile using the command given below. 
> python preprocessor_job.py

The file calls preprocessor to perform the following operations : Convert text to Lower Case, Tokenize text using whitespace, Remove Stop Words, Use Porter Stemmer to stem the words.

Then, the file creates an inverted index, computes page rank scores for the collection using inverted index and writes them to "Computations" folder

**Note** The Preprocessor takes around 10 minutes to finish processing

**Note** The processesed data of Crawler and Preprocessor is already present in this repository inside Computations folder. To save time, only the search engine can be run directly as described in earlier section.


# Results

The architecture, design and the results of evaluation of the search engine could be found at the doc "ProjectReport.pdf"


