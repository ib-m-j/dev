# -*- coding: utf-8 -*-
import html.parser
import sys
#from pypeg2 import *
import pypeg2
import re
import types
from bridgecore import Strain
import bridgescore

games = []
cards = []
title = []

class TagType(pypeg2.Keyword):
    grammar = pypeg2.Enum( pypeg2.K('end'), pypeg2.K('start'))

class CoreActionDef(str):
    grammar = '(', pypeg2.attr('tagName',pypeg2.word),',',\
              pypeg2.attr('tagType', TagType),',',\
              (pypeg2.attr('action', pypeg2.word),\
               pypeg2.attr('parameter',pypeg2.optional('(',pypeg2.word,')'))),')'

class StateDef(str):
    grammar = pypeg2.attr(
        'stateName', pypeg2.word),'(',pypeg2.attr(
            'actions',pypeg2.some(CoreActionDef)),')'

coreActionElements = '((tr, start, newRow)( tr, end, flushRow)( td, start, newData) ( td, end, flushData)( table, end, flushTable))'

cardActionElements = '((tr, start, newRow)( tr, end, flushRow)( td, start, newData) ( td, end, flushData)( table, end, flushTable)(img, start, cardColour))'

oneLineStates = 'oneline ' + '((tr, start, newRow)(td, start, newData)(td, end, flushData)(tr, end, flushRowAndExit))'

oneHeaderStates = 'oneline ' + '((tr, start, newRow)(th, start, newData)(th, end, flushData)(td, start, newData)(td, end, flushData)(tr, end, flushRowAndExit))'

titleStates = 'title' + '((head, start, newRow) (head, end, flushRowAndExit) (title, start, newData) (title, end, flushData))'

#standardStates = 'standard ' + coreActionElements
tournamentStates = 'tournament ' + cardActionElements

#list of parserdefined statedefinitions to be used
tournamentActions = pypeg2.parse(tournamentStates, StateDef)
oneLineActions = pypeg2.parse(oneLineStates, StateDef)
oneHeaderActions = pypeg2.parse(oneHeaderStates, StateDef)
titleActions = pypeg2.parse(titleStates, StateDef)



class Action:
    def __init__(self, definition):
        self.tag = definition.tagName
        self.tagType =   definition.tagType.name
        self.callBack =  definition.action
        self.parametre = definition.parameter

    def __str__(self):
        return '{}, {}'.format(self.tag, self.tagType)

class Data:
    def __init__(self, name = ''):
        self.name = name
        self.value = ''

    def setData(self, data):
        self.value = data

    def addData(self, data):
        self.value = self.value + data

    def __str__(self):
        return self.value

class StatesManager:
    def __init__(self, parser, states, parent):
        #print(states)
        self.parser = parser
        self.states = states
        self.remainingStates = self.states
        self.currentState = None
        self.parent = parent
        if isinstance(self.states, list):
            self.type = 'loop'
        else:
            self.type = 'tuple'

    def advance(self):
        #debugging
        #if self.currentState:
        #    print(self.currentState)
        if len(self.remainingStates) > 0:
            self.currentState = self.remainingStates[0]
            #print("new state")
            #print(self.currentState)
            self.remainingStates = self.remainingStates[1:]
            if isinstance(self.currentState, State):
                self.currentState.start(self)
            else:
                self.child = StatesManager(self.parser, self.currentState, self)
                self.child.advance()
        else:
            if self.type == 'tuple':
                print('exiting')
                self.exit()
            else:
                self.remainingStates = self.states
                self.advance()
                
    def exit(self):
        if self.parent:
            self.parent.advance()
        else:
            self.parser.noCallbacks()


