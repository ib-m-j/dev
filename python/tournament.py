class Deal:
    def __init__(self, id, dealer, zone):
        self.id = id    #created by define tournament
        self.dealer = dealer
        self.zone = ''  #created by define tournament
        self.cards = [] #list of hands SWNE
        self.plays = [] #list of bids, results


class Team:
    def __init__(self, id, name):
        self.id = id #relative to a tournament
        self.name = name
        self.members = []

class Pair:
    def __init__(self, id, name):
        self.id = id #relative to a tournament
        self.name = name
        self.members = []


class Tournament:
    def __init__(self, name, type):
        self.name  = name
        self.type = type
        self.sessions = [] 

class TeamTournament(Tournament):
    def __init__(self, teams):
        self.teams = teams
    
class PairsTournament(Tournament):
    def __init__(self, pairs):
        self.pairs = pairs
    

class Session:
    def __init__(self, name, deals):
        self. name = name
        self.deals = deals #list of deals
    
