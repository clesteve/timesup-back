from uuid import uuid4
from typing import List
from datetime import datetime
import json
from random import shuffle


class Character():
    """
    """

    def __init__(self, name: str, submitted: str, discovered=""):
        self.name = name
        self.discovered = discovered
        self.submitted = submitted


class Game():
    """
    Represents a game

    Attributes
    ----------
    id : str
        The generated uuid of the game
    users : List[str]
        The players in this game
    teams : List[Teams]
        List of teams in the game
    characters : List[dict]
    round : Current game round 

    Methods
    -------
    add_user(username : str)
        Add a player to the player list
    """

    def __init__(self, id=str(uuid4()), users=[], characters: dict = {}, teams: List[List[str]] = [], round=-1, admin="", submitted=[]):
        self.id = id
        self.users = users
        self.characters = characters
        self.submitted = submitted
        self.teams = teams
        self.round = round
        self.current_user = 0
        self.chrono = {'started': False, 'begin': datetime.now().isoformat()}
        self.admin = admin
        self.to_discover: list = []
        self.end = False

    def make_discover_list(self):
        self.to_discover = list(self.characters.keys())
        shuffle(self.to_discover)

    def from_dict(self, game_dict: dict):
        self.id = game_dict['id']
        self.users = game_dict['users']
        self.characters = game_dict['characters']
        self.submitted = game_dict['submitted']
        self.teams = game_dict['teams']
        self.current_user = game_dict['current_user']
        self.chrono = game_dict['chrono']
        self.round = game_dict['round']
        self.admin = game_dict['admin']
        self.to_discover = game_dict['to_discover']
        self.end = game_dict['end']

    def add_user(self, username: str):
        if username not in self.users:
            self.users.append(username)
        else:
            raise Exception(
                "Already a user with name {} in this game".format(username))

    def next_user(self):
        self.current_user = (self.current_user + 1) % len(self.users)
        self.chrono = {'started': False, 'begin': datetime.now().isoformat()}

    def start_chrono(self):
        self.chrono = {'started': True,
                       'begin': datetime.now().isoformat()}  # type: ignore

    def discover(self, character, username):
        self.to_discover.remove(character)
        self.characters[character]['discovered'][self.round] = username

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return json.dumps(self.__dict__)

    def toJSON(self):
        game_dict = self.__dict__
        return json.dumps(game_dict)

    def visibleToJSON(self):
        to_send = {
            'users': self.users,
            'teams': self.teams,
            'round': self.round,
            'current_user': self.current_user,
            'chrono': self.chrono,
            'admin': self.admin,
            'submitted': self.submitted,
            'end': self.end
        }
        return json.dumps(to_send)
