#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import collections
import random
import re
import functools
import parsing
from pypeg2 import parse

coloursInput = [("Spades", "S", u"\x50", 4),
                ("Hearts", "H", u"\x50", 3),
                ("Diamonds", "D", u"\x50", 2),
                ("Clubs", "C", u"\x50", 1)]

strainsInput = [("Pass", "P", "P", 0), ("Notrump", "NT", u"\x50", 5)]+coloursInput

class Colour:
    colours = {}

    def __init__(self, name, id, symbol, order):
        self.name = name
        self.id = id
        self.symbol = symbol
        self.order = order
        Colour.colours[id] = self

    def __str__(self):
        return self.id

    def __lt__(self, other):
        return self.order < other.order

    @staticmethod
    def standardOrder():
        all = [v for v in Colour.colours.values()]
        all.sort()
        return all

    @staticmethod
    def fromId(id):
        return Colour.colours[id]


colours = [Colour(x[0], x[1], x[2], x[3]) for x in coloursInput]


class Strain(Colour):
    strains = {}
    scores = {"NT":(30, 10),
              "S":(30, 0),
              "H":(30, 0),
              "D":(20, 0),
              "C":(20, 0),
              "P":(0,0)}

    def __init__(self, name, id, symbol, order):
        self.name = name
        self.id = id
        self.symbol = symbol
        self.order = order
        self.baseScore = Strain.scores[id][0]
        self.firstScore = Strain.scores[id][1]
        Strain.strains[id] = self

    def __str__(self):
        return("{} ".format(self.name))
        #
        #        return("{} {} {} {}".format(
        #            self.name,self.id,self.baseScore,self.firstScore))
    

    def __lt__(self, other):
        return self.order < other.order

    def getColour(self):
        if self.id in Colour.colours:
            return Colour.colours[self.id]
        else:
            return None

    def dkName(self):
        map = {'NT':'Sans','S':'Spar','H':'Hjerter','D':'Ruder','C':'Klør'}
        return map[self.id]

    @staticmethod
    def fromId(id):
        return Strain.strains[id]


    @staticmethod
    def fromDKString(string):
        map = {'UT':'NT','SP':'S','HJ':'H','RU':'D','KL':'C'}
        return Strain.fromId(map[string])
        



#    @staticmethod
#    def setStrainScores():
#        for s in scores:
#        pass
            
    
strains = [Strain(x[0], x[1], x[2], x[3]) for x in strainsInput]

cardValuesInput = [(1,"A",14),
              (2,"2", 2),
              (3,"3", 3),
              (4,"4", 4),
              (5,"5", 5),
              (6,"6", 6),
              (7,"7", 7),
              (8,"8", 8),
              (9,"9", 9),
              (10,"T", 10),
              (11,"J", 11),
              (12,"Q", 12),
              (13,"K", 13)]

class CardValue:
    translate = str.maketrans('EBD','AJQ')

    def __init__(self, a):
        self.number = a[0]
        self.symbol = a[1]
        self.order = a[2]

    def __lt__(self, other):
        return self.order < other.order

    def __str__(self):
        return self.symbol

    @staticmethod
    def fromSymbol(s):
        s1 = s.translate(CardValue.translate)
        for c in cardValuesInput:
            if c[1] == s1:
                return CardValue((c[0], c[1], c[2]))
    
    @staticmethod
    def fromNumber(s):
        for c in cardValuesInput:
            if c[0] == s:
                return CardValue((c[0], c[1], c[2]))
        raise (BaseException("bad cardvalue" + c))

cardValues = [CardValue(x) for x in cardValuesInput]

class Card:
    def __init__(self, colour, value):
       self.value = value
       self.colour = colour

    def __lt__(self, other):
       return (self.colour,self.value) < (other.colour, other.value)

    def __eq__(self, other):
        return (self.value.number == other.value.number and 
        self.colour.id == other.colour.id)

    def byNumber(self, other):
        if self.colour < other.colour:
            return -1
        elif self.colour == other.colour:
            return self.value.number - other.value.number
        else:
            return +1
            
    def sameColour(self,other):
        self.colour == other.colour

    def colour(self):
        return self.colour[3]

    def __str__(self):
        return(self.colour.__str__()+self.value.__str__())
        
    def beats(self, other, trump):
        if self.colour == other.colour and self.value > other.value:
            return True
        if self.colour == trump and not(other.colour == trump):
            return True
        return False

