# -*- coding: utf-8 -*-

import bridgecore
import sys

def makeSuitTag(suit):
    return '<img src={suit}.gif alt={suit}>'.format(suit=suit) 

def makeContractText(tricks, suit, seat):
    return '{tricks}{suittag}{seat}'.format(
        tricks=tricks, suittag=makeSuitTag(suit), seat=seat)


def makeHtmlTemplate(input, x):
    f = open("..\\..\\tests\\testHand{}.html".format(x), "w")
    f.write("""
    <!doctype html public "-//W3C//DTD HTML 4.0//EN" >
            <html>
<head >
<style>
    .tablesize {font-size:2em;}
    #middle {font-size:1.7em; color:white; 
       horizontal-align:center; width:70%; 
       background-color:green; margin:auto;}
    .redcolor {color:red;}
    .spaced {letter-spacing:3px; padding-left:5px;}
    .right-padding  {padding-right:20px;}
    .top-padding  {padding-top:10px;}
    .blackcard {text-align:center; }
    .redcard {text-align:center; color:red; }
</style>
</head>
<body><br><br>"""+template.format(**input)+"</body></html>")
    f.close()     



template = """
<font class=tablesize>
<table cellspacing=0 cellpadding=0>
<tr valign=top>
  <td rowspan=2>Spil Nr {board}<br>Zone: {zone}<br>{contract}
  <td>{NName}
<tr>
  <td style="display:flex; justify-content:center;">
<table>
  <tr>
    <td class="blackcard">&spades;<td class="spaced">{SN}
  </tr>
  <tr>
    <td class="redcard">&hearts;<td class="spaced">{HN}
  </tr>
  <tr>
    <td class="redcard">&diams;<td class="spaced">{DN}
  </tr>
  <tr>
    <td class="blackcard">&clubs;<td class="spaced">{CN}
  </tr>
</table>
<tr>  
  <td class=right-padding>{WName}
  <td rowspan=2 class="top-padding">
    <div  style="display:flex; justify-content:center;">
    <table id=middle cellspacing=0 cellpadding=0>
    <col width=33%><col width=34%><col width=33%>
      <tr valign=top>
         <td><td style="text-align:center">N<td>
      <tr valign=middle>
         <td style="padding-left:20px;">W
         <td>
         <td style="text-align:right; padding-right:20px;">E
      <tr valign=bottom>
         <td><td style="text-align:center">S<td>
    </table>
</div>
  <td >{EName}
<tr>
 <td style="display:flex; justify-content:center;">
<table>
  <tr>
    <td class="blackcard">&spades;<td class="spaced">{SW}
  </tr>
  <tr>
    <td class="redcard">&hearts;<td class="spaced">{HW}
  </tr>
  <tr>
    <td class="redcard">&diams;<td class="spaced">{DW}
  </tr>
  <tr>
    <td class="blackcard">&clubs;<td class="spaced">{CW}
  </tr>
</table>
 <td  display:flex; justify-content:center;">
<table>
  <tr>
    <td class="blackcard">&spades;<td class="spaced">{SE}
  </tr>
  <tr>
    <td class="redcard">&hearts;<td class="spaced">{HE}
  </tr>
  <tr>
    <td class="redcard">&diams;<td class="spaced">{DE}
  </tr>
  <tr>
    <td class="blackcard">&clubs;<td class="spaced">{CE}
  </tr>
</table>
<tr>
  <td>
  <td >{SName}
<tr>
  <td>Udspil:  {lead}
  <td style="display:flex; justify-content:center;">
<table>
  <tr>
    <td class="blackcard">&spades;<td class="spaced">{SS}
  </tr>
  <tr>
    <td class="redcard">&hearts;<td class="spaced">{HS}
  </tr>
  <tr>
    <td class="redcard">&diams;<td class="spaced">{DS}
  </tr>
  <tr>
    <td class="blackcard">&clubs;<td class="spaced">{CS}
  </tr>
</table>
  </td>
</tr>
</table>

</font>
"""



def makeHtmlHand(t):
    print("startinghtml")

    for z in range(4):
        x=4*z
        play = t.plays[x]
        deal = t.deals[t.plays[x].deal]
        cards = deal.cards

        input = dict()
        for seat in bridgecore.Seat.all:
            #print(seat)
            for suit in bridgecore.colours:
                #print(seat,suit)
                key = '{}{}'.format(suit,seat)

                res = '  '
                for c in cards[seat][suit]:
                    res = res + c.value.symbol
                #print(res)

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
