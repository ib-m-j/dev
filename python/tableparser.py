import html.parser
import sys
from pypeg2 import *
import re




class TagType(Keyword):
    grammar = Enum( K('end'), K('start'))

class Action(Keyword):
    grammar = Enum( K('newTable'), K('newRow'), K('newData'), K('flushData'))

class BasicObject(str):
    grammar = '(', name(),',',attr('tagtype', TagType),',',\
              (attr('action', Action),attr('parameter',optional('(',word,')'))),')'

class EndAction(str):
    grammar = '(', name(), ',', attr('tagtype', TagType),')'

class Loop(Keyword):
    grammar = Enum( K('loop'))

class ParserDef(str):
    grammar = [(attr('loop', Loop), '('), (attr('endaction', EndAction)), \
               (attr('basic',BasicObject)),')'] , attr('rest',restline)


tableParseDef1 = 'loop((endtag, end)(tag, start, finish)loop((tag1, end, skip(a))))(tag2, start, finish)(tag3, end, inc)'

tableDescribing = 'loop((table, end)(table, start, newTable)\
loop((tr, end)(tr, start, newRow)loop((tr, end)(td, start, newData)(td,end,flushData))))'

tableTest = '(table,start,newTable)(tr,end,newRow)(td,start,newData)(td,end,flushData)'

tablesOnly = 'loop((table, end)(table, start, newTable))'

def parseValue(res, attr):
    return attr in res.__dict__


class Table:
    def __init__(self, name = 'none'):
        self.rows = []
        self.name = name

    def addRow(self, row):
        self.rows.append(row)

class Row:
    def __init__(self, name = 'none'):
        self.data = []
        self.name = name
    
    def addData(self, data):
        self.data.append(data)

class Data:
    def __init__(self, name = 'none'):
        self.value = name

    def setData(self, data):
        self.value = data

