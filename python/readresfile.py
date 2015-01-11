# -*- coding: utf-8 -*-
import states
import re
import bridgecore 
import bridgescore
import pickle
import sqlite3
import datetime
import locale
import tournament
import sys

def makeDeals(cards, allDeals):
    for (n,l) in enumerate(cards):
        #print(l)
        if n >= 12*(len(cards) //12):
            print('breaking', n, len(cards))
            break

        cardElements = [x.strip() for x in l.split(',')]

        if n % 12 == 0:
            currentDeal = bridgecore.Deal()
            currentDeal.setDealNo(cardElements[0])
            allDeals[int(currentDeal.dealNo)] = currentDeal
            currentDeal.addSuit(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif n % 12 == 1:
            parts = cardElements[0].split('/')
            currentDeal.setDealer(bridgecore.Seat.fromDKId(parts[0]))
            currentDeal.setZone(bridgecore.Zone.fromDKName(parts[1]))
            currentDeal.addSuit(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif n % 12 == 2 or n % 12 == 3:
            currentDeal.addSuit(
                bridgecore.Seat.fromId('N'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])
        elif 4 <= n%12 and n % 12 < 8:
            currentDeal.addSuit(
                bridgecore.Seat.fromId('W'),
                bridgecore.Colour.fromId(cardElements[0]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[1]])
            if n%12 == 4:
                currentDeal.addSuit(
                    bridgecore.Seat.fromId('E'),
                    bridgecore.Colour.fromId(cardElements[3]),
                    [bridgecore.CardValue.fromSymbol(c) for c in cardElements[4]])
            else:
                currentDeal.addSuit(
                    bridgecore.Seat.fromId('E'),
                    bridgecore.Colour.fromId(cardElements[2]),
                    [bridgecore.CardValue.fromSymbol(c) for c in cardElements[3]])
        elif n%12 < 12:
            currentDeal.addSuit(
                bridgecore.Seat.fromId('S'),
                bridgecore.Colour.fromId(cardElements[1]),
                [bridgecore.CardValue.fromSymbol(c) for c in cardElements[2]])

    return allDeals


def largeIslevPairs():
    (parser,statesManager, games, cards, title) = states.setIslevPairResStates()
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

    allDeals = {}
    makeDeals(cards, allDeals)

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

    #connect = sqlite3.connect('..\\database\\tournament.db')
    #cur = connect.cursor()
    #cur.execute('insert into deals values(?,?)', (
    #    allDeals[n].hash, allDeals[n].__str__()))

    #cur.execute('select * from deals')
    #(h, d) = cur.fetchone()
    #connect.commit()
    #connect.close()
    #print("fromhash: \n",bridgecore.Deal.fromHash(h))
    #print("stored string: \n", d)
    

def searchTournamentType(text):
    pairTexts = 'par|pair'
    teamTexts = 'hold|team'
    pairSearcher = re.compile(pairTexts, re.IGNORECASE)
    teamSearcher = re.compile(teamTexts, re.IGNORECASE)
    if pairSearcher.search(text):
        return 'PAIR'
    elif teamSearcher.search(text):
        return 'TEAM'
    raise BaseException("no tournament type fouond")
    
def parseIslevTitle(title):
    elements = title.split(',')
    tournamentName = elements[0].strip()
    tournamentType = searchTournamentType(tournamentName)
    date = elements[1].strip()
    section = elements[2].strip()
    #bracket = elements[3].strip() not always there
    print(tournamentName)
    print(tournamentType)
    print(date)
    print(section)
    #print(bracket)

def basicIslevPairs(input):
    (parser,statesManager, games, cards, title) = states.setIslevPairResStates()
    #inputFile  = open(r"..\data\allresults.html",'r')
    #input = inputFile.read()
    #inputFile.close()

    print("doing pairs")
    statesManager.advance()
    try:
        parser.feed(input)
        parseIslevTitle(title[1])
    except:
        print('could not read file')
    else:
        print('games')
        for l in games:
            print(l)
        print('cards')
        for l in cards:
            print( l)

def basicIslevTeams(input, t):
    (parser,statesManager, games, cards, title) = states.setIslevTeamResStates()
    #inputFile  = open(r"..\data\mellemrundehold.http",'r')
    #input = inputFile.read()
    #inputFile.close()

    statesManager.advance()
    try:
        parser.feed(input)
    except:
        print('could not read file')
    else:
        #parseIslevTitle(title[1]) to many changes to thi8s string no parse yet
        t.setName(title[1]) #gets set twice but should be ok
        dealNo = t.getNextDeal()
        
        for (n,l) in enumerate(games):
            if n % 2 == 0:
                playElements1 = [x.strip() for x in l.split(',')]
            else:
                playElements2 = [x.strip() for x in l.split(',')]
                tableNo = int(playElements1[0])
                teamNS = playElements1[1]
                NPlayer = playElements1[2]
                teamEW = playElements1[3]
                EPlayer = playElements1[4]
                bid = bridgecore.Bid.fromIslevString(playElements1[5])
                if not(bid.isPlayedBid()):
                    tricks = int(playElements1[7])
                    NSScore = int(playElements1[8])
                    IMPScore = int(playElements1[9])
                else:
                    tricks = int(playElements1[8])
                    NSScore = int(playElements1[9])
                    IMPScore = int(playElements1[10])
                SPlayer = playElements2[0]
                WPlayer = playElements2[1]
                
                if tableNo == 1:
                    dealNo = dealNo + 1

                t.addPlay(dealNo, [
                    (teamNS, SPlayer), 
                    (teamEW, WPlayer), 
                    (teamNS, NPlayer), 
                    (teamEW, EPlayer)],
                          bid, tricks, NSScore)

        allDeals = {}

        makeDeals(cards, allDeals)
        for (id, deal) in allDeals.items():
            t.addDeal(id, deal)

    #for n in keys:
    #    print(allDeals[n])
    
    



        
if __name__ == '__main__':
    #print(locale.getlocale())
    #locale.setlocale(locale.LC_ALL, 'da_dk')
    largeIslevPairs()
    #basicIslevTeams()
    #basicIslevPairs()
    
    #dateString = '25. oktober 2014'
    #print(dateString)
    #date = datetime.datetime.strptime(dateString,'%d. %B %Y')
    #print(date.year, date.month, date.day)
    
