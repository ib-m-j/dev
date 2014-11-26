 # -*- coding: utf-8 -*-

import html.parser
import sys
from pypeg2 import *
import re
import types

class TagType(Keyword):
    grammar = Enum( K('end'), K('start'))


class CoreActionDef(str):
    grammar = '(', attr('tagName',word),',',\
              attr('tagType', TagType),',',\
              (attr('action', word),\
               attr('parameter',optional('(',word,')'))),')'



class StateDef(str):
    grammar = attr('stateName', word),'(',attr('actions',some(CoreActionDef)),')'


coreActionElements = '((tr, start, newRow)( tr, end, flushRow)( td, start, newData) ( td, end, flushData)( table, end, flushTable))'

standardState = 'standard ' + coreActionElements



class Action:
    def __init__(self, definition):
        self.tag = definition.tagName
        self.tagType =   definition.tagType.name
        self.callBack =  definition.action
        self.parametre = definition.parameter

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
        print(states)
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
        print('remainingnnn',self.remainingStates)
        if len(self.remainingStates) > 0:
            self.currentState = self.remainingStates[0]
            self.remainingStates = self.remainingStates[1:]
            print('tuplecomparison', isinstance(self.remainingStates, tuple))
            print(self.currentState, 'goingtostart',isinstance(self.currentState, State) )
            if not(isinstance(self.currentState, list) or isinstance(
                    self.currentState, list)):
                print('starting new state')
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
        self.name = actionDefs.stateName
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

    def start(self, mgr):
        pripnt("starting state start")
        self.mgr = mgr
        self.parser.noCallbacks()
        self.parser.setCallbacks(self.actions)
        self.parser.setDataTarget(self.addData)
        self.parser.deActivateData()
    
    def checkExists(self, action):
        res = eval('self.'+action.callBack)
        print(res)
        return res
               


class SkipState(State):

    def start(self, mgr):
        print("starting skipstart")
        self.mgr = mgr
        self.parser.noCallbacks()
        self.parser.setCallbacks(self.actions)
        self.parser.deActivateData()

    def skip(self):
        print('got skip now at', self.count)
        if self.count == 0:
            self.mgr.advance()
        else:
            self.count = self.count - 1

gotoTemplate = '{} ((table, start, skip ({})))'

def gotoTableNo(no, parser):
    res = parse(gotoTemplate.format('gotoTable', no), StateDef)
    
    state =  SkipState(res, parser)
    state.count = no
    return state


class TableState(State):
    #def __str__(self):
    #    res = ''
    #    for r in self.rows:
    #        for d in r:
    #            res = res + '{}, '.format(d.__str__())
    #        res = res[:-2] +'\n'
    #    return res

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
    
               
    def newRow(self):
        print('got callback row')
        self.currentRow = []
        pass

    def flushRow(self):
        print('got flush row')
        self.rows.append(self.currentRow)
        pass

    def newData(self):
        print('got callback data')
        self.currentData = Data()
        self.parser.activateData()
        pass

    def flushData(self):
        self.currentRow.append(self.currentData)
        self.parser.deActivateData()
        pass

    def flushTable(self):
        print('got flush table')
        print(self)
        self.mgr.advance()
        pass

    def skip(self):
        pass

    def addData(self, data):
        if self.currentData:
            print('adding', data)
            self.currentData.addData(data)






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
        print('data activated')
        self.dataActive = True

    def deActivateData(self):
        print('Data de activates')
        self.dataActive = None

    def handle_starttag(self, tag, attrs):
        if self.count > 0:
            self.count = self.count - 1
            if self.count == 0:
                sys.exit(0)
        if tag in self.startTags.keys():
            self.startTags[tag]()

    def handle_endtag(self, tag):
        if tag in self.endTags.keys():
            self.endTags[tag]()

    def handle_data(self, data):
        if self.dataTarget and self.dataActive:
            self.dataTarget(data.strip())



if __name__ == '__main__':

    parser = HTMLParserTableBased()

    res = parse(standardState, StateDef)

    #print(res.stateName)
    #for x in res.actions:
    #    print(x.tagName, x.tagType.name, x.action, x.parameter)
    #    print(x.__dict__)
    state = TableState(res, parser)
    mgr = StatesManager(parser, (gotoTableNo(4, parser), State), None)
    #mgr = StatesManager(parser, (State, State), None)
    inputFile  = open(r"..\data\allresults.html",'r')
    input = inputFile.read()
    inputFile.close()

    map = str.maketrans('æøåÆØÅ', 'xxxxxx')
    res = input.translate(map)
    mgr.advance()
    parser.feed(res)

# a small change