class Cards:
    all = []

    def __init__(self, cards):
        self.cards = cards

    def __in__(self,x):
        return x in self.cards

    def __iter__(self):
        for c in self.cards:
            yield c

    #def __next__(self):
    #    self.step = self.step + 1
    #    if self.step == len(self.cards):
    #        raise StopIteration
    #    else:
    #        return self.cards[self.step]


    def __len__(self):
        return len(self.cards)

    def __str__(self):
        res = ''
        for c in self.cards:
            res = res + '{}, '.format(c)
        return res


    def index(self, v):
        return self.cards.index(v)

    def clone(self):
        return Cards(self.cards.copy())

    def shuffle(self):
        l = self.cards
        random.shuffle(l)
        return Cards(l)

    def deal(self, piles):
        if sum(piles) > len(self.cards):
            print("error")
        start = 0
        res = []
        for pile in piles:
            end = start + pile
            res.append(Cards(self.cards[start:end]))
            start = end
        if start < len(self.cards):
            res.append(Cards(self.cards[start:]))
        return res

    def getCardsOfColour(self, colour):
        byColour = []
        for card in  self.cards:
            if card.colour == colour:
                byColour.append(card)
        return byColour

    def cardsByColour(self):
        byColour = collections.defaultdict(list)
        for card in  self.cards:
            byColour[card.colour].append(card.value)
        res = ""
        colours = [k for k in byColour.keys()]
        colours.sort(reverse=True)
        for c in colours:
            res1 = "\n"+c.__str__()+" "
            values = byColour[c]
            values.sort(reverse= True)
            for v in values:
                res1 = res1 + v.__str__()+" "
            res = res + res1[:len(res1)-1]
        return res 
            
    def removeCard(self, card):
        self.cards.remove(card)


