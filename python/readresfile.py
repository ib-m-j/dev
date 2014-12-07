# -*- coding: utf-8 -*-
import states
import re
import bridgecore 
import bridgescore
import pickle
import sqlite3

allDeals = {}

def makeDeals(cards):
    for (n,l) in enumerate(cards):
        print(l)
        cardElements = [x.strip() for x in l.split(',')]

        if n % 12 == 0:
            currentDeal = bridgecore.Deal()
            currentDeal.setDealNo(cardElements[0])
            allDeals[int(currentDeal.dealNo)] = currentDeal
            currentDeal.addCards(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif n % 12 == 1:
            parts = cardElements[0].split('/')
            currentDeal.setDealer(bridgecore.Seat.fromDKId(parts[0]))
            currentDeal.setZone(bridgecore.Zone.fromDKName(parts[1]))
            currentDeal.addCards(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif n % 12 == 2 or n % 12 == 3:
            currentDeal.addCards(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif 4 <= n%12 and n % 12 < 8:
            currentDeal.addCards(
                bridgecore.Seat.fromId('W'),
                bridgecore.Colour.fromId(cardElements[0]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[1]])
            if n%12 == 4:
                currentDeal.addCards(
                    bridgecore.Seat.fromId('E'),
                    bridgecore.Colour.fromId(cardElements[3]),
                    [bridgecore.CardValue.fromSymbol(c) for c in cardElements[4]])
            else:
                currentDeal.addCards(
                    bridgecore.Seat.fromId('E'),
                    bridgecore.Colour.fromId(cardElements[2]),
                    [bridgecore.CardValue.fromSymbol(c) for c in cardElements[3]])
        elif n%12 < 12:
            currentDeal.addCards(
                bridgecore.Seat.fromId('S'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
    


def testReadIslev1():
    (parser,statesManager, games, cards, title) = states.setIslevSpilResStates()
    inputFile  = open(r"..\data\allresults.html",'r')
    input = inputFile.read()
    inputFile.close()

    statesManager.advance()
    parser.feed(input)
    for l in games:
        print(l)


    zones = {}
    for (n,l) in enumerate(cards):
        if n % 12 == 0:
            gameno = int(l.split(',')[0]) - 1
        if n % 12 == 1:
            zones[gameno] = l.split(',')[0][2:]
        print(l)
        
    for n in zones.keys():
        print(n, zones[n])

    
        
    
    def checkScore(bidValue, bidStrain, wonTricks, dbl, inZone, score):
        pass
        
#    patternDK = re.compile('(?P<bidder>[xVSN]) (?P<tricks>[1-7])(?P<strain>UT|SP|HJ|RU|KL) +(?P<dbl>[DR])*')

    patternDK = re.compile('((?P<bidder>[ØVSN]) (?P<tricks>[1-7])(?P<strain>UT|SP|HJ|RU|KL) *(?P<dbl>[DR])*)|(?P<other>.*)')

    def getZone(bidder, gamenumber):
        gn = gamenumber // 9 
        if zones[gn] == 'Ingen':
            return False
        if zones[gn] == 'Alle':
            return True
        if zones[gn] =='NS':
            if bidder in 'NS':
                return True
            return False
        if zones[gn] == 'ØV':
            if bidder in 'NS':
                return False
            return True
        
    def getNSres(bidder, NSRes, EWRes):
        if len(NSRes.strip()) != 0:
            return int(NSRes)
        else:
            return -1*int(EWRes)

    def getNSResFromCalc(bidder, res):
        if bidder in 'NS':
            return res
        return -res

    for (n, l) in enumerate(games):
        elements = l.split(',')
        if elements[0][0] == 'S':
            print('Line ', n, elements[0])
        else:
            #print(l)
            #print('trying :', elements[6].strip(),':')
            match = patternDK.match(elements[6].strip())
            if match:
                if not(match.group('other')):
                    tricks = int(match.group("tricks"))
                    strain = bridgecore.Strain.fromDKString(match.group("strain"))
                    dbl = match.group("dbl")
                    if dbl != 'D':
                        dbl = 'P'
                    won = int(elements[7])
                    bidder = match.group('bidder')
                    zone = getZone(bidder, n)
                    NSRes = getNSres(bidder, elements[10], elements[11])
                    calcRes =  bridgescore.getScore(tricks, 
                                                    strain, won, dbl, zone)

                    if NSRes != getNSResFromCalc(bidder,calcRes):
                        print('{} {} {} {} {}:  {}'.format(
                            n // 9, elements[6],elements[7],NSRes,(n//9)%4,
                            getNSResFromCalc(bidder,calcRes)))


            else:
                raise (BaseException("bid exception"))


    for l in title:
        print("title ", l)

    makeDeals(cards)

    keys = [x for x in allDeals.keys()]
    keys.sort()

    for n in keys:
        print(allDeals[n])
    
    print(allDeals[n])
    res = ''
    for b in allDeals[n].hash():
        res = res + '\\x{:x}'.format(b)
    print("now game 30")
    print(res)

    print(allDeals[n])

    res = bridgecore.Deal.fromHash(allDeals[n].hash)
    print(res)
    print('deck',bridgecore.deck)

    connect = sqlite3.connect('..\\database\\tournament.db')
    cur = connect.cursor()
    #cur.execute('insert into deals values(?,?)', (
    #    allDeals[n].hash, allDeals[n].__str__()))

    cur.execute('select * from deals')
    (h, d) = cur.fetchone()
    connect.commit()
    connect.close()
    print('unpickled')
    print("hash: \n",h)
    print("fromhash: \n",bridgecore.Deal.fromHash(h))
    print("stored string: \n", d)
    
    

        
if __name__ == '__main__':
    testReadIslev1()
