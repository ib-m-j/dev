#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

class Colour:
    def __init__(self, name, short, symbol, order):
        self.name = name
        self.short = short
        self.symbol = symbol
        self.order = order

    def __str__(self):
        return self.name+self.short+self.symbol



if __name__ == '__main__':
    for i in range(5):
        print(i, "\i")



    c1 = Colour("Spades", "S", u"\x50", 1)
    c2 = Colour("Hearts", "H", u"\x50", 2)
    c3 = Colour("Diamonds", "D", u"\x50", 3)
    c4 = Colour("Clubs", "C", u"\x50", 4)

    
