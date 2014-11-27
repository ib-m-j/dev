 # -*- coding: utf-8 -*-
import html.parser
import sys
from pypeg2 import *
import re
import types


games = []
cards = []

class TagType(Keyword):
    grammar = Enum( K('end'), K('start'))


class CoreActionDef(str):
    grammar = '(', attr('tagName',word),',',\
              attr('tagType', TagType),',',\
              (attr('action', word),\
               attr('parameter',optional('(',word,')'))),')'



class StateDef(str):
    grammar = attr('stateName', word),'(',attr('actions',some(CoreActionDef)),')'


coreActionElements = '((tr, start, newRow)( tr, end, flushRow)( td, start, newData) ( td, end, flushData)( table, end, flushTable)(img, start, cardColour))'

standardState = 'standard ' + coreActionElements



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
        if len(self.remainingStates) > 0:
            self.currentState = self.remainingStates[0]
            self.remainingStates = self.remainingStates[1:]
            if isinstance(self.currentState, State):
                self.currentState.start(self)
            else:
                self.child = StatesManager(parser, self.currentState, self)
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
        return self.name
        pass

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
        


#    def start(self, mgr):
#        pripnt("starting state start")
#        self.mgr = mgr
#        self.parser.noCallbacks()
#        self.parser.setCallbacks(self.actions)
#        self.parser.setDataTarget(self.addData)
#        self.parser.deActivateData()
#    
    def checkExists(self, action):
        res = eval('self.'+action.callBack)
        print(res)
        return res
               

class TableState(State):
    def __init__(self, actionDefs, parser, storage):
        self.storage = storage
        State.__init__(self, actionDefs, parser)

    def __str__(self):
        res = str(len(self.rows))+'\n'
        for c,r in enumerate(self.rows):
            res = res + '{}:'.format(c)
            for d in r:
                res = res + '{}, '.format(d.__str__())
            res = res[:-2] +'\n'
        return res


    def start(self, mgr):
        print('starting tablestate')
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
        print('got flush row')
        self.rows.append(self.currentRow)
        pass

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
                line = line + '{}, '.format(d.value)
            self.storage.append(line[:-2])
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
    res = parse(gotoTemplate.format('gotoTable', 'table', no), StateDef)
    
    state =  SkipState(res, parser)
    state.setSkipNo(no)
    return state

def skipRowNo(no, parser):
    res = parse(skipTemplate.format('skipRow', 'tr', no), StateDef)
    state = SkipState(res, parser)
    state.setSkipNo(no)
    return state


def skipTableNo(no, parser):
    res = parse(skipTemplate.format('skipTable', 'table', no), StateDef)
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
        if self.count > 0:
            self.count = self.count - 1
            if self.count == 0:
                sys.exit(0)
        if tag in self.startTags.keys():
            self.startTags[tag](attrs)

    def handle_endtag(self, tag):
        if tag in self.endTags.keys():
            self.endTags[tag]()

    def handle_data(self, data):
        if self.dataTarget and self.dataActive:
            self.dataTarget(data.strip())



if __name__ == '__main__':

    parser = HTMLParserTableBased()

    res = parse(standardState, StateDef)

    gamesResults = TableState(res, parser, games)
    hands = TableState(res, parser, cards)



    #mgr = StatesManager(parser, (gotoTableNo(8, parser), gotoTableNo(4, parser)), None)
    mgr = StatesManager(parser, (gotoTableNo(4, parser), 
                                 skipRowNo(1, parser), 
                                 [gamesResults,gotoTableNo(1, parser),
                                  hands, gotoTableNo(2, parser),
                                  skipRowNo(1, parser)]), None)
    #mgr = StatesManager(parser, (gotoTableNo(4, parser), 
    #                             skipRowNo(1, parser), 
    #                             gamesResults,gotoTableNo(1,parser),
    #                             hands, gotoTableNo(2, parser),
    #                              skipRowNo(1, parser), gamesResults), None)
    #mgr = StatesManager(parser, [state, state], None)
    inputFile  = open(r"..\data\allresults.html",'r')
    input = inputFile.read()
    inputFile.close()

    map = str.maketrans('æøåÆØÅ', 'xxxxxx')
    res = input.translate(map)
    mgr.advance()
    parser.feed(res)
    for l in games:
        print(l)

    for l in cards:
        print(l)
# a small change
