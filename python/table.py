import bridgecore
import bridgescore
import cardevaluation
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



        
class CardPlay:

    def __init__(self, dealer, zone = 'NONE'):
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
        s = s + '\nZone {}\n'.format(self.zone )
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
        trick = Trick(
            self.strain.getColour(), self.player, bridgecore.Cards(trickInput))
        self.playedTricks.append(trick)
        self.player = trick.winner()
        self.wonTricks[self.player.getPair()] = self.wonTricks[
            self.player.getPair()] + 1

    def legalPlay(self, x, seat):
        trumpColour = self.bid.strain.getColour()
        played = None
        if x == 0:
            pick = random.randrange(0,len(self.dealt[seat].cards.cards))
            played = self.dealt[seat].cards.cards[pick]
            self.trickColour = played.colour
        else:
            correctColour = self.dealt[seat].cards.getCardsOfColour(
                self.trickColour)
            if len(correctColour)>0:
                played = correctColour[0]
            elif trumpColour:
                trumps = self.dealt[seat].cards.getCardsOfColour(
                    trumpColour)
                if len(trumps)>0:
                    played = trumps[0]

            if not played:
                played = self.dealt[seat].cards.cards[0]
            #raise (BaseException("bid exception"))

        return played

    def setFinalBid(self, bid):
        self.bid = bid
        self.player = bid.bidder
        self.strain = self.bid.strain

#not used kept until I am sure this is irrelevant
#        if self.bid.strain.id in bridgecore.Colour.colours:
#            self.strain = bridgecore.Colour.colours[self.bid.strain.id]
#        else:
#            self.strain = None

    def getFinalBid(self):
        return self.bid

    def getNSScore(self):
        wonTricks = self.wonTricks[bridgecore.Seat.getPair(self.bid.bidder)]
        bidValue = self.bid.getTricks()
        player = self.getFinalBid().bidder
        inZone = self.zone.inZone(player)
        print( '{} - {} tricks \n'.format(
            self.getFinalBid(), wonTricks))
        print(self.strain, self.bid.strain)
        score = bridgescore.getScore(
            bidValue, self.bid.strain, wonTricks, self.bid.dbl, inZone)

        if self.bid.bidder.getPair() == "NS":
            return score
        else:
            return -score
        

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

    def startPlay(self, dealer, zone):
        #these values should come from other sources in the end
        self.play = CardPlay( dealer, zone)
        self.play.dealCards()
        (bestSeat, bestLength, bestColour) = \
        cardevaluation.getBestHandAndColour(self.play.dealt)
        self.play.setFinalBid(
            bridgecore.Bid(bestSeat, "3NTP"))
#            bridgecore.Bid(bestSeat, "4{}P".format(bestColour.id)))

    def playATrick(self):
        self.play.playATrick()
            
    def getScore(self):
        return self.play.getNSScore()

#unittests

def runPlay():
    t = Table (['a','b','c','d'])
    t.startPlay('N', 'ALL')
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
                    brdigescore.getScore(bid, strain, x, dbl, inZone)))


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
                            won, bridgescore.getScore(
                                bid, strain, won, dbl, inZone))
                    print(res)


if __name__ == '__main__':
    shuffled = bridgecore.deck.shuffle()
    shuffled.deal([13,13,13])
    print("starting")
    for x in bridgecore.Seat.all:
        print(x)

    runPlay()

#added this comment in github

