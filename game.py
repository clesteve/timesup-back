from uuid import uuid4
from typing import List
import json


class Character():
    """
    """

    def __init__(self, name: str, discovered=""):
        self.name = name
        self.discovered = discovered

    def is_discovered(self, by: str):
        self.discovered = by

    def __repr__(self):
        return self.__dict__

    def _str___(self):
        return self.__dict__


class Team():
    def __init__(self, users=[], id=str(uuid4())):
        self.users = users
        self.id = id

    def add_user(self, username):
        if username not in self.users:
            self.users.append(username)
        else:
            raise Exception(
                "Already a user with name {} in this team".format(username))


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
    characters : List[Character]
        A list of characters (cf class Character)
    round : Current game round 

    Methods
    -------
    add_user(username : str)
        Add a player to the player list
    """

    def __init__(self, id=str(uuid4()), users=[], characters: List[Character] = [], teams: List[Team] = [], round=1):
        self.id = id
        self.users = users
        self.characters = characters
        self.teams = teams
        self.round = round

    def from_dict(self, game_dict: dict):
        self.id = game_dict['id']
        self.users = game_dict['users']
        self.characters = [Character(c['name'], discovered=c['discovered'])
                           for c in game_dict['characters']]
        self.teams = [Team(users=t['users'], id=t['id'])
                      for t in game_dict['teams']]
        self.round = game_dict['round']

    def add_user(self, username: str):
        if username not in self.users:
            self.users.append(username)
        else:
            raise Exception(
                "Already a user with name {} in this game".format(username))

    def add_team(self, team: Team):
        if team not in self.teams:
            self.teams.append(team)
        else:
            raise Exception(
                "This team is already in the game")

    def __repr__(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.__dict__)
