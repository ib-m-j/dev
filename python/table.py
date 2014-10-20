import bridgecore
import random

class Trick:
    def __init__(self, contractStrain, start, cards):
        self.start = start
        self.cards = cards
        self.contractStrain = contractStrain

    def addCard(self, card):
        self.cards.append(card)

    def __str__(self):
        res =  'by {}  {} won by {}'.format(
            self.start, self.cards, self.winner())
        return res

    def winner(self):
        winner = self.cards.cards[0]
        offset = 0
        for (no,c) in enumerate(self.cards.cards[1:]):
            if c.beats(winner,self.contractStrain):
                winner = c
                offset = no+1
        return self.start.getNext(offset)


def getScore(bidTricks, bidStrain, wonTricks, dbl, inZone):
    won = wonTricks - 6 

    def gameBonus(inZone):
        if inZone:
            return 500
        return 300
            
    def smallSlamBonus(inZone):
        if inZone:
            return 750
        return 500

    def largeSlamBonus(inZone):
        if inZone:
            return 1500
        return 1000

    def overtrickValue(inZone, dbl, bidStrain, overTricks):
        if inZone:
            factor = 2
        else: 
            factor = 1

        if dbl == "P":
            return bidStrain.baseScore*overTricks
        elif dbl == "D":
            return 100*factor*overTricks
        else:
            return 200*factor*overTricks

    def defeatedScore(inZone, dbl, lostTricks):
        if inZone:
            factor = 2
        else:
            factor = 1

        baseDbl = [100,300,500]
        baseRdbl =[200,500,800]
        extraDownValue = 300
        simpleDown = 50
        extraDownTricks = lostTricks - 3
        if extraDownTricks < 0:
            extraDownTricks = 0

        if dbl == "P":
            return lostTricks*simpleDown*factor
        
        if extraDownTricks == 0:
            if dbl == "D":
                return baseDbl[lostTricks - 1]*factor
            if dbl == "R":
                return baseRdbl[lostTricks - 1]*factor
        else:
            if dbl == "D":
                return (extraDownTricks*extraDownValue + baseDbl[-1])*factor
            if dbl == "R":
                return (extraDownTricks*extraDownValue + baseRdbl[-1])*factor
                
    if dbl == "D":
        factor = 1
    else:
        factor = 2
#still need to compensate for games whe doubled...
    if won >= bidTricks:
        res = bidTricks*bidStrain.baseScore + bidStrain.firstScore
        if bidTricks >= bidStrain.gameBonusTricks:
            res = res + gameBonus(inZone)
            if bidTricks == 6:
                res = res + smallSlamBonus(inZone)
            if bidTricks == 7:
                res = res + largeSlamBonus(inZone)
        else:
            res = res + 50

        res = res*factor + overtrickValue(inZone, dbl, bidStrain, won - bidTricks)

    else:
        res = -defeatedScore(inZone, dbl, bidTricks - won)


  #  return '{} {} - {} {} tricks {}\n'.format(
  #      bidTricks, bidStrain, wonTricks, inZone, res)
    return res






        