class Deal:
    
    def __init__(self):
        self.dealer = None
        self.zone = None
        self.cards = {}
        self.dealNo = None

    def setDealNo(self, no):
        self.dealNo = no

    def setDealer(self, dealer):
        self.dealer = dealer
        
    def setZone(self, zone):
        self.zone = zone

    #used to addCards 
    def addSuit(self, hand, colour, cards):
        cardList = [Card(colour, c) for c in cards]
        cardList.sort(reverse = True)
        if hand in self.cards:
            self.cards[hand][colour] = cardList
        else:
            self.cards[hand] = {colour: cardList}

    def addOneCard(self, hand, card):
        if not(hand in self.cards):
            self.cards[hand] = {card.colour: [card]}
        else:
            if card.colour in self.cards[hand]:
                self.cards[hand][card.colour].append(card)
            else:
                self.cards[hand][card.colour] = [card]

    def sortHands(self):
        for hand in self.cards:
            for c in self.cards[hand]:
                self.cards[hand][c].sort(reverse= True)

    def addWholeCards(self, hand, colour, cards):
        cards.sort(reverse = True)
        if hand in self.cards:
            self.cards[hand][colour] = cards
        else:
            self.cards[hand] = {colour: cards}

    def __str__(self):
        res = '{} {}/{}:\n'.format(self.dealNo, self.dealer, self.zone)
        hand = Seat.fromId('N')
        for x in range (4):
            res = res + '{}:\n'.format(hand)
            suits = [c for c in self.cards[hand].keys()]
            suits.sort(reverse = True)
            for suit in suits:
                symbols = ''.join(
                    [c.value.symbol for c in self.cards[hand][suit]])
                res = res + '{} {}\n'.format(suit, symbols)
            hand = hand.getNext()

        return res
            
    def hash(self):
        values = bytearray(52)
        count = 0
        for hand in self.cards:
            for (colour, cards)  in self.cards[hand].items():
                for c in cards:
                    count += 1
                    values[deck.index(c)]= hand.order
        print(count, deck)
        print('values',values)
        res = []
        res.append(self.dealer.order*4 + self.zone.getNumber())
        count = 0
        extra = 0
        for v in values:
            if count == 4:
                res.append(extra)
                count = 0
                extra = 0
            extra = extra | (v<<(6 - 2* count))
            count +=1
        if count != 0:
            res.append(extra)
        
        print('res', res)
        self.hash = bytes(res)
        return self.hash

    def bridgebaseHand(self, playerList, bid):
        res = ' http://www.bridgebase.com/tools/handviewer.html?{}'
        cards = ''
        hand = Seat.fromId('N')
        for x in range (3):
            cards = cards + '&{}='.format(hand)
            suits = [c for c in self.cards[hand].keys()]
            suits.sort(reverse = True)
            for suit in suits:
                symbols = ''.join(
                    [c.value.symbol for c in self.cards[hand][suit]])
                cards = cards + '{}{}'.format(suit, symbols)
            hand = hand.getNext()
        res = res + '&v={}&d={}&b={}&p=s'.format(
            self.zone.bridgebaseZone(), 's', self.dealNo) 
        #the p parameter above is required but does not show the player
        for (s,name) in playerList:
            res = res + '&{}n={}'.format(s,name)
        #the bid destroys other display
        #res = res + '&a=-{}'.format(bid)
        return res.format(cards).lower()


    @staticmethod
    def fromHash(hash):
        deal = Deal()
        deal.setDealer( Seat.fromNumber(hash[0] // 4))
        deal.setZone( Zone.fromNumber(hash[0] % 4))
        deal.setDealNo(0)
        
        res = []
        for c in hash[1:]:
            for shift in range(6,-2,-2):
                res.append((c>>shift) & 0b11)

        for (s, card) in zip(res, deck):
            deal.addOneCard(Seat.all[s], card)
            
        deal.sortHands()
        return deal

class Bid:
    pattern = re.compile(
        "(?P<tricks>[1-7])(?P<strain>NT|S|H|D|C)(?P<dbl>[PDR])")

    def __init__(self, bidder = None, tricks = None, strain= None, dbl = None):
        self.bidder = bidder
        self.tricks = tricks
        self.strain = strain
        self.dbl = dbl
        if not bidder:
            self.passedHand = True
        else:
            self.passedHand = False
        #will need to extend when handling not played 

    def relevantFor(self, other):
        if self.passedHand or other.passedHand:
            return True
        else:
            return self.bidder.id in other.bidder.getPair()

    def bridgebaseBid(self):
        if self.dbl == 'P':
            dblStr = ''
        else:
            dblStr = self.dbl
        if self.strain.id == 'NT':
            strainStr = 'n'
        else:
            strainStr = self.strain.id

        return '{:d}{}{}{}'.format(
            self.tricks, strainStr, dblStr,self.bidder).lower()

    @staticmethod
    def fromIslevString(bidstring):
        #pattern = re.compile(
        #    "(?P<bidder>V|Ø|N|S) (?P<tricks>[1-7])(?P<strain>UT|SP|HJ|RU|KL) *(?P<dbl>[PDR]*)")
        #match = pattern.match(bidstring)
        #print('bidstring >{}<'.format(bidstring))
        #if match:
        #    player = Seat.fromDKId(match.group("bidder"))
        #    tricks = match.group("tricks")
        #    strain = Strain.fromDKString(match.group("strain"))
        #    if not(match.group("dbl")):
        #        dbl = 'P'
        #    else:
        #        dbl = match.group("dbl")
        #else:
        #    raise (BaseException("bid exception"))
        #print(bidstring)
        res = parse(bidstring, parsing.Bid)
        if hasattr(res, 'passed'):
            return Bid(strain = Strain.fromId('P'))
        else:
            res = res.played
            player = Seat.fromDKId(res.seat)
            tricks = int(res.tricks)
            strain = Strain.fromDKString(res.strain)
            if res.dbl == '':
                dbl = 'P'
            else:
                dbl = res.dbl
            return Bid(player, tricks, strain, dbl)

    def isPlayedBid(self):
        if not(self.bidder):
            return False
        return True

    def __str__(self):
        if self.dbl == 'P':
            dblStr = ''
        else:
            dblStr = self.dbl

        if self.bidder:
            return("{} {} {} i {}".format(
                self.tricks,self.strain.dkName(),dblStr,self.bidder))
        else:
            return("Pass")

    def getTricks(self):
        return int(self.tricks)

    def getNSResult(self, bidderTricks, zone):
        if self.bidder == None:
            return 0

        bidderScore = bridgescore.getScore(
            self.tricks, self.strain, bidderTricks, self.dbl, 
            zone.inZone(self.bidder)) 
        if self.bidder.getPair() == 'NS':
            return bidderScore
        else:
            return -bidderScore



        
class BidDeprecated:
    pattern = re.compile(
        "(?P<tricks>[1-7])(?P<strain>NT|S|H|D|C)(?P<dbl>[PDR])")

    def __init__(self, bidder, bidstring):
        match = BidDeprecated.pattern.match(bidstring)
        if match:
            self.tricks = match.group("tricks")
            self.strain = Strain.fromId(match.group("strain"))
            self.dbl = match.group("dbl")
        else:
            raise (BaseException("bid exception"))
        self.bidder = bidder

    def __str__(self):
        return("{} {} {} i {}".format(
            self.tricks,self.strain.name,self.dbl,self.bidder))

    def getTricks(self):
        return int(self.tricks)

    def getNSResult(self, bidderTricks, zone):
        bidderScore = bridgescore.getScore(
            self.tricks, self.strain, bidderTricks, self.dbl, 
            zone.inZone(self.bidder)) 
        if self.bidder.getPair() == 'NS':
            return bidderScore
        else:
            return -bidderScore
        
deck = Cards([Card(colour, value) for value in cardValues for colour in Colour.colours.values()])

class Seat:
    all = []
    pairs = ["NS", "EW"]

    def __init__(self, id, order):
        self.id = id
        self.order = order
        Seat.all.append(self)

    def getNext(self, step = 1):
        own = Seat.all.index(self)
        return Seat.all[(own+step) % 4]

    def __str__(self):
        return '{}'.format(self.id)

    def __iter__(self):
        self.count = -1
        print("in iter")
        return self

    def next(self):
        print("in next")
        self.count = self.count + 1
        if self.count == len(Seat.all):
            raise StopIteration
        else:
            return self.getNext(self.count)

    def getPair(self):
        if self.id == "N" or self.id == "S":
            return "NS"
        elif self.id == "E" or self.id == "W":
            return "EW"
        else:
            return "NSEW" #passed hand

    def getOtherPair(self):
        temp = self.getPair()
        if temp == "NS":
            return "EW"
        elif temp == "EW":
            return "NS"
        else:
            print("passed hand")
            return "--"

    @staticmethod
    def fromId(id):
        for x in Seat.all:
            if x.id == id:
                return x
        raise (BaseException("seat not found" + id))

    @staticmethod
    def fromNumber(no):
        for x in Seat.all:
            if x.order == no:
                return x
        raise (BaseException("seat not found" + id))

    @staticmethod
    def fromDKId(id):
        if id == 'Ø':
            id = 'E'
        elif id == 'V':
            id = 'W'

        for x in Seat.all:
            if x.id == id:
                return x
        raise (BaseException("seat not found" + id))

    

allSeatsInput = [("S",0), ("W",1), ("N",2), ('E',3)]
for seat in allSeatsInput:
    Seat(seat[0],seat[1])

Seat.all.sort(key = lambda x: x.order)

class Zone:
    pattern = re.compile("(NONE|NS|EW|ALL)")
    all ={0:'NONE', 1:'NS', 2:'EW',3:'ALL'}
    
    def __init__(self, zoneString):
        match = Zone.pattern.match(zoneString)
        if match:
            self.zone = match.group()
        else:
            raise (BaseException("zone exception"))

    def __str__(self):
        return self.zone

    def inZone(self, seat):
        if self.zone == 'ALL':
            return True
        if self.zone == 'NONE':
            return False
        return seat.id in self.zone

    def bridgebaseZone(self):
        if self.zone == 'ALL':
            return 'b'
        elif self.zone == 'EW':
            return 'e'
        elif self.zone == 'NS':
            return 'n'
        else:
            return '-'

    @staticmethod
    def fromDKName(name):
        if name == 'Ingen':
            res = Zone('NONE')
        elif name == 'Alle':
            res = Zone('ALL')
        elif name == 'NS':
            res = Zone('NS')
        elif name == 'ØV':
            res = Zone('EW')
        return res

    def getNumber(self):
        for (x,v) in Zone.all.items():
            if v == self.zone:
                return x
            
        raise (BaseException("zone exception"))

    @staticmethod
    def fromNumber(x):
        if x in Zone.all.keys():
            return Zone.all[x]
        
        raise (BaseException("zone exception"))
    

if __name__ == '__main__':
#    deck.cards.sort(a)
#    for c in deck.cards:
#        print(c)

    for c in colours:
        print(c)
    print (deck.cardsByColour())
    for p in strains:
        print(p)

    shuffled = deck.shuffle()
#    for c in shuffled:
#        print( c)

    res = shuffled.deal([13,13,13])
    for hand in res:
        print(hand.cardsByColour())

    for x in Strain.strains:
        x

    for t in range(1,8):
        for s in Strain.strains.keys():
            print(BidDeprecated(Seat.fromId('N'),'{}{}P'.format(t,s)))

    print("N", Seat.fromId("N"))
                       
    for x in (Seat.all):
        print(x)
        print("NSZone: ", Zone("NS").inZone(x))
        print("EWZone: ", Zone("EW").inZone(x))
        print("ALLZone: ", Zone("ALL").inZone(x))
        print("NoneZone: ", Zone("NONE").inZone(x))
    for x in range (4):
        print('N + {} {}'.format(x, Seat.fromId("N").getNext(x)))

