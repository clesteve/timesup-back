import os
import redis
import json
from flask import Flask, session, request, jsonify, make_response, Response
from flask_cors import CORS  # type: ignore
from dotenv import load_dotenv  # type: ignore
from datetime import datetime
from random import shuffle
from uuid import uuid4


from game import Game

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET')
red = redis.StrictRedis()


def event_stream(game_id):
    pubsub = red.pubsub()
    pubsub.subscribe(game_id.encode('utf-8'))
    event = pubsub.get_message()
    for message in pubsub.listen():
        if message['type'] == 'message':
            yield 'data: %s\n\n' % message['data'].decode('utf-8')


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
    # type: ignore
    return jsonify({'games': [i.decode('utf-8') for i in red.scan_iter()]})


@app.route('/games', methods=['POST'])
def create_game_route():
    user = request.args['username']
    game = Game(users=[user], admin=request.args['username'])
    red.set(game.id, game.toJSON())
    return jsonify({'gameId': game.id})


@app.route('/games/<id>', methods=['GET'])
def get_game_route(id):
    game = get_game(id)
    username = request.args['username']
    if username not in game.users:
        game.add_user(username)
        red.set(id, game.toJSON())
        red.publish(id, game.visibleToJSON())
    return jsonify({'game': game.visibleToJSON()})


@app.route('/quit/<id>', methods=['GET'])
def quit_game(id):
    game = get_game(id)
    username = request.args['username']
    if username in game.users:
        game.users.remove(username)
        red.set(id, game.toJSON())
        red.publish(id, game.visibleToJSON())
    if len(game.users) == 0:
        red.delete(id)
    return jsonify({'deconnected': True})


@app.route('/characters/<id>', methods=['POST'])
def update_game_route(id):
    game = get_game(id)
    username = request.json['username']

    if 'characters' in request.json:
        for c in request.json['characters']:
            cid = str(uuid4())
            game.characters[cid] = {
                'id': cid, 'name': c, 'submitted': username, 'discovered': ['', '', '']}

    if username not in game.submitted:
        game.submitted.append(username)

    game.make_discover_list()

    red.set(game.id, game.toJSON())
    red.publish(id, game.visibleToJSON())

    return jsonify({'acknowledged': True})


@app.route('/round/<id>')
def next_round(id):
    game = get_game(id)
    game.round += 1
    red.set(game.id, game.toJSON())
    red.publish(id, game.visibleToJSON())
    return jsonify({'success': True})


@app.route('/stream/<id>', methods=['GET'])
def get_stream_route(id):
    return Response(event_stream(id),
                    mimetype="text/event-stream")


@app.route('/teams/<id>', methods=['GET'])
def generateTeams(id):
    game = get_game(id)
    if len(game.users) < 4:
        raise Exception("Impossible to play with less than 4 players")
    if len(game.users) % 2:
        raise Exception("Impossible to play with an odd number of players")

    shuffle(game.users)
    game.teams = [[game.users[i], game.users[i +
                                             int(len(game.users)/2)]] for i in range(int(len(game.users)/2))]

    red.set(game.id, game.toJSON())
    red.publish(id, game.visibleToJSON())
    return jsonify({'success': True})


@app.route('/chrono/<id>')
def start_chrono(id):
    game = get_game(id)
    game.start_chrono()
    red.set(game.id, game.toJSON())
    red.publish(id, game.visibleToJSON())
    return jsonify({'success': True, 'character': game.characters[game.to_discover[0]]})


@app.route('/player/<id>')
def next_player(id):
    game = get_game(id)
    game.next_user()
    red.set(game.id, game.toJSON())
    red.publish(id, game.visibleToJSON())
    return jsonify({'success': True, 'user': game.current_user})


@app.route('/discovered/<id>')
def character_discovered(id):
    game = get_game(id)
    game.discover(request.args['character'], request.args['username'])
    if len(game.to_discover):
        next_character = game.characters[game.to_discover[0]]
        red.set(game.id, game.toJSON())
        red.publish(id, game.visibleToJSON())
        return jsonify({'succes': True, 'character': next_character, 'end': False})
    elif game.round < 2:
        game.round += 1
        game.make_discover_list()
        next_character = game.characters[game.to_discover[0]]
        game.next_user()
        red.set(game.id, game.toJSON())
        red.publish(id, game.visibleToJSON())
        return jsonify({'succes': True, 'character': next_character, 'end': False})
    else:
        game.end = True
        red.set(game.id, game.toJSON())
        red.publish(id, game.visibleToJSON())
        return jsonify({'succes': True, 'character': {}, 'end': True})


@app.route('/pass/<id>')
def pass_card(id):
    game = get_game(id)
    to_pass = game.to_discover[0]
    game.to_discover.pop(0)
    game.to_discover.append(to_pass)
    red.set(game.id, game.toJSON())
    return jsonify({'character': game.characters[game.to_discover[0]]})


@app.route('/results/<id>')
def getResults(id):
    game = get_game(id)
    return jsonify({'game': game.toJSON()})


@app.route('/character/<id>')
def getCharacter(id):
    game = get_game(id)
    return jsonify({'character': game.characters[game.to_discover[0]]})


@app.errorhandler(Exception)
def handleException(e):
    return make_response(jsonify({'message': str(e)}), 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
