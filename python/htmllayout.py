# -*- coding: iso-8859-1 -*-
import html
import os
import itertools
import bridgecore

class HtmlTag:
    def __init__(self, start, end = None, content = None):
        self.start = start
        if end == None:
            self.end = self.start[0]+'/'+self.start[1:]
        else:
            self.end = end
        self.content = []
        if content:
            self.content.append(content)
        self.attributes = []
        self.escape = True

    def addAttribute(self, attr, value):
        self.attributes.append((attr, value))

    def addContent(self, content):
        self.content.append(content)

    def dontEscape(self):
        self.escape = False

    def renderContent(self):
        #print('rendercontent', self)
        res = ''
        for c in self.content:
            if isinstance(c, str):
                if self.escape:
                    contentStr = html.escape(c)
                else:
                    contentStr = c
            elif c:
                contentStr = c.render()
            else:
                contentStr = ''
            res = res + contentStr
        return res

    def renderAttrs(self):
        endAt = self.start.find('>')
        res = self.start[:endAt] + ' '
        for (attr,value) in self.attributes:
            res = res + ' {} = "{}" '.format(attr, value)
        return res + self.start[endAt:]
            
    def render(self):
        #print(self, self.start, self.end)
        contentStr = self.renderContent()
        return self.renderAttrs() + contentStr + self.end 

    def saveToFile(self, filename):
        f = open(filename, 'w')
        f.write(self.render())
        f.close()

class DivTag(HtmlTag):
    def __init__(self, name):
        HtmlTag.__init__(self, '<div>')
        self.addAttribute('id', name)


class JsScriptTag(HtmlTag):
    def __init__(self, fileName):
        HtmlTag.__init__(self, '<script>')
        self.addAttribute('type', "text/javascript")
        self.fileName = fileName

    def getPreContent(self):
        res = ''
        if self.fileName:
            f = open(self.fileName, 'r')
            res = f.read()
            f.close()
        return res


class HtmlCell(HtmlTag):
    def __init__(self, content):
        HtmlTag.__init__(self, '<td>')
        self.content.append(content)
        
class HtmlRow(HtmlTag):
    def __init__(self):
        self.cells = []
        HtmlTag.__init__(self, '<tr>\n','\n</tr>\n')
        
    def addCell(self, cell):
        self.cells.append(cell)

    def addCells(self, cells):
        self.cells = self.cells + cells
        return self

    def renderContent(self):
        #res = '<div>'
        res = ''
        for c in self.cells:
            res = res + c.render()
        return res

class HtmlTable(HtmlTag):
    def __init__(self):
        self.rows = []
        HtmlTag.__init__(self, '<table>\n')

    def addRow(self, row):
        self.rows.append(row)
        return self.rows[:-1]

    def addRows(self, rows):
        self.rows.extend(rows)

    def renderContent(self):
        #res = '<div>'
        res = ''
        for r in self.rows:
            res = res + r.render() 
        return res

    def addRowWithCell(self, content):
        c = HtmlCell(content)
        r = HtmlRow()
        r.addCell(c)
        self.addRow(r)

