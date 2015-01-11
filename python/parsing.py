#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


from pypeg2 import *
import re

tricks = re.compile('[1-7]')
strain = re.compile('UT|SP|HJ|RU|KL') 
dbl = re.compile('[PDR]*')
passed = re.compile('P')
seat = re.compile('S|V|N|Ø')

class PlayedBid(str):
    grammar = (attr('seat', seat), contiguous(attr('tricks', tricks), attr('strain', strain)), optional(attr('dbl', dbl)))

class PassedHand(str):
    grammar = attr('passed', str)

class Bid(str):
    grammar = [attr('played',PlayedBid), attr('passed', PassedHand)]


#res = parse('Ø 6UT', Bid)
#print(isinstance(res, Bid))
#print(res.__dict__)
#print(res.played.seat)
##
#            
#
#res = parse('P', PassedHand)
#print(res.__dict__)
#print(res.passed)