class TableParser:
    tables = []

    def __init__(self, parser, parent, type):
        self.states = []
        self.endactions = []
        self.parent = parent
        self.input = ''
        self.level = 0
        self.type = type
        self.parser = parser
        self.callback = {'newTable': self.newTable,
                         'newRow': self.newRow,
                         'newData': self.newData,
                         'flushData': self.flushData}
                         

    def setInput(self, input):
        self.input = input

    def setStates(self, level):
        self.level = level
        while len(self.input) > 0:
            print (self.input)
            res = parse(self.input, ParserDef)
            if parseValue(res, 'loop'):
                child = TableParser(parser, self, res.loop)
                child.setInput(res.rest)
                child.setStates(level + 1)
                self.states.append(child)
            elif parseValue(res, 'basic'):
                self.states.append((res.basic.name,res.basic.tagtype,
                                    res.basic.action, res.basic.parameter))
                self.input = res.rest
            elif parseValue(res, 'endaction'):
                self.endactions.append((res.endaction.name,
                                        res.endaction.tagtype))
                self.input = res.rest
            else:
                if level> 0:
                    self.parent.setInput(res.rest)
                break


    def __str__(self):
        res = '{} type {} length {}\n'.format(
            self.level, self.type, len(self.states))
        res = res + '{}endactions: '.format(self.level*'  ')
        for s in self.endactions:
            res = res + '{}, '.format(s)
        res = res + '\n'
        for s in self.states:
            if isinstance(s, TableParser):
                res = res + '{}child {}\n'.format(self.level*'  ',s.__str__())
            else:
                res = res + '{}{}\n'.format(self.level*'  ',s)
        
        return res

    

    def newTable(self):
        print('got callback table')
        newTable = Table()
        TableParser.tables.append(newTable)
        TableParser.currentTable = newTable
        self.advance()
        
    def newRow(self):
        print('got callback row')
        newRow = Row()
        TableParser.currentTable.addRow(self)
        TableParser.currentRow = newRow
        self.advance()

    def newData(self):
        print('got callback data')
        newData = Data()
        TableParser.currentRow.addData(newData)
        TableParser.currentData  = newData
        self.parser.dataTarget = self.addData
        self.advance()

    def addData(self, data):
        if TableParser.currentData:
            TableParser.currentData = TableParser.currentData.setData(data)
        
    def flushData(self):
        self.parser.dataTarget = None
        self.advance()

    def levelUp(self):
        if self.parent:
            self.parent.cont()

    def advance(self):
        #print('advancwe', len(self.remainingStates))
        if len(self.remainingStates) > 0:
            nextWait = self.remainingStates[0]
            #print("states", nextWait.__dict__)
            #print(nextWait[0].name, nextWait[1].name, nextWait[2].name)
            self.remainingStates = self.remainingStates[1:]
            #print("!!!!!!!!!!!!", self.type)
            if isinstance(nextWait, TableParser):
                nextWait.remainingStates = nextWait.states
                nextWait.parser.settags()
                nextWait.advance()
                print("here")
            else:
                self.parser.registerCallback(
                    nextWait[0].name, nextWait[1].name, 
                    self.callback[nextWait[2].name])
        else:
            if self.type == 'loop':
                self.remainingStates = self.states
            elif self.parent:
                self.parent.cont()
            else:
                self.parser.registerCallback(None)

    def cont(self):
        self.advance()
        self.parser.registerLevelUp(
            self.endactions[0].name, self.endactions[1].name, self.levelUp)

    def read(self, file):
        self.remainingStates = self.states
        self.parser.settags()
        print (self.endactions)
        if len(self.endactions) > 0:
            self.parser.registerLevelUp(
                self.endactions[0].name, self.endactions[1].name, self.levelUp)
        self.advance()
        f = open(file, 'r')
        parser.feed(f.read())
        
        


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
        self.count = 4 #for testing
        self.startTags = {}
        self.endTags = {}
        self.levelUpStart = {}
        self.levelUpEnd = {}
        self.dataTarget = None

    def setParseDef(self, definition):
        HTMLParserTableBased.definition = definition
        self.setNextParse()

    def registerLevelUp(self, levelUpTag, levelUpType, levelUpAction):
        if levelUpTag:
            if levelUpType == 'end':
                self.levelUpEnd[levelUpTag] = levelUpAction
            else:
                self.levelUpStart[levelUpTag] = levelUpAction


    def registerCallback(self, tag, type= None, action= None):
        self.startTags = {}
        self.endTags = {}
        if not(tag):
            return
        print(' registercallback ', tag, type)
        if type == 'start':
            self.startTags[tag] = action
        elif type == 'end':
            self.endTags[tag]  = action
        else:
            pass

    def setNextParse(self):
        print(HTMLParserTableBased.definition[0], "nesrtdef")

        first = HTMLParserTableBased.definition[0]
        HTMLParserTableBased.definition = HTMLParserTableBased.definition[1:]

        HTMLParserTableBased.gotoTable = 0
        HTMLParserTableBased.skipRows = 0
        HTMLParserTableBased.printRows = 0
        print("setting", first[0], first[1])
        if first[0] == 'gotoTable':
            HTMLParserTableBased.gotoTable = first[1]
        elif first[0] == 'skipRows':
            HTMLParserTableBased.skipRows = first[1]
        else:
            HTMLParserTableBased.printRows = first[1]


    def handle_starttag(self, tag, attrs):
        #print("saw tag ", tag)
        if tag in self.startTags.keys():
            self.startTags[tag]()
        if tag in self.levelUpStart.keys():
            self.levelUpStart[tag]()

    def handle_endtag(self, tag):
        if tag == 'table':
            self.count = self.count - 1
            if self.count == 0:
                self.startTags = {}
                self.endTags = {}
        if tag in self.endTags.keys():
            self.endTags[tag]()
        print(self.levelUpEnd.keys(), tag)
        if tag in self.levelUpEnd.keys():
            self.levelUpEnd[tag]()
            
    def handle_data(self, data):
        if self.dataTarget:
            self.dataTarget(data)
        #if self.lastTag == 'td' or self.lastTag == 'th':
        #    #self.rowdata.append(data.strip()) 
        #    if HTMLParserTableBased.printRows > 0:
        #        print(data)






if __name__ == "__main__":

    print(tableDescribing)

    parser = HTMLParserTableBased()
    top = TableParser(parser, None,'top')
    #top.setInput(tableTest)
    top.setInput(tableDescribing)
    #top.setInput(tablesOnly)
    top.setStates(0)

    print()
    print(top)

    top.read(r".\data\allresults.html")
    print('registered tables:',len(top.tables))
