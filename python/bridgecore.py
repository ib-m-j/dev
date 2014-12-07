#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import collections
import random
import re
import functools

coloursInput = [("Spades", "S", u"\x50", 4),
                ("Hearts", "H", u"\x50", 3),
                ("Diamonds", "D", u"\x50", 2),
                ("Clubs", "C", u"\x50", 1)]

strainsInput = [("Notrump", "NT", u"\x50", 5)]+coloursInput

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
              "C":(20, 0)}

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
    


    def getColour(self):
        if self.id in Colour.colours:
            return Colour.colours[self.id]
        else:
            return None


    

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
        self.step = -1
        return self

    def __next__(self):
        self.step = self.step + 1
        if self.step == len(self.cards):
            raise StopIteration
        else:
            return self.cards[self.step]

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        res = ''
        for c in self.cards:
            res = res + '{}, '.format(c)
        return res

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

    def addCards(self, hand, colour, cards):
        cardList = [Card(colour, c) for c in cards]
        cardList.sort(reverse = True)
        if hand in self.cards:
            self.cards[hand][colour] = cardList
        else:
            self.cards[hand] = {colour: cardList}

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
        res = []
        res.append(self.dealer.order*4 + self.zone.getNumber())
        for count in range(3):
            seat = Seat.all[count]
            for colour in Colour.standardOrder():
                cardList = self.cards[seat][colour]
                cL = cardList.copy()
                cL.sort(
                reverse = True, key = functools.cmp_to_key(Card.byNumber))
                for card in cL:
                    res.append(card.value.number)
                res.append(0)
            res = res[:-1]

        if len(res) % 2 == 1:
            res.append(0)
        
        print( res)
        compact = []
        for r in range((len(res) // 2)):
            compact.append(16*res[2*r] + res[2*r+1])
            print('{:x}'.format(compact[-1]))
        self.hash = bytes(compact)
        return self.hash

    @staticmethod
    def fromHash(hash):
        deal = Deal()
        splitHash = []
        for b in hash:
            splitHash.extend([b // 16, b % 16])
        deal.setDealer( Seat.fromNumber(splitHash[0] // 4))
        deal.setZone( Zone.fromNumber(splitHash[0] % 4))
        deal.setDealNo(0)

        cardCount = 0
        currentSeatNo = 0
        currentColourCount = 0
        colourOrder = Colour.standardOrder()
        currentColour = colourOrder[currentColourCount%4]
        cardValues = []
        for n in splitHash[1:]:
            if n != 0 and cardCount != 13:
                cardValues.append(CardValue.fromNumber(n))
                cardCount += 1
            else:
                deal.addCards(
                    Seat.all[currentSeatNo], currentColour, cardValues)
                currentColourCount += 1
                currentColour = colourOrder[currentColourCount%4]
                cardValues = []
                if cardCount == 13:
                    currentSeatNo += 1
                    if n == 0:
                        deal.addCards(
                            Seat.all[currentSeatNo], currentColour, cardValues)
                        currentColourCount += 1
                        currentColour = colourOrder[currentColourCount%4]
                        cardValues = []
                        cardCount = 0
                    else:
                        cardValues.append(CardValue.fromNumber(n))
                        cardCount = 1

        allCards = deck.clone()
        for seat in deal.cards.keys():
            for colour in deal.cards[seat].keys():
                for card in deal.cards[seat][colour]:
                    allCards.removeCard(card)
        
        for colour in Colour.standardOrder():
            cards = allCards.getCardsOfColour(colour)
            deal.addWholeCards(Seat.all[3],colour, cards)

                
        return deal
                    
#    def dealFromHash(hash):
#        splitHash = []
#        for b in hash:
#            splitHash.extend([b // 16, b % 16])
#        cardCount = 0
#        currentSeatNo = 0
#        deal = {Seat.all[currentSeatNo]: []}
#        currentColourCount = 0
#        colourOrder = Colour.standardOrder()
#        cards = colourOrder[currentColourCount].id + ': '
#        for n in splitHash[1:]:
#            if n != 0 and cardCount != 13:
#                cards = cards + '{} '.format(n)
#                cardCount += 1
#            else:
#                deal[Seat.all[currentSeatNo]].append(cards)
#                currentColourCount += 1
#                cards = colourOrder[currentColourCount%4].id + ': '
#                if cardCount == 13:
#                    currentSeatNo += 1
#                    deal[Seat.all[currentSeatNo]] =  []
#                    if n == 0:
#                        deal[Seat.all[currentSeatNo]].append(cards)
#                        currentColourCount += 1
#                        cards = colourOrder[currentColourCount%4].id + ': '
#                        cardCount = 0
#                    else:
#                        cards = cards + '{} '.format(n)
#                        cardCount = 1
#                    
#        return deal
#                    
                
                
                
            

class Bid:
    pattern = re.compile(
        "(?P<tricks>[1-7])(?P<strain>NT|S|H|D|C)(?P<dbl>[PDR])")

    def __init__(self, bidder, bidstring):
        match = Bid.pattern.match(bidstring)
        if match:
            self.tricks = match.group("tricks")
            self.strain = Strain.fromId(match.group("strain"))
            self.dbl = match.group("dbl")
        else:
            raise (BaseException("bid exception"))
        self.bidder = bidder

    def __str__(self):
        return("{} {} {} by {}".format(
            self.tricks,self.strain.name,self.dbl,self.bidder))

    def getTricks(self):
        return int(self.tricks)

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
        else:
            return "EW"

    

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
            print(Bid(Seat.fromId('N'),'{}{}P'.format(t,s)))

    print("N", Seat.fromId("N"))
                       
    for x in (Seat.all):
        print(x)
        print("NSZone: ", Zone("NS").inZone(x))
        print("EWZone: ", Zone("EW").inZone(x))
        print("ALLZone: ", Zone("ALL").inZone(x))
        print("NoneZone: ", Zone("NONE").inZone(x))
    for x in range (4):
        print('N + {} {}'.format(x, Seat.fromId("N").getNext(x)))