class ArrayContent:
    def __init__(self, cellFormatter):
        self.headerRow = []
        self.headerColumn = []
        self.cells = {} #cells contains content indexed by coordinates
        self.attributes = {}
        self.cellFormatter = cellFormatter
        self.teamFocusStrain = None
        self.teamFocusResult = None
        self.focusStrain = None
        self.focusResult = None


    def setHeaderRow(self, headerRow, formatter = str):
        self.headerRow = headerRow
        self.rowFormatter = formatter

    def setHeaderColumn(self, headerColumn, formatter = str):
        self.headerColumn = headerColumn
        self.columnFormatter = formatter

    def addHeaderRowValue(self, headerRowValue):
        self.headerRow.append(headerRowValue)

    def addFirstHeaderColumnValue(self, headerValue):
        self.headerColumn = [headerValue] + self.headerColumn

    def addHeaderColumnValue(self, headerColumnValue):
        self.headerColumn.append(headerColumnValue)

    #def setFocus(self, strain, result):
    #    self.focusResult = self.headerRow.index(result)
    #    self.focusStrain = self.headerColumn.index(strain)
    #
    #def setTeamFocus(self, strain, result):
    #    self.teamFocusResult = result #self.headerRow.index(result)
    #    self.teamFocusStrain = strain #self.headerColumn.index(strain)
    #
    #def getTeamFocusIndexes(self):
    #    if self.teamFocusResult:
    #        return (self.headerRow.index(self.teamFocusResult),
    #                self.headerColumn.index(self.teamFocusStrain))
    #    return None


    def getCoord(self, rValue, cValue):
        if cValue in self.headerRow and rValue in self.headerColumn:
            return (self.headerColumn.index(rValue),
                    self.headerRow.index(cValue))
        else:
            raise Exception(
                'cannot find coordinate {},{}'.format(rValue, cValue))

    def setContent(self, rIndex, cIndex, content):
        #print(rIndex, cIndex, self.headerColumn, self.headerRow, content)
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            #print(self.cells)
            if not rIndex in self.cells:
                self.cells[rIndex] = {}
            self.cells[rIndex][cIndex] = content
        else:
            print(self.headerRow, self.headerColumn, rIndex, cIndex)
            raise Exception(
                'could not set content {},{}'.format(rIndex, cIndex))

    def getContent(self, rIndex, cIndex):
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            return self.cells[rIndex][cIndex]
        else:
            raise Exception(
                'could not get content {},{}'.format(rIndex, cIndex))

    def setAttributes(self, rIndex, cIndex, attributes):
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            if not rIndex in self.attributes:
                self.attributes[rIndex] = {}
            self.attributes[rIndex][cIndex] = attributes
        else:
            print(self.headerRow, self.headerColumn, rIndex, cIndex)
            raise Exception(
                'could not set attributes {},{}'.format(rIndex, cIndex))

    def addAttribute(self, rIndex, cIndex, attribute):
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            if not rIndex in self.cells:
                self.attriutes[rIndex] = {}
            if not cIndex in self.sells[rIndex]:
                self.attributes[rIndex][cIndex] =[]
            self.attributes[rIndex][cIndex].append(attribute)
        else:
            print(self.headerRow, self.headerColumn, rIndex, cIndex)
            raise Exception(
                'could not set content {},{}'.format(rIndex, cIndex))

    def getAttributes(self, rIndex, cIndex):
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            if self.hasAttributes(rIndex, cIndex):
                return self.attributes[rIndex][cIndex]
            else: 
                return []
        else:
            return []

    def hasCell(self, r,c):
        return (r in self.cells.keys() and c in self.cells[r].keys())

    def hasAttributes(self, r,c):
        return (r in self.attributes.keys() and c in self.attributes[r].keys())

    def getCell(self, r,c):
        if self.hasCell(r, c):
            return self.cells[r][c] 

    def getAttribue(self, r,c):
        if self.hasAttribute(r, c):
            return self.attributes[r][c] 
        return None

    def __iter__(self):
        self.rIndex = -1
        self.cIndex = len(self.headerRow) -1
        return self

    def __next__(self):
        self.cIndex += 1
        if self.cIndex == len(self.headerRow):
            self.cIndex = 0

            self.rIndex += 1
            if self.rIndex == len(self.headerColumn):
                raise StopIteration
        
        if self.hasCell(self.rIndex,self.cIndex):
            return (self.rIndex,self.cIndex,self.cells[self.rIndex][self.cIndex])
        else:
            return (self.rIndex,self.cIndex, None)
            
    def merge(self, other):
        pass

    def expandRows(self, other):
        #result will contain sum of rows columns assumed identical
        res = ArrayContent('{:d}'.format)
        res.setHeaderRow(self.headerRow)
        res.setHeaderColumn(self.headerColumn)
        for (r,c,v) in self:
                res.setContent(r,c,v)
        
        for r in self.attributes.keys():
            for c in self.attributes[r].keys():
                res.setAttributes(r,c,self.getAttributes(r,c))

        #columnMap = {}
        #for (n,x) in enumerate(other.headerRow):
        #    if x in self.headerRow:
        #        columnMap[n] = self.headerRow.index(x)
        #    else:
        #        res.headerRow.append(x)
        #        columnMap[n] = len(res.headerRow) - 1
        #not needed for identical columns

        rowMap = {}
        for (n,x) in enumerate(other.headerColumn):
            res.headerColumn.append(x)
            rowMap[n] = len(res.headerColumn) - 1

        for (r,c,v) in other:
            res.setContent(rowMap[r], c, v)
            #if colulmns also change use this
            #res.setContent(rowMap[r], columnMap[c], v)

        for r in other.attributes.keys():
            for c in other.attributes[r].keys():
                res.setAttributes(rowMap[r],c,other.getAttributes(r,c))

        return res

    def sortColumns(self, reverseValue = False):
        map = {}
        newHeader = self.headerRow[:]
        newHeader.sort(reverse = reverseValue)
        for c in range(len(self.headerRow)):
            map[c] = newHeader.index(self.headerRow[c])

        #print(self.headerColumn, self.headerRow, newHeader, map)
    
        newCells = {}
        for (r,c,v) in self:
            if v:
                #print('found ', r, c, v)
                if not r in newCells.keys():
                    newCells[r] = {}
                newCells[r][map[c]] = v
                #print('wrote', r, map[c], v)
                
        self.headerRow = newHeader
        self.cells = newCells
        self.focusResult = map[self.focusResult]
        self.teamFocusResult = map[self.teamFocusResult]

    def sortRows(self, reverseValue = False):
        map = {}
        newHeader = self.headerColumn[:]
        newHeader.sort(reverse = reverseValue)
        for c in range(len(self.headerColumn)):
            map[c] = newHeader.index(self.headerColumn[c])

        #print(self.headerColumn, self.headerRow, newHeader, map)
    
        newCells = {}
        for (r,c,v) in self:
            if v:
                #print('found ', r, c, v)
                if not map[r] in newCells.keys():
                    newCells[map[r]] = {}
                newCells[map[r]][c] = v
                
        self.headerColumn = newHeader
        self.cells = newCells
        self.focusStrain = map[self.focusStrain]

    def makeTable(
        self, caption, includeHeaderColumn = True, includeHeaderRow = True):
        res = HtmlTable()
        res.addAttribute('rules','all')
        res.addAttribute('frame','border')
        caption = HtmlTag('<caption>','</caption>', caption)
        res.addRow(caption)
        if includeHeaderRow:
            row = []
            for x in self.headerRow:
                cell = HtmlCell(self.rowFormatter(x))
                cell.addAttribute('align','center')
                row.append(cell)            
            if includeHeaderColumn:
                row = [HtmlCell('')] + row
            
            res.addRow(HtmlRow().addCells(row))

        for (r,v) in enumerate(self.headerColumn):
            #print("starting row", r)
            if includeHeaderRow:
                if isinstance(v, bridgecore.Strain):
                    vStr = v.dkName()
                else:
                    vStr = v

                row = [HtmlCell(self.columnFormatter(vStr))]
            else:
                row = []
            for c in range(len(self.headerRow)):
                #print(r,c, len(self.headerRow))
                if self.hasCell(r,c):
                    toDisplay = self.getContent(r,c)
                    if not toDisplay:
                        toDisplay = ''
                    else:
                        toDisplay = self.cellFormatter(toDisplay)
                else:
                    toDisplay = ''
                cell = HtmlCell(toDisplay)
                cell.addAttribute('width', '50px')
                cell.addAttribute('align', 'center')
                
                for (a,b) in self.getAttributes(r,c):
                    cell.addAttribute(a,b)
                #if r == self.teamFocusStrain and c == self.teamFocusResult:
                #    cell.addAttribute('bgcolor','#FFAAAA')
                row.append(cell)

            #print(self.cells)
            #teamFocus = self.getTeamFocusIndexes()
            #if teamFocus:
            #    c = self.getCell(teamFocus[0], teamFocus[1])
            #    if c:
            #        print("thsi should be a cell:", c)
            #        c.addAttribute('bgcolor','#FFAAAA')

            res.addRow(HtmlRow().addCells(row))
            
        return res


    #not completed    
    def makeGoogleTable(self, divTag, caption):
        div = DivTag(divTag)
        
        rows = [['']+[x for x in self.headerRow]]
        
        for (r,v) in enumerate(self.headerColumn):
            row = [v]
            for c in range(len(self.headerRow)):
                if self.hasCell(r,c):
                    toDisplay = self.getContent(r,c)
                else:
                    toDisplay = ''
                row.append(toDisplay)
                
                #for (a,b) in self.getAttributes(r,c):
                #    cell.addAttribute(a,b)
                #if r == self.teamFocusStrain and c == self.teamFocusResult:
                #    cell.addAttribute('bgcolor','#FFAAAA')
                
        chartDef = GoogleChart(divTag, caption, rows)
        chartDef.setupData()
        return (chartDef, divTag)


            
