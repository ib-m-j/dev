#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import collections
import random
import re

coloursInput = [("Spades", "S", u"\x50", 4),
                ("Hearts", "H", u"\x50", 3),
                ("Diamonds", "D", u"\x50", 2),
                ("Clubs", "C", u"\x50", 1)]

strainsInput = [("Notrump", "NT", u"\x50", 5)]+coloursInput

class Colour:
    def __init__(self, name, id, symbol, order):
        self.name = name
        self.id = id
        self.symbol = symbol
        self.order = order

    def __str__(self):
        return self.id

    def __lt__(self, other):
        return self.order < other.order

colours = [Colour(x[0], x[1], x[2], x[3]) for x in coloursInput]


class Strain(Colour):
    strains = {}

    def __init__(self, name, id, symbol, order):
        scores = {"NT":(30, 10),
                  "S":(30, 0),
                  "H":(30, 0),
                  "D":(20, 0),
                  "C":(20, 0)}
        Colour.__init__(self, name, id, symbol, order)
        self.baseScore = 0
        self.firstScore = 0
        Strain.strains[id] = self
        Strain.strains[id].baseScore = scores[id][0]
        Strain.strains[id].firstScore = scores[id][1]

    def __str__(self):
        return("{} ".format(self.name))
#
#        return("{} {} {} {}".format(
#            self.name,self.id,self.baseScore,self.firstScore))
    
    @staticmethod
    def fromId(id):
        return Strain.strains[id]

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
    def __init__(self, a):
        self.number = a[0]
        self.symbol = a[1]
        self.order = a[2]

    def __lt__(self, other):
        return self.order < other.order

    def __str__(self):
        return self.symbol


cardValues = [CardValue(x) for x in cardValuesInput]

class Card:
    def __init__(self, colour, value):
       self.value = value
       self.colour = colour

    def __lt__(self, other):
       return (self.colour,self.value) < (other.colour, other.value)

    def sameColour(self,other):
        self.colour == other.colour

    def colour(self):
        return self.colour[3]

    def __str__(self):
        return(self.colour.__str__()+self.value.__str__())
        
    def beats(self, other, trump):
        print(self, other)
        if self.colour == other.colour and self.value > other.value:
            return True
        if other.colour == trump and not(self.colour == trump):
            return False
        return False
            

class Cards:
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

class Bid:
    pattern = re.compile(
        "(?P<tricks>[1-7])(?P<strain>[NT,S,H,D,C]{1,2})(?P<dbl>[PDR])")

    def __init__(self, bidstring):
        match = Bid.pattern.match(bidstring)
        if match:
            self.tricks = match.group("tricks")
            self.strain = Strain.fromId(match.group("strain"))
            self.dbl = match.group("dbl")
        else:
            raise (BaseException("bid exception"))
    
    def __str__(self):
        return("{} {} {}".format(self.tricks,self.strain.name,self.dbl))

deck = Cards([Card(colour, value) for value in cardValues for colour in colours])

class Seat:
    all = []

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


    @staticmethod
    def fromId(id):
        for x in Seat.all:
            if x.id == id:
                return x
        raise (BaseException("seat not found" + id))

allSeatsInput = [("S",0), ("W",1), ("N",2), ('E',3)]
for seat in allSeatsInput:
    Seat(seat[0],seat[1])

Seat.all.sort(key = lambda x: x.order)


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
            print(Bid('{}{}P'.format(t,s)))

    print("N", Seat.fromId("N"))
                       
    for x in (Seat.all):
        print(x)
    for x in range (4):
        print('N + {} {}'.format(x, Seat.fromId("N").getNext(x)))