class CardPlay:

    def __init__(self, strainId, dealer, zone = 'NONE'):
        self.dealer = dealer
        self.dealt = {}
        self.wonTricks = {}
        for x in bridgecore.Seat.pairs:
            self.wonTricks[x] = 0
        #if strainId in bridgecore.Colour.colours:
        #    self.strain = bridgecore.Colour.colours[strainId]
        #else:
        #    self.strain = None
        #from self.bid
        #self.player = bridgecore.Seat.fromId('N')
        self.playedTricks = []
        self.zone = bridgecore.Zone(zone)

        #self.bid set by call

    def showDeal(self):
        s=''
        for (p,n) in self.dealt.items():
            s = s + '\n{}: {}\n'.format(p,n.cardsByColour())
        return s

    def playATrick(self):
        trickInput = []
        self.trickColour = None
        for x in range(len(bridgecore.Seat.all)):
            seat = self.player.getNext(x)           
            #  pick = random.randrange(0,len(self.dealt[seat].cards.cards))
            #  played = self.dealt[seat].cards.cards[pick]
            played = self.legalPlay(x, seat)
            self.dealt[seat].cards.cards.remove(played)
            trickInput.append(played)
        trick = Trick(self.strain, self.player, bridgecore.Cards(trickInput))
        self.playedTricks.append(trick)
        self.player = trick.winner()
        self.wonTricks[self.player.getPair()] = self.wonTricks[
            self.player.getPair()] + 1

    def legalPlay(self, x, seat):
        if x == 0:
            pick = random.randrange(0,len(self.dealt[seat].cards.cards))
            played = self.dealt[seat].cards.cards[pick]
            self.trickColour = played.colour
        else:
            correctColour = self.dealt[seat].cards.getCardsOfColour(
                self.trickColour)
            if len(correctColour)>0:
                played = correctColour[0]
            else:
                played = self.dealt[seat].cards.cards[0]
            #raise (BaseException("bid exception"))

        return played

    def setFinalBid(self, bid):
        #this still suffers from mixup between colour and strain
        #self.strain is now set to be a colour as needed by trick playing
        self.bid = bid
        self.player = bid.bidder
        if self.bid.strain.id in bridgecore.Colour.colours:
            self.strain = bridgecore.Colour.colours[self.bid.strain.id]
        else:
            self.strain = None

    def getFinalBid(self):
        return self.bid

    def getNSScore(self):
        won = self.wonTricks[bridgecore.Seat.getPair(self.bid.bidder)] - 6
        bidTricks = self.bid.getTricks()
        player = self.getFinalBid().bidder
        inZone = self.zone.inZone(player)
        print( '{} - {} tricks \n'.format(
            self.getFinalBid(), won))
        print(self.strain, self.bid.strain)

        

    def dealCards(self):
        shuffled = bridgecore.deck.shuffle()
        dealt = shuffled.deal([13,13,13])
        for (place, cards) in zip(bridgecore.Seat.all, dealt):
            self.dealt[place] = bridgecore.Cards(cards)



class Table:
    def __init__(self, names):
        #from tournament once pr sitting
        self.seats = {}
        #south, west, north, east
        for (place, name) in zip(bridgecore.Seat.all, names):
            self.seats[place] = name
        #

        #from playing system self.play includes dealing so once pr hand
        #from bidding system included in self.play
        #from scoring system ijcluded in self.play




    def __str__(self):
        s = ""
        for (p,n) in self.seats.items():
            s = s + '\n{}: {}\n'.format(p,n)
        return s+'\n'

    def startPlay(self, strain, dealer, zone):
        self.play = CardPlay(strain, dealer, zone)
        self.play.dealCards()
        self.play.setFinalBid(
            bridgecore.Bid(bridgecore.Seat.fromId('N'), "4SP"))

    def playATrick(self):
        self.play.playATrick()
            
    def getScore(self):
        return self.play.getNSScore()


def runPlay():
    t = Table (['a','b','c','d'])
    t.startPlay('S', 'N', 'ALL')
 #   print(t)
    print(t.play.showDeal())
    
    print(t.play.getFinalBid())

    while len(t.play.playedTricks) < 13:
        t.playATrick()
    for (n,trick) in enumerate(t.play.playedTricks):
        print('{}: {}'.format(n,trick))

    print(t.getScore())    


if __name__ == '__main__':
#    shuffled = bridgecore.deck.shuffle()
#    shuffled.deal([13,13,13])
#    print("starting")
#    for x in bridgecore.Seat.all:
#        print(x)
    for inZone in [False, True]:
        print("\n")
#        for strain in bridgecore.Strain.strains.values():
        strain = bridgecore.Strain.strains["S"]
        for bid in range(1,8):
            print (inZone, strain, bid)
            res = ''
            for won in range(14):
                res = res + '{}:{} '.format(
                    won, getScore(bid, strain, won, "R", inZone))
            print( res)
