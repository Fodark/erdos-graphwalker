from flask import Flask, request, jsonify
from lib.sherlock import search_author
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


@app.route('/')
def hello():
    return "Miao! Scrivi qualcosa!"

@app.route('/search')
def link():
    nome_cercato = request.args.get('name')
    logging.debug("APP: Searched for: {}".format(nome_cercato))
    prova_search_author = search_author(nome_cercato)

    return jsonify(prova_search_author)






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 


