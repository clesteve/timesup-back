import os
import redis
import json
from flask import Flask, session, request, jsonify, make_response
from dotenv import load_dotenv  # type: ignore

from game import Game

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET')
red = redis.StrictRedis()


def get_game(game_id: str) -> Game:
    resp = red.get(game_id.encode('utf-8'))
    if resp:
        game_dict = json.loads(resp.decode('utf-8'))
        game = Game()
        game.from_dict(game_dict)
        return game
    else:
        raise Exception(
            "Could not load game with id {} \n".format(game_id))


@app.route('/games')
def index():
    return jsonify({'games': [i.decode('utf-8') for i in red.scan_iter()]})


@app.route('/games', methods=['POST'])
def create_game_route():
    user = request.args['user']
    game = Game(users=[user])
    red.set(game.id, json.dumps(game.__dict__))
    return jsonify({'game': game.__dict__})


@app.route('/games/<id>', methods=['GET'])
def get_game_route(id):
    game = get_game(id)
    print(game)
    username = request.args['user']
    if username not in game.users:
        game.add_user(username)
    return jsonify({'game': game.__dict__})


@app.route('/games/<id>', methods=['POST'])
def update_game_route(id):
    """
    TODO
    """
    pass


@app.errorhandler(Exception)
def handleException(e):
    return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True)
