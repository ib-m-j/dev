import html.parser
import sys
from pypeg2 import *
import re




class TagType(Keyword):
    grammar = Enum( K('end'), K('start'))

class Action(Keyword):
    grammar = Enum( K('newTable'), K('newRow'), K('newData'), K('flushData'), K('advance'))

class BasicObject(str):
    grammar = '(', attr('tagName',word),',',attr('tagtype', TagType),',',\
              (attr('action', Action),attr('parameter',optional('(',word,')'))),')'

class EndAction(str):
    grammar = '(', name(), ',', attr('tagtype', TagType),')'

class Loop(Keyword):
    grammar = Enum( K('loop'))

class ParserDef(str):
    grammar = [(attr('loop', Loop), '('), (attr('endaction', EndAction)), \
               (attr('basic',BasicObject)),')'] , attr('rest',restline)


standardData = [(tr, start, newRow), (tr, end, flushRow), 
                (td, start, newData), (td, end, flushData),
                (table, end , flushTable)]
 

islevTotal = 'islevGetHeader loop(islevGetPlays, islevGetCards)'

islevGetHeader = standardData
islevGetPlays = '(tr, start, (

tableParseDef1 = 'loop((endtag, end)(tag, start, finish)loop((tag1, end, skip(a))))(tag2, start, finish)(tag3, end, inc)'

tableDescribing = 'loop((table, end)(table, start, newTable)\
loop((tr, end)(tr, start, newRow)loop((tr, end)(td, start, newData)(td,end,flushData))))'

tableTest = '(table,start,newTable)(tr,end,newRow)(td,start,newData)(td,end,flushData)'

testDetails = '(table, start, newTable) (tr, start, newRow) (td, start, newData) (td, end, flushData)(table, start, newTable)loop((table, end)(tr, start, newRow)loop((tr, end) (td, start, newData)(td,end,flushData)))(table, start, newTable)(table, start, newTable)(table, start, newTable)loop((table, end)(tr, start, newRow)loop((tr, end) (td, start, newData)(td,end,flushData)))'

tablesOnly = 'loop((table, end)(table, start, newTable))'

def parseValue(res, attr):
    return attr in res.__dict__


