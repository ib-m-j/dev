#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pypeg2 import *
import re

tricks = re.compile('[1-7]')
strain = re.compile('UT|SP|HJ|RU|KL') 
dbl = re.compile('[PDR]*')
passed = re.compile('P')
seat = re.compile('S|V|N|Ø')
notPlayed = re.compile('\(Justeret\)')

class PlayedBid(str):
    grammar = (attr('seat', seat), contiguous(attr('tricks', tricks), attr('strain', strain)), optional(attr('dbl', dbl)))

class PassedHand(str):
    grammar = attr('passed', passed)

class NotPlayed(str):
    grammar = attr('not_played', notPlayed)

class Bid(str):
    grammar = [attr('played',PlayedBid), attr('passed', PassedHand), 
               attr('not_played', NotPlayed)]


if __name__ == '__main__':


    res = parse('Ø 6UT', Bid)
    print(res.played.__dict__)

    res = parse('P', Bid)
    print(res.passed.__dict__)

    res = parse('(Justeret)', Bid)
    print(res.__dict__)

#print(isinstance(res, Bid))
#print(res.__dict__)
#print(res.played.seat)
##
#            
#
#res = parse('P', PassedHand)
#print(res.__dict__)
#print(res.passed)
