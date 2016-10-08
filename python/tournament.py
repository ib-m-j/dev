import re
import bridgecore
import bridgescore
import sys
import os.path

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
    def __init__(
            self, deal, SWNEPlayers, bid, tricks, NSResult, playedOut = None):
        self.deal = deal
        self.players = {}
        for id, p in zip(['S','W','N','E'],SWNEPlayers):
            self.players[bridgecore.Seat.fromId(id)] = p
        self.bid = bid
        self.tricks = tricks
        self.NSResult = NSResult
        self.playedOut = playedOut
        if not self.bid.bidder:
            self.tricks = '-'

    def dump(self):
        print("dealno",self.deal)
        print(self.players)
        print(self.bid)
        print(self.NSResult)
        print(self.playedOut)
        

#    def displayStrainId(self):
#        if self.bid.bidder:
#            return self.bid.strain.id
#        return 'Pass'
#
    def playedBy(self):
        if self.bid.bidder:
            return self.players[self.bid.bidder]
        return ('-', '-')

    def hasParticipant(self, teamPlayer):
        return teamPlayer in self.players.values()

    def hasTeamParticipant(self, team):
        found = False
        for teamPlayer in self.players.values():
            if team == teamPlayer[0]:
                found = True
                break
        return found

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

    def seatOf(self, teamPlayer):
        res = ''
        for (seat, tPlayer) in self.players.items():
            if (tPlayer) == teamPlayer:
                res = seat
                break
        if res:
            return seat
        else:
            return ''

    def getResult(self, direction):
        if direction == 'NS':
            return self.NSResult
        else:
            return -self.NSResult

    def getBridgeBasePlayers(self):
        playerList = []
        for seat in ['S','W','N','E']:
            playerList.append(
                (seat, self.players[bridgecore.Seat.fromId(seat)][1]))
        return playerList


#class Team:
#    def __init__(self, localId):
#        self.localId = localId
#        self.globalId = self.localId
#        self.teamPlayers = []
#    
#    def addTeamPlayer(self, teamPlayer):
#        if not(teamPlayer in self.teamPlayers):
#            self.teamPlayers.append(teamPlayer)
#

class Tournament:
    playerKey = re.compile('\s*(?P<name>\w+)@(?P<team>\w+)\s*$')

    #only teams for now
    def __init__(self, name = None):
        self.type = ''
        self.name = name
        self.teams = {}
        self.deals = {}
        self.plays = [] #dealid, players, deal, bid, NSresult
        self.teamPlayers = bridgecore.TeamPlayers('TeamPlayers')

    def setName(self, name):
        self.name = name
        
    def addOrigin(self, server, url):
        self.server = server
        self.url = url

    def getId(self):
        base = os.path.splitext(os.path.basename(self.url))[0]
        return '{}{}'.format(
            self.server.split('.')[0],
            base[len(base)- 4:])
            

    #def getTeam(self, teamLocalId):
    #    if not teamLocalId in self.teams:
    #        self.teams[teamLocalId] = Team(teamLocalId)
    #    return self.teams[teamLocalId]
        
    def getNextDeal(self):
        return len(self.deals)
        
    def addDeal(self, dealId, deal):
        if dealId in self.deals:
            raise Exception('duplicate deal')
        self.deals[dealId] = deal
        
            
    def addPlay(self, dealLocalId, SWNEPlayers, 
                bid, tricks, NSResult, playedOut):
        #One Player: (TeamName, OwnName)
        #bid bidder, bid
        for (team, player) in SWNEPlayers:
            self.teamPlayers.addValue((team, player))
        self.plays.append(
            Play(dealLocalId, SWNEPlayers, bid, tricks, NSResult, playedOut))

    #deprecated def getPlayedByPair(self, teamPlayer):
    def getParticipatedByPlayer(self, teamPlayer):
        playedBy  = []
        defendedBy = []
        for play in self.plays:
            #print(play.players)
            if teamPlayer in play.playedByPair():
                playedBy.append(play)
            elif play.hasParticipant(teamPlayer):
                defendedBy.append(play)
        return (playedBy, defendedBy)
    
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

    #played means particpated in play
    def isPlayedByTeamOther(self, play, teamPlayer):
        if play.hasTeamParticipant(
                teamPlayer[0]) and not play.hasParticipant(
                teamPlayer):
            return  True
        return False

    def getPlayedByTeamOther(self, deal, teamPlayer):
        for play in self.plays:
            if play.deal == deal and self.isPlayedByTeamOther(play, teamPlayer):
                return play
        return None

    def getRank(self, play, direction):
        rank = -1
        total = -2
        myScore = play.getResult(direction)
        for p in self.plays:
            if p.deal == play.deal:
                total = total + 2
                if p.getResult(direction) < play.getResult(direction):
                    rank = rank + 2
                elif p.getResult(direction)== play.getResult(direction):
                    rank = rank + 1
        return (rank, total)

        
    def getCrossImps(self, play, direction):
        res = 0
        count = 0
        myScore = play.getResult(direction)
        for p in self.plays:
            if p.deal == play.deal:
                if p.players != play.players:
                    count = count + 1
                    res = res + bridgescore.impScore(myScore - p.getResult(direction))

        return res/count

    def makeTableInput(self, focusTeamPlayer):
        (playedByFocus, defendedByFocus) = self.getPlayedByPair(
            focusTeamPlayer)
        
        focusType = bridgecore.IdList('focusType', ['playedBy', 'defendedBy'])
        tableHeader = bridgecore.IdList(
            'teamOverviewTable',['dealNo', 
                'focusType', 'focusDirection', 'bonusType',
                'teamScore', 'crossImps', 'rank'])
        tableData = []
        for (n, list) in enumerate([playedByFocus, defendedByFocus]):
            for p in list:
                focusDirection = p.pairOf(focusTeamPlayer)
                teamScore = p.getResult(
                    focusDirection)- self.getPlayedByTeamOther(
                    p.deal, focusTeamPlayer).getResult(focusDirection)
                crossImps =  self.getCrossImps(p, focusDirection)
                (rank, maxRank) = self.getRank(p, focusDirection)
                tableData.append(
                    [p.deal, focusType.getValue(n), focusDirection, 
                     p.bid.getBidBonusType(), teamScore, 
                     round(crossImps,1), rank, maxRank])

        return (tableHeader, tableData)
             