class TableWithData:
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
    count = 0

    def __init__(self, parser, parent, type):
        self.id = TableParser.count
        TableParser.count = TableParser.count + 1
        self.states = []
        self.endActions = []
        self.parent = parent
        self.input = ''
        self.level = 0
        self.type = type
        self.parser = parser
        self.callback = {'newTable': self.newTable,
                         'newRow': self.newRow,
                         'newData': self.newData,
                         'flushData': self.flushData,
                         'advance': self.advance}
                         

    def setInput(self, input):
        self.input = input

    def setEndActions(self, actions):
        for a in actions:
            self.endActions.append(a)
        
    

    def setStates(self, level):
        self.level = level
        while len(self.input) > 0:
            print (self.input)
            res = parse(self.input, ParserDef)
            if parseValue(res, 'loop'):
                child = TableParser(parser, self, res.loop)
                child.setEndActions(self.endActions)
                #print('setting end:', child.endActions)
                child.setInput(res.rest)
                child.setStates(level + 1)
                self.states.append(child)
                
            elif parseValue(res, 'basic'):
                #print('!!!!!!!',res.__dict__['basic'].__dict__['name'])
                #print('!!!!!',res.basic.name, res.basic.tagtype)
                self.states.append((res.basic.tagName,res.basic.tagtype.name,
                                    res.basic.action.name, res.basic.parameter))
                self.input = res.rest
            elif parseValue(res, 'endaction'):
                self.endActions.append((res.endaction.name.name,
                                        res.endaction.tagtype.name, 
                                        self.levelUp))
                #print('adding end:', self.endActions)
                self.input = res.rest
            else:
                if level> 0:
                    self.parent.setInput(res.rest)
                break


    def __str__(self):
        res = 'id: {}, level: {} type {} length {}\n'.format(
            self.id, self.level, self.type, len(self.states))
        res = res + '{}endactions: '.format(self.level*'  ')
        for s in self.endActions:
            res = res + '{}, {} -  '.format(s[0],s[1])
        res = res + '\n'
        for s in self.states:
            if isinstance(s, TableParser):
                res = res + '{}child {}\n'.format(self.level*'  ',s.__str__())
            else:
                res = res + '{}{}\n'.format(self.level*'  ',s)
        
        return res

    def strShort(self):
        return '{} type {}\n'.format(self.level, self.type)

    def newTable(self):
        print('got callback table')
        newTable = TableWithData()
        TableParser.tables.append(newTable)
        TableParser.currentTable = newTable
        self.advance()
        
    def newRow(self):
        print('got callback row')
        newRow = Row()
        TableParser.currentTable.addRow(newRow)
        TableParser.currentRow = newRow
        self.advance()

    def newData(self):
        print('got callback data start')
        newData = Data()
        TableParser.currentRow.addData(newData)
        TableParser.currentData  = newData
        self.parser.dataTarget = self.addData
        self.advance()

    def addData(self, data):
        print(data)
        if TableParser.currentData:
            TableParser.currentData = TableParser.currentData.setData(data)
            #print('set data to:',data)
        
    def flushData(self):
        print('flush data')
        self.parser.dataTarget = None
        self.advance()

    def advance(self):
        self.advance()

    def levelUp(self):
        con = self.parent #hmm problems handling going up
        print('got callback level up from', self.id)
        con.parser.registerLevelUps(con.endActions)
        con.advance()

        

    def advance(self):
        if len(self.remainingStates) > 0:
            nextWait = self.remainingStates[0]
            self.remainingStates = self.remainingStates[1:]
            if isinstance(nextWait, TableParser):
                #print("Going down to",nextWait.id, nextWait.endActions)
                nextWait.remainingStates = nextWait.states
                nextWait.parser.settags()
                if len(nextWait.endActions) > 0:
                    #print('set endActions: ',nextWait.endActions[0])
                    nextWait.parser.registerLevelUps(nextWait.endActions)
                        #nextWait.endActions[0][0], nextWait.endActions[0][1], 
                        #nextWait.levelUp)
                nextWait.advance()
            else:
                print('set callbacks:', nextWait)
                if nextWait[2] != 'None':
                    self.parser.registerCallback(
                        nextWait[0], nextWait[1], 
                        self.callback[nextWait[2]])
        else:
            if self.type == 'loop':
                print('doing loop')
                self.remainingStates = self.states
                print(self.states[0])
                self.advance()
            elif self.parent:
                self.levelUp()
            else:
                self.parser.registerCallback(None)


    def read(self, file):
        self.remainingStates = self.states
        self.parser.settags()
        #print ('endactions!!!!', self.endActions)
        if len(self.endActions) > 0:
            self.parser.registerLevelUps(self.endActions)
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
        self.count = 6 #for testing
        self.startTags = {}
        self.endTags = {}
        self.levelUpStart = {}
        self.levelUpEnd = {}
        self.dataTarget = None

    #def setParseDef(self, definition):
    #    HTMLParserTableBased.definition = definition
    #    self.setNextParse()
    
    def registerLevelUps(self, levelUps):
        print(levelUps)
        self.levelUpStart = {}
        self.levelUpEnd = {}
        for lU in levelUps:
            self.registerLevelUp(lU[0], lU[1], lU[2])

    def registerLevelUp(self, levelUpTag, levelUpType, levelUpAction):
        #print('register levelUp:', levelUpTag, levelUpType)
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
        #print(' registercallback ', tag, type)
        if type == 'start':
            self.startTags[tag] = action
        elif type == 'end':
            self.endTags[tag]  = action
        else:
            pass

    #def setNextParse(self):
    #    print(HTMLParserTableBased.definition[0], "nesrtdef")
    #
    #    first = HTMLParserTableBased.definition[0]
    #    HTMLParserTableBased.definition = HTMLParserTableBased.definition[1:]
    #
    #    HTMLParserTableBased.gotoTable = 0
    #    HTMLParserTableBased.skipRows = 0
    #    HTMLParserTableBased.printRows = 0
    #    print("setting", first[0], first[1])
    #    if first[0] == 'gotoTable':
    #        HTMLParserTableBased.gotoTable = first[1]
    #    elif first[0] == 'skipRows':
    #        HTMLParserTableBased.skipRows = first[1]
    #    else:
    #        HTMLParserTableBased.printRows = first[1]


    def handle_starttag(self, tag, attrs):
        #print("saw tag ", tag)
        if tag in self.startTags.keys():
            self.startTags[tag]()
        if tag in self.levelUpStart.keys():
            self.levelUpStart[tag]()

    def handle_endtag(self, tag):
        if tag == 'table':
            pass
            #print('got end tag', tag, self.count)
        ##if tag == 'table':
        #    self.count = self.count - 1
        #    if self.count == 0:
        #        self.startTags = {}
        #        self.endTags = {}
        #        self.dataTarget = None
        #        print("!!!!!!!!!!!!!stopping")
        #        #sys.exit(0)
        if tag in self.endTags.keys()and self. count > 0:
            self.endTags[tag]()
        if tag in self.levelUpEnd.keys() and self.count > 0:
            print('tag: ', tag, 'end')
            self.levelUpEnd[tag]()
            
    def handle_data(self, data):
        if self.dataTarget:
            self.dataTarget(data)
        #if self.lastTag == 'td' or self.lastTag == 'th':
        #    #self.rowdata.append(data.strip()) 
        #    if HTMLParserTableBased.printRows > 0:
        #        print(data)


def doTables():
    print(tableDescribing)

    parser = HTMLParserTableBased()
    top = TableParser(parser, None,'top')
    #top.setInput(tableTest)
    top.setInput(tableDescribing)
    #top.setInput(tablesOnly)
    top.setStates(0)

    print()
    print(top)

    top.read(r"..\data\allresults.html")
    print('registered tables:',len(top.tables))
    for t in top.tables:
        print('start table', t)
        for r in t.rows:
            res = 'New Row>>'
            for d in r.data: 
                res = res + d.value + '@'
            print(res)



if __name__ == "__main__":

    print(testDetails)

    parser = HTMLParserTableBased()
    top = TableParser(parser, None,'top')
    top.setInput(testDetails)
    top.setStates(0)

    print()
    print(top)

    top.read(r"..\data\allresults.html")
    print('registered tables:',len(top.tables))
    for t in top.tables:
        print('start table', t)
        for r in t.rows:
            res = 'New Row>>'
            for d in r.data: 
                res = res + d.value + '@'
            print(res)