class HtmlWrapper(HtmlTag):
    def __init__(self):
        HtmlTag.__init__(
            self,'''<!doctype html public "-//W3C//DTD HTML 4.0//EN">
            <html>\n''', '</html>')
        self.setHead()

    def setHead(self, head = None):
        if head:
            self.head = head
        else:
            self.head = HtmlTag('<head>')
        
    def setBody(self, body):
        self.body = body

    def renderContent(self):
        return self.head.render()+self.body.render()

class HtmlLink(HtmlTag):
    def __init__(self, text, link):
        HtmlTag.__init__(self,'<a>')
        self.addContent(text)
        self.addAttribute('href', link)

    def render(self):
        return '\n' + HtmlTag.render(self)
    
class HtmlBreak(HtmlTag):
    def __init__(self):
        HtmlTag.__init__(self, '<br>')
        self.end = ''

class HtmlList(HtmlTag):
    def __init__(self, basedAt, masterName, header):
        self.basedAt = basedAt
        self.masterName = masterName
        self.list = []
        self.displayList = []
        self.header = header
        self.linkTemplate = '{}.html'
        HtmlTag.__init__(self, '', '', '')

    def addElement(self, relListName, displayName):
        self.list.append(relListName)
        self.displayList.append(displayName)

    def getMasterName(self):
        return os.path.join(self.masterName + '.html')

    def getLinkFileName(self, n):
        return os.path.join(self.linkTemplate.format(
            self.list[n].replace(' ','')))

    def getFileNameAtBase(self, fileName):
        return os.path.join(self.basedAt, fileName)

    def getPreviousName(self, n):
        if n == 0:
            return self.getMasterName()
        else:
            return self.getLinkFileName(n-1)

    def getNextName(self, n):
        if n == len(self.list) - 1:
            return self.getMasterName()
        else:
            return self.getLinkFileName(n+1)
                    
    def getPreviousLink(self, n):
        if n == 0:
            previousLink = HtmlLink('forrige', self.getMasterName())
        else:
            previousLink = HtmlLink('forrige', self.getPreviousName(n))
        return previousLink

    def getNextLink(self, n):
        if n == len(self.list) - 1:
            nextLink = HtmlLink('næste', self.getMasterName())
        else:
            nextLink = HtmlLink('næste', self.getNextName(n))
        return nextLink

    def getMasterLink(self):
        masterLink = HtmlLink('op', self.getMasterName())
        return masterLink

    def getAsTag(self):
        br = HtmlBreak() #same break for all breaks
        header = HtmlTag('<h3>','</h3>', self.header)
        
        self.content = [br, header ]
        for n in range(len(self.list)):
            link = HtmlLink(self.displayList[n], self.getLinkFileName(n))
            self.content.append(link)
            self.content.append(br)
        return self

            
