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


def getScore(bidValue, bidStrain, wonTricks, dbl, inZone):
    wonValue = wonTricks - 6 

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
        if inZone == True:
            factor = 2
        else:
            factor = 1

        if dbl == "D":
            dblFactor = 1
        elif dbl == "R":
            dblFactor = 2

        baseDbl = [100,300,500]
        baseDblInZone =[200,500,800]
        extraDownValue = 300
        simpleDown = 50
        extraDownTricks = lostTricks - 3
        if extraDownTricks < 0:
            extraDownTricks = 0

        if dbl == "P":
            return lostTricks*simpleDown*factor

        if lostTricks <= 3:
            if inZone:
                res = baseDblInZone[lostTricks - 1]
            else:
                res = baseDbl[lostTricks - 1]
        else:
            if inZone:
                res = baseDblInZone[-1]
            else:
                res = baseDbl[-1]
        res = res +  extraDownTricks*extraDownValue
        res = res *dblFactor
        return res
 
    if dbl == "P":
        factor = 1
    elif dbl == "D":
        factor = 2
    else:
        factor = 4

    
    if wonValue >= bidValue:
        #first the bid score
        res = (bidValue*bidStrain.baseScore + bidStrain.firstScore)*factor
        if res >= 100:
            res = res + gameBonus(inZone)
        else:
            res = res + 50
        
        if dbl == "D":
            res = res + 50
        elif dbl == "R":
            res = res + 100

        #other bonusses
        if bidValue == 6:
            res = res + smallSlamBonus(inZone)
        if bidValue == 7:
            res = res + largeSlamBonus(inZone)

        
        res = res + overtrickValue(inZone, dbl, bidStrain, wonValue - bidValue)

    else:
        res = -defeatedScore(inZone, dbl, bidValue - wonValue)


  #  return '{} {} - {} {} tricks {}\n'.format(
  #      bidValue, bidStrain, wonTricks, inZone, res)
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
        bidValue = self.bid.getTricks()
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


def checkGoingDown():
    strains = [x.id for x in bridgecore.Strain.strains.values()]
    for inZone in [True, False]:
        print("in Zone: ", inZone)
        for dbl in ["P","D","R"]:
            print("Dbl: ", dbl)
            for x in range (13):
                strain = bridgecore.Strain.strains[random.choice(strains)]
                bid = 7
                won = x
                print("in zone {}. {} {} {} {} ({}): {}".format(
                    inZone, bid, strain, dbl, x, bid + 6 - won ,
                    getScore(bid, strain, x, dbl, inZone)))


def checkWinning():
    for strainId in ["NT", "S", "D"]:
        strain = bridgecore.Strain.strains[strainId]
        for inZone in [True, False]:
            print("in Zone: ", inZone)
            for dbl in ["P","D","R"]:
                print("Dbl: ", dbl)
                for bid in range (1,8):
                    res = "in zone {}. {} {} {} ".format(
                        inZone, bid, strain, dbl,)
                        
                    for won in range(13, bid + 5,-1):
                        res = res + '  {}: {}'.format(
                            won, getScore(bid, strain, won, dbl, inZone))
                    print(res)


if __name__ == '__main__':
#    shuffled = bridgecore.deck.shuffle()
#    shuffled.deal([13,13,13])
#    print("starting")
#    for x in bridgecore.Seat.all:
#        print(x)
    checkWinning()
