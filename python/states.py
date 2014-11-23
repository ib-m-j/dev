import html.parser
import sys
from pypeg2 import *
import re

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
    def __init__(self, name = 'none'):
        self.name = name
        self.value = 'none'

    def setData(self, data):
        self.value = data

    def addData(self, data):
        self.value = self.value + data

class State:
    def __init__(self, actionDefs, parser):
        self.name = actionDefs.stateName
        self.actions = []
        for actionDef in actionDefs.actions:
            newAction = Action(actionDef)
            self.actions.append(newAction)
            self.checkExists(newAction)
            newAction.callBack = res

        self.rows = []
        self.currentRow = None
        self.currentData = None
        self.parser = parser
        

    def __str__(self):
        return self.name
        
    def run(self, input):
        self.parser.setCallbacks(self.actions)
        self.parser.setDataTarget(self.addData)
        self.parser.parse(input, StateDef)
    
    def checkExists(self, action):
        res = eval('self.'+action.callBack)
        print(res)
        return res
               
    def newRow(self):
        self.currentRow = []
        pass

    def flushRow(self):
        self.rows.append(self.currentRow)
        pass

    def newData(self):
        self.currentData = Data()
        self.parser.activateData()
        pass

    def flushData(self):
        self.currentRow.append(self.currentData)
        self.parser.deActivateData()
        pass

    def flushTable(self):
        pass

    def skip(self):
        pass

    def addData(self):
        self.currentData.addData()



class HTMLParserTableBased(html.parser.HTMLParser):
    level = 0
    lastTag = ''
    allTables = []
    gotoTable = 0
    skipRows = 0
    printRows = 0
    rowdata = []
    definition = []

    def settags(self):
        self.count = 6 #for testing
        self.startTags = {}
        self.endTags = {}
        self.dataTarget = None

 
    def setCallbacks(self, actions):
        self.startTags = {}
        self.endTags = {}
        if len(actions) == 0:
            return
        for action in actions:
            if action.tagType == 'start':
                self.startTags[action.tag] = action.callBack
            elif type == 'end':
                self.endTags[action.tag]  = action.callBack
        else:
            pass

    def setDataTarget(self, callBack):
        self.dataTarget = callBack

    def activateData(self):
        self.dataActive = True

    def deActivateData(self):
        self.dataActive = None

    def handle_starttag(self, tag, attrs):
        #print("saw tag ", tag)
        if tag in self.startTags.keys():
            self.startTags[tag].callBack()

    def handle_endtag(self, tag):
        if tag in self.endTags.keys():
            self.endTags[tag].callBack()

    def handle_data(self, data):
        if self.dataTarget:
            self.dataTarget(data)



if __name__ == '__main__':

    parser = HTMLParserTableBased()

    res = parse(standardState, StateDef)

    print(res.stateName)
    for x in res.actions:
        print(x.tagName, x.tagType.name, x.action, x.parameter)
        print(x.__dict__)
    state = State(res, parser)
    inputFile  = open(r"..\data\allresults.html",'r')
    
    state.run(inputFile.read())