def getHtmlStart():
    br = HtmlBreak() #same break for all breaks
    body = HtmlTag('<body>')
    wrap= HtmlWrapper()
    wrap.setBody(body)
    return (wrap, body, br)

def renderTable():
    table = HtmlTable()
    table.addRowWithCell('aaaÃ¸')
    print(table.rows)
    print(table.render())
       
    table = HtmlTable()
    table1 = HtmlTable()
    table2 = HtmlTable()
    for r in range(6): 
        row = HtmlRow()
        for d in range(6):
            c = HtmlCell('{}'.format(d))
            #print(c.render())
            row.addCell(c)
        #print(row.render())
        table.addRow(row)
        table1.addRow(row)
        table2.addRow(row)
    row = HtmlRow()
    c = HtmlCell(table1)
    c1 = HtmlCell(table2)
    row.addCells([c,c1])
    table.addRow(row)

    wrap= HtmlWrapper()
    wrap.addContent(table)

    f = open(os.path.normpath('..\\data\\htmlformat.html'), 'w')
    f.write(wrap.render())
    f.close()
    print(wrap.render())


def renderLinks():
    links = ['1', '2', '3']
    br = HtmlBreak() #same break for all breaks

    masterFileName = os.path.normpath('..\\data\\testlinks.html')
    header = HtmlTag('<th>',None, 'Tableheader')
    body = HtmlTag('<body>')
    wrap= HtmlWrapper()
    wrap.addContent(body)
    body.addContent(header)
    body.addContent(br)
    linkTemplate = '{}.html'
    last = None
    
    for n in range(len(links)):
        wrap1 = HtmlWrapper()
        body1 = HtmlTag('<body>')
        wrap1.addContent(body1)
        linkFileName = linkTemplate.format(links[n])
        if n == 0:
            previousLink = HtmlLink('previous', masterFileName)
        else:
            previousLink = HtmlLink('previous', linkTemplate.format(links[n-1]))
        if n == len(links) - 1:
            nextLink = HtmlLink('nest', masterFileName)
        else:
            nextLink = HtmlLink('next', linkTemplate.format(links[n+1]))
            
        link = HtmlLink(links[n], linkFileName)
        body1.addContent('this is number ' + links[n])
        body1.addContent(br)
        body1.addContent(previousLink)
        body1.addContent(br)
        body1.addContent(nextLink)

        f = open(os.path.normpath('..\\data\\{}'.format(linkFileName)), 'w')
        f.write(wrap1.render())
        f.close()
        
        body.addContent(link)
        body.addContent(br)

    f = open(masterFileName, 'w')
    f.write(wrap.render())
    f.close()


