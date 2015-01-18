import re
import bridgecore
import sys

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

class Play:
    def __init__(self, deal, SWNEPlayers, bid, tricks, NSResult):
        self.deal = deal
        self.players = {}
        for id, p in zip(['S','W','N','E'],SWNEPlayers):
            self.players[bridgecore.Seat.fromId(id)] = p
        self.bid = bid
        self.tricks = tricks
        self.NSResult = NSResult
        if not self.bid.bidder:
            self.tricks = '-'

#    def displayStrainId(self):
#        if self.bid.bidder:
#            return self.bid.strain.id
#        return 'Pass'
#
    def playedBy(self):
        if self.bid.bidder:
            return self.players[self.bid.bidder]
        return None

    def hasParticipant(self, teamPlayer):
        return teamPlayer in self.players.values()

    def playedByPair(self):
        if self.bid.bidder:
            side = self.bid.bidder.getPair()
            return [self.players[bridgecore.Seat.fromId(x)] for x in side]
        return []

    def pairOf(self, teamPlayer):
        res = False
        for (seat, tPlayer) in self.players.items():
            if (tPlayer) == teamPlayer:
                res = seat
                break
        if res:
            return seat.getPair()
        else:
            return ''

class Team:
    def __init__(self, localId):
        self.localId = localId
        self.globalId = self.localId
        self.teamPlayers = []
    
    def addTeamPlayer(self, teamPlayer):
        if not(teamPlayer in self.teamPlayers):
            self.teamPlayers.append(teamPlayer)


class Tournament:
    playerKey = re.compile('\s*(?P<name>\w+)@(?P<team>\w+)\s*$')

    #only teams for now
    def __init__(self, name = None):
        self.name = name
        self.teams = {}
        self.deals = {}
        self.plays = [] #dealid, players, deal, bid, NSresult

    def setName(self, name):
        self.name = name

    def getTeam(self, teamLocalId):
        if not teamLocalId in self.teams:
            self.teams[teamLocalId] = Team(teamLocalId)
        return self.teams[teamLocalId]
        
    def getNextDeal(self):
        return len(self.deals)
        
    def addDeal(self, dealId, deal):
        if dealId in self.deals:
            raise Exception('duplicate deal')
        self.deals[dealId] = deal
        
            
    def addPlay(self, dealLocalId, SWNEPlayers, bid, tricks, NSResult):
        #One Player: (TeamName, OwnName)
        #bid bidder, bid
        for (team, player) in SWNEPlayers:
            if not(team in self.teams):
                self.teams[team]=Team(team)
            self.teams[team].addTeamPlayer(player)
        self.plays.append(Play(dealLocalId, SWNEPlayers, bid, tricks, NSResult))

    def getPlayedByPair(self, teamPlayer):
        res = []
        for play in self.plays:
            if teamPlayer in play.playedByPair():
                res.append(play)
        return res
            
    def getDefendedByPair(self, teamPlayer):
        res = []
        for play in self.plays:
            if play.hasParticipant(teamPlayer) and not(
                    teamPlayer in play.playedByPair()):
                res.append(play)
        return res
            

    def getPlayedByPlayer(self, teamPlayer):
        res = []
        for play in self.plays:
            if play.playedBy() == teamPlayer:
                res.append(play)
        return res

    def getPlayedByTeam(self, teamPlayer):
        res = []
        for play in self.plays:
            if play.hasParticipant(teamPlayer):
                res.append(play)
        return res


#        def getPos(teamPlayer, SWNEPlayers):
#            try:
#                res = ['S','W','N','E'][SWNEPlayers.index(teamPlayer)]
#            except:
#                return None
#            else:
#                return res
#    
#        res = []
#        for play in self.plays:
#            player = play[2].bidder
#            pos = getPos(teamPlayer, play[1])
#            if pos and pos in player.getPair():
#                    res.append(play)
#        return res