class State:
    def __init__(self, actionDefs, parser):
        self.actions = []
        for actionDef in actionDefs.actions:
            newAction = Action(actionDef)
            self.actions.append(newAction)
            res = self.checkExists(newAction)
            newAction.callBack = res

        self.parser = parser
        
    def __str__(self):
        res ="actions: "
        for a in self.actions:
            res = res + a.tag + ", "
        return res

    def reset(self):
        pass

    @staticmethod
    def getAttr(key, attrs):
        res = None
        for (k,v) in attrs:
            if k == key:
                res = v
                break
        return res
        


    def checkExists(self, action):
        res = eval('self.'+action.callBack)
        #print(res)
        return res
               

class TableState(State):
    def __init__(self, actionDefs, parser, storage):
        self.storage = storage
        State.__init__(self, actionDefs, parser)

#    def __str__(self):
#        res = str(len(self.rows))+'\n'
#        for c,r in enumerate(self.rows):
#            res = res + '{}:'.format(c)
#            for d in r:
#                res = res + '{}, '.format(d.__str__())
#            res = res[:-2] +'\n'
#        return res


    def start(self, mgr):
        #print('starting tablestate')
        self.mgr = mgr
        self.rows = []
        self.currentRow = []
        self.currentData = None
        self.parser.noCallbacks()
        self.parser.setCallbacks(self.actions)
        self.parser.setDataTarget(self.addData)
        self.parser.deActivateData()
    
    def cardColour(self, attrs):
        attrValue = State.getAttr('src', attrs)
        if attrValue:
            d = Data()
            d.addData(attrValue[0])
            self.currentRow.append(d)
        
               
    def newRow(self, attrs = None):
        #print('got callback row')
        self.currentRow = []
        pass

    def flushRow(self):
        #print('got flush row')
        #for l in self.currentRow:
        #    print(l.value)
        self.rows.append(self.currentRow)
        pass

    def flushRowAndExit(self):
        #print('got flushrow and exit')
        self.rows.append(self.currentRow)
        for r in self.rows:
            line = ''
            for d in r:
                if d:
                    line = line + '{}, '.format(d.value)
            self.storage.append(line[:-2])
        self.rows = []
        self.mgr.advance()

    def newData(self, attrs = None):
        #print('got callback data')
        
        attrValue = State.getAttr('name', attrs)
        if attrValue:
            d = Data()
            d.addData(attrValue)
            self.currentRow.append(d)

        self.currentData = Data()
        self.parser.activateData()
        pass

    def flushData(self):
        #print('got flush data')
        self.currentRow.append(self.currentData)
        #res = ''
        #for d in self.currentRow:
        #    res = res +d.value + ', '
        #print('register data: ', self.currentData)
        self.parser.deActivateData()
        pass

    def flushTable(self):
        #print('got flush table')
        for r in self.rows:
            line = ''
            for d in r:
                line = line + '{}¤ '.format(d.value)
            self.storage.append(line[:-2])
        #print(self.storage)
        self.rows = []
        self.mgr.advance()
        pass

    def skip(self):
        pass

    def addData(self, data):
        if self.currentData:
            #print('adding', data)
            self.currentData.addData(data)

class SkipState(State):

    def start(self, mgr):
        #print("starting skipstate")
        self.mgr = mgr
        self.parser.noCallbacks()
        self.parser.setCallbacks(self.actions)
        self.parser.deActivateData()
        #for a in self.actions:
        #    print(a)

    def setSkipNo(self, no):
        self.count = no
        self.orgCount = no

    def reset(self):
        #print('resttintg to', self.count)
        self.count = self.orgCount

    def skip(self, attrs = None):
        #print('got skip now at', self.count)
        if self.count == 0:
            self.reset()
            self.mgr.advance()
        else:
            self.count = self.count - 1

gotoTemplate = '{} (({}, start, skip ({})))'
skipTemplate = '{} (({}, end, skip ({})))'


def gotoTableNo(no, parser):
    res = pypeg2.parse(gotoTemplate.format('gotoTable', 'table', no), StateDef)
    
    state =  SkipState(res, parser)
    state.setSkipNo(no)
    return state

def skipRowNo(no, parser):
    res = pypeg2.parse(skipTemplate.format('skipRow', 'tr', no), StateDef)
    state = SkipState(res, parser)
    state.setSkipNo(no)
    return state


