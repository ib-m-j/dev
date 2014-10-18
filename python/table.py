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
        res =  'by {}  {}'.format(self.start, self.cards)
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

    def __init__(self, strainId, dealer, zone):
        self.dealer = dealer
        if strainId in bridgecore.Colour.colours:
            self.strain = bridgecore.Colour.colours[strainId]
        else:
            self.strain = None
        self.tricks = []
        self.player = bridgecore.Seat.fromId('N')
        self.zone = ''
        self.dealt = {}
        self.remainingCards = {}
        shuffled = bridgecore.deck.shuffle()
        dealt = shuffled.deal([13,13,13])
        for (place, cards) in zip(bridgecore.Seat.all, dealt):
            self.dealt[place] = bridgecore.Cards(cards)

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
        self.tricks.append(trick)
        self.player = trick.winner()

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

class Table:
    def __init__(self, names):
        self.seats = {}
        #south, west, north, east
        for (place, name) in zip(bridgecore.Seat.all, names):
            self.seats[place] = name

    def __str__(self):
        s = ""
        for (p,n) in self.seats.items():
            s = s + '\n{}: {}\n'.format(p,n)
        return s+'\n'

    def startPlay(self, strain, dealer, zone):
        self.play = CardPlay(strain, dealer, zone)

    def playATrick(self):
        self.play.playATrick()
            

if __name__ == '__main__':
    shuffled = bridgecore.deck.shuffle()
    shuffled.deal([13,13,13])
#    print("starting")
#    for x in bridgecore.Seat.all:
#        print(x)


    t = Table (['a','b','c','d'])
    t.startPlay('S', 'N', '')
 #   print(t)
    print(t.play.showDeal())
    
    while len(t.play.tricks) < 13:
        t.playATrick()
    for (n,trick) in enumerate(t.play.tricks):
        print('{}: {}'.format(n,trick))
