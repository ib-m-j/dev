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
            


class HTMLParserTablebased(html.parser.HTMLParser):
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
    skipFirstTables = SkipTables('starting', 3, 'skipHeaderRows')
    skipHeaderRows = SkipRows('skipHeaderRows', 2, 'readTeamNr')
    readTeamNr = PrintData('readTeamNr', 'readTeamName')
    readTeamName = PrintData('readTeamName', 'readContract')
    readContract = PrintData('readContract', 'goToEnd')
    goToEnd = SkipTables('goToEnd',200, 'goToEnd')
    skipFirstTables.setCurrentState('starting')

    parser = HTMLParserTableAnalysis()
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

    registerTables()

    #parser = MyHTMLParser()
    #input = open(r"..\data\allresults.html")
    #parser.feed(input.read())
    #
    #for x in HtmlTable.openTables:
    #    print('\t{}\n'.format(x))

                           
    #parseIslev()
