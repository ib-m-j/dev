#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import collections
import random

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
        Colour.__init__(self, name, id, symbol, order)
        Strain.strains[id] = self
    
    @staticmethod
    def fromId(id):
        return Strain.strains[id]
            
    
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
            

class Bid:
    def __init__(self, tricks, strain, dbl):
        pass
    


deck = Cards([Card(colour, value) for value in cardValues for colour in colours])
            
        

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
    for c in shuffled:
        print( c)

    res = shuffled.deal([13,13,13])
    for hand in res:
        print(hand.cardsByColour())

    print(Strain.fromId("NT").name)

                       
