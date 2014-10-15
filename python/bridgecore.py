#!/usr/bin/python
# -*- coding: iso-8859-1 -*-



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

colours = [Colour("Spades", "S", u"\x50", 4),
            Colour("Hearts", "H", u"\x50", 3),
            Colour("Diamonds", "D", u"\x50", 2),
            Colour("Clubs", "C", u"\x50", 1)]

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

class Deck:
    cards = {}
    cards1 = []

#    def __init__(self):
#        for value in cardValues:
#            for colour in colours:
#                Deck.cards1.append(Card(colour, value))
        

    def __init__(self):
        for value in cardValues:
            for colour in colours:
                print("added:"+value.__str__()+colour.__str__())
                Deck.cards[(colour.id, value.symbol)
                ]  =   Card(colour, value)
        

if __name__ == '__main__':
    Deck()
    v = Deck.cards.values()
    k = [x for x in v]
    k.sort()
    for c in k:
        print(c)
