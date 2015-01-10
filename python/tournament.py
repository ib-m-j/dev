import re

#use Deal from  bridgecore
#class Deal:
#    def __init__(self, localId):
#        self.localId = localId    #created by define tournament
#        self.globalId = self.localId
#        self.dealer = ''
#        self.zone = ''  
#        self.cards = [] #list of hands SWNE
#        self.plays = [] #list of generic players and bids, results
#
#    def addDetails(self, dealer, zone, cards):
#        self.dealer = dealer
#        self.zone = zone
#        self.cards = cards
#        
#    def addPlay(self, play):
#        self.plays.append(play)
#

class Team:
    def __init__(self, localId, teamPlayer):
        self.localId = localId
        self.globalId = self.localId
        self.teamPlayer = teamPlayer
    
    def addTeamPlayer(self, teamPlayer):
        if not(teamPlayer in self.teamPlayers):
            self.teamPlayers.append(teamPlayer)


class Tournament:
    playerKey = re.compile('\s*(?P<name>\w+)@(?P<team>\w+)\s*$')

    #only teams for now
    def __init__(self, name):
        self.name = name
        self.teams = {}
        self.deals = {}
        self.plays = [] #players, deal, bid, NSresult

    def getTeam(self, teamLocalId):
        if not teamLocalId in self.teams:
            self.teams[teamLocalId] = Team(teamLocalId)
        return self.teams[teamLocalId]

    def addDeal(self, deal, players):
        if deal.localId in self.deals:
            raise Exception('duplicate deal')
        self.deals[deal.localId] = bridgecore.Deal()
        
            
    def addPlay(self, dealLocalId, SWNEPlayers, bid, tricks, NSResult = None):
        #One Player: 'TeamName.OwnName'
        #bid bidder, bid
        if not(dealLocalId in self.deals):
            raise Exception('duplicate deal')
        for p in SWNEPlayers:
            res = playerKey.match(s)
            if not(res):
                raise Exception('badly formed team.player')
            else:
                team = res.group('team')
                player = res.group('name')
                if team in self.teams:
                    if not(player in self.teams[team]):
                        self.team.addTeamPlayer(player)
            if not NSResult:
                NSResult = bid.getNSResult(tricks, self.deals[dealLocalId].zone)
            self.plays.append([SWNEPlayers, bid, tricks, NSResult])