def skipTableNo(no, parser):
    res = pypeg2.parse(skipTemplate.format('skipTable', 'table', no), StateDef)
    state = SkipState(res, parser)
    state.setCount = no
    return state


class HTMLParserTableBased(html.parser.HTMLParser):

    def noCallbacks(self):
        self.count = 0 #for testing
        self.startTags = {}
        self.endTags = {}
        self.dataTarget = None
        self.dataActive = False

 
    def setCallbacks(self, actions):
        self.startTags = {}
        self.endTags = {}
        if len(actions) == 0:
            return
        for action in actions:
            if action.tagType == 'start':
                self.startTags[action.tag] = action.callBack
            elif action.tagType == 'end':
                self.endTags[action.tag]  = action.callBack
        else:
            pass


    def setDataTarget(self, callBack):
        self.dataTarget = callBack

    def activateData(self):
        #print('data activated')
        self.dataActive = True

    def deActivateData(self):
        #print('Data de activates')
        self.dataActive = None

    def handle_starttag(self, tag, attrs):
        if self.count > 0: #testing
            self.count = self.count - 1
            if self.count == 0:
                sys.exit(0)
        if tag in self.startTags.keys():
            self.startTags[tag](attrs)

    def handle_endtag(self, tag):
        if tag in self.endTags.keys():
            #print("got endtag")
            #print(tag)
            self.endTags[tag]()

    def handle_data(self, data):
        if self.dataTarget and self.dataActive:
            self.dataTarget(data.strip())


def setIslevPairResStates():
    games = []
    cards = []
    title = []
    parser = HTMLParserTableBased()

    #the definition below works with pairs islev 1140 mellemrunde
    #par 3/11 20152.sektion a rækken
    gamesResults = TableState(tournamentActions, parser, games)
    hands = TableState(tournamentActions, parser, cards)
    tournamentTitle = TableState(oneHeaderActions, parser, title)
    gameNo = TableState(oneHeaderActions, parser, games)
    clubName = TableState(titleActions, parser, title)

    mgr = StatesManager(parser, (clubName, gotoTableNo(0, parser), 
                                 tournamentTitle, gotoTableNo(0, parser),
                                 [gotoTableNo(1, parser), gameNo,
                                  gotoTableNo(0, parser), skipRowNo(1, parser), 
                                 gamesResults,gotoTableNo(1, parser),
                                  hands]), None)

    return (parser, mgr, games, cards, title)


def setIslevTeamResStates():
    games = []
    cards = []
    title = []
    parser = HTMLParserTableBased()

    gamesResults = TableState(tournamentActions, parser, games)
    hands = TableState(tournamentActions, parser, cards)
    tournamentTitle = TableState(oneHeaderActions, parser, title)
    gameNo = TableState(oneHeaderActions, parser, games)
    clubName = TableState(titleActions, parser, title)

    mgr = StatesManager(parser, (
        clubName, gotoTableNo(0, parser), tournamentTitle, 
        gotoTableNo(6, parser),[gotoTableNo(0,parser), 
        hands, gotoTableNo(0, parser), skipRowNo(0,parser), gamesResults,
         gotoTableNo(0,parser)]), None)

    return (parser, mgr, games, cards, title)

if __name__ == '__main__':

    inputFile  = open(r"..\data\allresults.html",'r')
    input = inputFile.read()
    inputFile.close()

    mgr.advance()
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
        gn = gamenumber // 8 
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
        #print('trying :', elements[6].strip(),':')
        match = patternDK.match(elements[6].strip())
        if match:
            if not(match.group('other')):
                tricks = int(match.group("tricks"))
                strain = Strain.fromDKString(match.group("strain"))
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
                        n // 8, elements[6],elements[7],NSRes,(n//8)%4,
                        getNSResFromCalc(bidder,calcRes)))
               

        else:
            raise (BaseException("bid exception"))

        
        
