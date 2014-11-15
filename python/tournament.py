class Deal:
    def __init__(self, id, dealer, zone):
        self.id = id    #created by define tournament
        self.dealer = dealer
        self.zone = ''  #created by define tournament
        self.cards = [] #list of hands SWNE
        self.plays = [] #list of players and bids, results
