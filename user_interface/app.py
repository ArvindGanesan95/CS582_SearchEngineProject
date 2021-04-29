from flask import Flask, request, abort

from QueryEngine import QEngine as qe

app = Flask(__name__, static_folder='public', static_url_path='')


@app.route('/processQuery', methods=['POST'])
def process_query():
    try:
        request_body = request.json
        search_string = request_body['searchString']
        ranking_algorithm = request_body['rankingAlgorithm']
        query_engine = qe.QueryEngine()
        pages = query_engine.process_query(search_string, ranking_algorithm)
        return str(pages)

    except Exception as e:
        print("Error in Process Query : " + str(e))
        abort(500, str(e))


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)
