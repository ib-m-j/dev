# -*- coding: utf-8 -*-

import bridgecore
import sys

def makeSuitTag(suit):
    return '<img src={suit}.gif alt={suit}>'.format(suit=suit) 

def makeContractText(tricks, suit, seat):
    return '{tricks}{suittag}{seat}'.format(
        tricks=tricks, suittag=makeSuitTag(suit), seat=seat)

template = """
<font class=tablesize>
<table width=100% cellspacing=0 cellpadding=0>
<col width=33%><col width=33%><col width=33%>
<tr valign=top>
  <td rowspan=2>Spil Nr {board}<br>Zone: {zone}<br>{contract}
  <td style=halign:left>{NName}
<tr>
  <td>
      &spades;<font class=spacy>{SN}</font><br>
      <font class=redcolor>&hearts;</font><font class=spacy>{HN}</font><br>
      <font class=redcolor>&diams;</font><font class=spacy>{DN}</font><br>
      &clubs;<font class=spacy>{CN}</font>
<tr>  
  <td class=special>{WName}
  <td rowspan=2>
    <table id=middle width=90% cellspacing=0 cellpadding=0>
    <col width=33%><col width=34%><col width=33%>
      <tr valign=top>
         <td><td style="text-align:center">N<td>
      <tr valign=middle>
         <td>W<td><td style="text-align:right">E
      <tr valign=bottom>
         <td><td style="text-align:center">S<td>
    </table>
  <td class=special>{EName}
<tr>
  <td class=special>
      &spades;<font class=spacy>{SW}</font><br>
      <font class=redcolor>&hearts;</font><font class=spacy>{HW}</font><br>
      <font class=redcolor>&diams;</font><font class=spacy>{DW}</font><br>
      &clubs;<font class=spacy>{CW}</font>
  <td class=special>
      &spades;<font class=spacy>{SE}</font><br>
      <font class=redcolor>&hearts;</font><font class=spacy>{HE}</font><br>
      <font class=redcolor>&diams;</font><font class=spacy>{DE}</font><br>
      &clubs;<font class=spacy>{CE}</font>
<tr>
  <td>
  <td class=special>{SName}
<tr>
  <td class=special style=text-align:top><font class=normalspace>Udspil: </font>{lead}
  <td class=special>
      &spades;<font class=spacy>{SS}</font><br>
      <font class=redcolor>&hearts;</font><font class=spacy>{HS}</font><br>
      <font class=redcolor>&diams;</font><font class=spacy>{DS}</font><br>
      &clubs;<font class=spacy>{CS}</font> 
</table>
</font>
"""

def makeHtmlTemplate(input, x):
    f = open("..\\..\\tests\\testHand{}.html".format(x), "w")
    f.write("""
    <!doctype html public "-//W3C//DTD HTML 4.0//EN" >
            <html>
<head >
<style>
    .tablesize {font-size:2em;}
    #middle {font-size:1.7em; color:white; horizontal-align:left; background-color:green}
    table,td {table-layout:fixed}
    .redcolor {color:red;}
    .spacy {letter-spacing:3px}
    
</style>
</head>
<body><br><br>"""+template.format(**input)+"</body></html>")
    f.close()     


def makeHtmlHand(t):
    print("startinghtml")

    for z in range(4):
        x=4*z
        play = t.plays[x]
        deal = t.deals[t.plays[x].deal]
        cards = deal.cards

        input = dict()
        for seat in bridgecore.Seat.all:
            print(seat)
            for suit in bridgecore.colours:
                print(seat,suit)
                key = '{}{}'.format(suit,seat)

                res = '  '
                for c in cards[seat][suit]:
                    res = res + c.value.symbol
                print(res)

                input[key] = res

        input['zone'] = deal.zone.bridgebaseZone()
        input['board'] = deal.dealNo
        input['contract']= play.bid.htmlStr()
        input['lead']= play.playedOut.htmlStr()

        for (s,name) in play.getBridgeBasePlayers():
            input['{}Name'.format(s)] = name
        makeHtmlTemplate(input, x)
            



#        #the p parameter above is required but does not show the player
#        for (s,name) in playerList:
#            res = res + '&{}n={}'.format(s,name)
#        #the bid destroys other display
#        #res = res + '&a=-{}'.format(bid)
#


#
#
#
#
#
#


if __name__=='__main__':
    #print(makeContractText(2,'S', 'East'))
            
    makeHtmlHand(None)
