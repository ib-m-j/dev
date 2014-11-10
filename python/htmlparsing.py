import html.parser
import sys
import tournament
import codecs

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



class HtmlTable:
    
    def __init__(self, name, nr, level):
        self.name = name
        self.nr = nr
        self.level = level
        self.header = 'none'
        self.rows = 0

    def addRow(self):
        self.rows = self.rows + 1

    def addHeader(self, header):
        self.header = header

    def __str__(self):
        return '{} {:7} - {:10} {:2} rows. TableNr {:3}'.format(self.level, 
                                                       self.header, self.name,
                                                       self.rows, self.nr)

def getAttribute(x, attrs):
    res = "none"
    for (a,b) in attrs:
        if a == x:
            res = b
    return res


class HTMLParserTableAnalysis(html.parser.HTMLParser):
    level = 0
    lastTag = ''
    allTables = []


    def handle_starttag(self, tag, attrs):
        HTMLParserTableAnalysis.lastTag = tag
        if tag == 'table':
            attributeValue = getAttribute('class', attrs)
            if attributeValue:
                tableClass = attributeValue
            else:
                tableClass = 'undefined'
        
            HTMLParserTableAnalysis.level = HTMLParserTableAnalysis.level + 1

            newTable = HtmlTable(tableClass, 
                                 len(HTMLParserTableAnalysis.allTables),
                                 HTMLParserTableAnalysis.level)
            HTMLParserTableAnalysis.allTables.append(newTable)

        if tag == 'tr':
            HTMLParserTableAnalysis.allTables[-1].addRow()

        if tag == 'th':
            HTMLParserTableAnalysis.allTables[-1].addHeader('header')
            


    def handle_endtag(self, tag):
        if tag == 'table':
            HTMLParserTableAnalysis.level = HTMLParserTableAnalysis.level -1
            




class HTMLParserTableBased(html.parser.HTMLParser):
    level = 0
    lastTag = ''
    allTables = []
    gotoTable = 0
    skipRows = 0
    printRows = 0
    rowdata = []
    definition = []

    def setParseDef(self, definition):
        HTMLParserTableBased.definition = definition
        self.setNextParse()

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
        self.lastTag = tag
        if tag == 'table':
            if HTMLParserTableBased.gotoTable > 0:
                HTMLParserTableBased.gotoTable = \
                HTMLParserTableBased.gotoTable - 1
                if HTMLParserTableBased.gotoTable == 0:
                    self.setNextParse()

        if tag == 'tr':
            if self.printRows > 0:
                self.rowdata = []


    def handle_endtag(self, tag):
        if tag == 'table':
            if (HTMLParserTableBased.printRows > 0 or 
                HTMLParserTableBased.skipRows > 0):
                self.setNextParse()
            
        if tag == 'tr':
            if HTMLParserTableBased.printRows > 0:
                print(self.rowdata)
                self.rowdata = []
                HTMLParserTableBased.printRows = \
                    HTMLParserTableBased.printRows - 1
                if self.printRows == 0:
                    self.setNextParse()
            if HTMLParserTableBased.skipRows > 0:
                HTMLParserTableBased.skipRows = HTMLParserTableBased.skipRows -1
                if HTMLParserTableBased.skipRows == 0:
                    self.setNextParse()
            
    def handle_data(self, data):
        if self.lastTag == 'td' or self.lastTag == 'th':
            #self.rowdata.append(data.strip()) 
            if HTMLParserTableBased.printRows > 0:
                print(data)


def registerTables():
        
    parser = HTMLParserTableAnalysis()
    input = open(r"..\data\allresults.html")
    log = open(r'..\logs\allresults.txt', 'w')
    parser.feed(input.read())
    for x in HTMLParserTableAnalysis.allTables:
        print(x)
        log.write(x.__str__()+'\n')
    log.close()


def parseIslev():
    #skipFirstTables = SkipTables('starting', 3, 'skipHeaderRows')
    #skipHeaderRows = SkipRows('skipHeaderRows', 2, 'readTeamNr')
    #readTeamNr = PrintData('readTeamNr', 'readTeamName')
    #readTeamName = PrintData('readTeamName', 'readContract')
    #readContract = PrintData('readContract', 'goToEnd')
    #goToEnd = SkipTables('goToEnd',200, 'goToEnd')
    #skipFirstTables.setCurrentState('starting')

    parser = HTMLParserTableBased()
    parseDef = [('gotoTable', 5), ('skipRows', 2), ('printRows', 6), 
                ('gotoTable', 200)]
    parser.setParseDef(parseDef)
    input = open(r"..\data\allresults.html")
    #print(input.read().encode('latin-1','ignore'))
    parser.feed(input.read().encode('latin-1').decode('utf-8','ignore'))


if __name__ == '__main__':
    #starting = SkipTables('starting', 5, 'getOneCell')
    #skipSomeTables = SkipTables('starting', 6, 'getOneCell')
    #getOneCell = PrintData('getOneCell', 'skipSomeRows')
    #getOneMoreCell = PrintData('getOneMoreCell', 'ending')
    #skipSomeRows = SkipRemainingRows('skipSomeRows', 'getOneMoreCell') 
    #ending = SkipTables('ending', 200, '')
    #starting.setCurrentState('starting')
    #


    #parser = MyHTMLParser()
    #input = open(r"..\data\allresults.html")
    #parser.feed(input.read())
    #
    #for x in HtmlTable.openTables:
    #    print('\t{}\n'.format(x))

                           
    parseIslev()
    #registerTables()
