from flask import Flask, request, jsonify
from lib.sherlock import search_author, search_author_by_id
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/')
def hello():
    return "Miao! Scrivi qualcosa!"

@app.route('/search')
def link():
    nome_cercato = request.args.get('name')
    logging.info("APP: Searched for: {}".format(nome_cercato))
    prova_search_author = search_author(nome_cercato)

    return jsonify(prova_search_author)


@app.route('/author')
def get_author_by_id():
    id_cercato = request.args.get('id')
    logging.info("APP: Searched ID: {}".format(id_cercato))
    result = search_author_by_id(id_cercato)
    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 


