from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from lib.sherlock import search_author, search_author_by_id
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def hello():
    return "Miao! Scrivi qualcosa!"

@app.route('/search')
@cross_origin()
def link():
    nome_cercato = request.args.get('name')
    logging.info("APP: Searched for: {}".format(nome_cercato))
    prova_search_author = search_author(nome_cercato)
    response = jsonify(prova_search_author)
    response.headers['Access-Control-Allow-Origin'] = 'react'
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, Access-Control-Allow-Origin')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response, prova_search_author['status_code']


@app.route('/author')
@cross_origin()
def get_author_by_id():
    id_cercato = request.args.get('id')
    logging.info("APP: Searched ID: {}".format(id_cercato))
    result = search_author_by_id(id_cercato)
    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 


