import html.parser
import sys
import tournament

islevParser = []
    
#events:
#TableStart, TableEnd, RowStart, RowEnd, CellStart, CellEnd, Data
#actions:
#SkipTable, SkipRow, SkipCell, RegisterNSNr, RegisterNSName, RegisterEWNr, RegisterEWName, RegisterPlayer, RegisterContract, RegisterResult, RegistePlayout, RegisterScore,RegisterNSpoints, RegisterEWPoints  
#
#State(
#

class State:
    all = {}
    currentState = None

    def __init__(self, id, nextStateId):
        self.id = id
        self.nextStateId = nextStateId
        State.all[id] = self

    def setCurrentState(self, nextStateId):
        State.currentState = State.all[nextStateId]
        print(nextStateId)

    def doEvent(self, tag, startEnd, attrs = None):
        pass

    def registerData(self, data):
        pass

class SkipTables(State):
    def __init__(self, id, skipNo, nextStateId):
        State.__init__(self, id, nextStateId)
        self.skipNo = skipNo
        
    def doEvent(self, tag, startEnd, attrs = None):
        if tag == 'table' and startEnd == 'S':
            self.skipNo = self.skipNo - 1
        if self.skipNo <= 0:
            self.setCurrentState(self.nextStateId)

class SkipRows(State):
    def __init__(self, id, skipNo, nextStateId):
        State.__init__(self, id, nextStateId)
        self.skipNo = skipNo
        
    def doEvent(self, tag, startEnd, attrs = None):
        if tag == 'tr' and startEnd == 'S':
            self.skipNo = self.skipNo - 1
        if self.skipNo <= 0:
            self.setCurrentState(self.nextStateId)

class SkipRemainingRows(State):
    def __init__(self, id, nextStateId):
        State.__init__(self, id, nextStateId)
        
    def doEvent(self, tag, startEnd, attrs = None):
        if tag == 'tr' and startEnd == 'E':
            self.setCurrentState(self.nextStateId)

class PrintData(State):
    def __init__(self, id, nextStateId):
        State.__init__(self, id, nextStateId)
        self.data = ''
        
    def doEvent(self, tag, startEnd, attrs = None):
        if tag == 'td' and startEnd == 'E':
            print("in data",self.data)
            self.setCurrentState(self.nextStateId)

    def registerData(self, data):
        self.data = self.data + data.strip()

    
            



    


class HtmlTable:
    openTables = []
    level = 0
    allTables = {}
    
    def __init__(self, name):
        self.name = name
        self.nr = len(HtmlTable.openTables)
        self.level = HtmlTable.level
        self.header = 'none'
        self.rows = 0
        HtmlTable.level = HtmlTable.level + 1
        HtmlTable.openTables.append(self)
        #print(self.level, HtmlTable.allTables)
        if self.level in HtmlTable.allTables:
            HtmlTable.allTables[self.level].append(self)
        else:
            HtmlTable.allTables[self.level] = [self]

    def addRow(self):
        self.rows = self.rows + 1

    def addHeader(self, header):
        self.header = header

    def __str__(self):
        return '{} {} - {} {} rows. TableNr {}'.format(self.level, 
                                                       self.header, self.name,
                                                       self.rows, self.nr)


class MyHTMLParser(html.parser.HTMLParser):
    lastTag = ''
    openTable = []


    def handle_starttag(self, tag, attrs):
        State.currentState.doEvent(tag, 'S', attrs)



        #MyHTMLParser.lastTag = tag
        #if tag == 'table':
        #    tableClass = 'undefined'
        #    for (x,y) in attrs:
        #        if x == 'class':
        #            tableClass = y
        #            break
        #
        #    newTable = HtmlTable(tableClass)
        #    MyHTMLParser.openTable.append( newTable)

        #if tag == 'tr':
        #    MyHTMLParser.openTable[-1].addRow()

        #if tag == 'th':
        #    HtmlTable.openTables[-1].addHeader()
            


    def handle_endtag(self, tag):
        State.currentState.doEvent(tag, 'E', None)
        #if tag == 'table':
        #    HtmlTable.level = HtmlTable.level - 1
        #    MyHTMLParser.openTable.pop()
        #    
        #    #if len(HtmlTable.openTables) > 4:
        #    #    print (HtmlTable.allTables)
        #    #    sys.exit(1)
        #pass
        #print("Encountered an end tag :", tag)

    def handle_data(self, data):
        State.currentState.registerData(data)
        #if MyHTMLParser.lastTag == 'th':
        #    if len(data.strip()) > 0:
        #        HtmlTable.openTables[-1].addHeader(data)
        #
        #
        #    #print("saw data:{}:".format(data))
        #pass
        #print("Encountered some data  :", data)


def registerTables():
    class OneMoreTable(State):
        def doEvent(self, tag, startEnd, attrs):
            if tag == 'table' and startEnd == 'S':
                tableClass = 'undefined'
                print( attrs)
                for (x,y) in attrs:
                    if x == 'class':
                        tableClass = y
                        break
        
                newTable = HtmlTable(tableClass)

        
    dumpTables = OneMoreTable('tables', 'tables')
    dumpTables.setCurrentState('tables')

    parser = MyHTMLParser()
    input = open(r"..\data\allresults.html")
    parser.feed(input.read())

    for x in HtmlTable.openTables:
        print(x)


def parseIslev():
    skipFirstTables = SkipTables('starting', 3, 'skipHeaderRows')
    skipHeaderRows = SkipRows('skipHeaderRows', 2, 'readTeamNr')
    readTeamNr = PrintData('readTeamNr', 'readTeamName')
    readTeamName = PrintData('readTeamName', 'readContract')
    readContract = PrintData('readContract', 'goToEnd')
    goToEnd = SkipTables('goToEnd',200, 'goToEnd')
    skipFirstTables.setCurrentState('starting')

    parser = MyHTMLParser()
    input = open(r"..\data\allresults.html")
    parser.feed(input.read())


if __name__ == '__main__':
    #starting = SkipTables('starting', 5, 'getOneCell')
    #skipSomeTables = SkipTables('starting', 6, 'getOneCell')
    #getOneCell = PrintData('getOneCell', 'skipSomeRows')
    #getOneMoreCell = PrintData('getOneMoreCell', 'ending')
    #skipSomeRows = SkipRemainingRows('skipSomeRows', 'getOneMoreCell') 
    #ending = SkipTables('ending', 200, '')
    #starting.setCurrentState('starting')
    #

    #registerTables()

    #parser = MyHTMLParser()
    #input = open(r"..\data\allresults.html")
    #parser.feed(input.read())
    #
    #for x in HtmlTable.openTables:
    #    print('\t{}\n'.format(x))

                           
    parseIslev()