class GoogleChart(HtmlTag):
    def __init__(self, divTag, title, rows, subTitle = ''):
        self.divTag = divTag
        self.title = title
        HtmlTag.__init__(self, '<head>')
        self.apiScript = JsScriptTag(None)
        self.apiScript.addAttribute('src', "https://www.google.com/jsapi")
        #self.tableScript = JsScriptTag(os.path.join(
        #    '..','javascript','tablescript.js'))
        self.tableScript = JsScriptTag(os.path.join(
            '..','javascript','viewscript.js'))
        self.tableScript.dontEscape()
        self.rows = rows
        self.subTitle = subTitle 

    def setupData(self):
        res = self.tableScript.getPreContent()
        res = res.replace('¤rows¤', self.rows)
        res = res.replace('¤divtag¤', self.divTag)
        res = res.replace('¤title¤', self.title)
        res = res.replace('¤subtitle¤', self.subTitle)
        self.tableScript.addContent(res)

    def renderContent(self):
        res = self.apiScript.render()
        res = res + self.tableScript.render()
        return res
      
    def getDivTag(self):
        tag =  DivTag(self.divTag)
        tag.addAttribute('style', 'width: 900px; height: 500px;')
        return tag

if __name__ == '__main__':
    #renderTable()
    #renderLinks()
    #list = HtmlList(os.path.normpath('..\\data\\'), 'testlinks', 'title')
    #for n in range(5):
    #    list.addElement('Game {:d}'.format(n))
    #
    #list.saveToFile(list.getMasterName())
    

    rows = '''
    ['Year', 'Sales', 'Expenses', 'Profit'],
    ['2014', 1000, 400, 200],
    ['2015', 1170, 460, 250],
    ['2016', 660, 1120, 300],
    ['2017', 1030, 540, 350]
'''

    body = HtmlTag('<body>')
    div = DivTag('test-chart')
    div.addAttribute('style', 'width: 900px; height: 500px;')
    body.addContent(div)
    
    chartDef = GoogleChart('test-chart', 'title', rows)
    chartDef.setupData()

    
    wrap= HtmlWrapper()
    wrap.setHead(chartDef)
    wrap.setBody(body)

    print(wrap.render())
    wrap.saveToFile('../data/testChart.html')

