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
        
    def addAttribute(self, attr, value):
        self.attributes.append((attr, value))

    def addContent(self, content):
        self.content.append(content)

    def renderContent(self):
        res = ''
        for c in self.content:
            if isinstance(c, str):
                contentStr = html.escape(c)
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
        self.cellFormatter = cellFormatter

    def setHeaderRow(self, headerRow, formatter = str):
        self.headerRow = headerRow
        self.rowFormatter = formatter

    def setHeaderColumn(self, headerColumn, formatter = str):
        self.headerColumn = headerColumn
        self.columnFormatter = formatter

    def addHeaderRowValue(self, headerRowValue):
        self.headerRow.append(headerRowValue)

    def addHeaderColumnValue(self, headerColumnValue):
        self.headerColumn.append(headerColumnValue)

    def setFocus(self, strain, result):
        self.focusResult = self.headerRow.index(result)
        self.focusStrain = self.headerColumn.index(strain)

    def setTeamFocus(self, strain, result):
        self.teamFocusResult = self.headerRow.index(result)
        self.teamFocusStrain = self.headerColumn.index(strain)


    def getCoord(self, rValue, cValue):
        #print('getcoord', cValue, self.headerRow, rValue, self.headerColumn)
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
            raise Exception(
                'could not set content {},{}'.format(rIndex, cIndex))

    def getContent(self, rIndex, cIndex):
        if cIndex < len(self.headerRow) and rIndex < len(self.headerColumn):
            return self.cells[rIndex][cIndex]
        else:
            raise Exception(
                'could not get content {},{}'.format(rIndex, cIndex))

    def hasCell(self, r,c):
        return (r in self.cells.keys() and c in self.cells[r].keys())

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
        #merge by adding column and rows to create large table
        
    def expandRows(self, other):
        #result will contain sum of rows columns will be joined
        res = ArrayContent()
        res.setHeaderRow(self.headerRow + other.headerRow)
        res.setHeaderColumn(self.headerColumn)
        for (r,c,v) in self:
                res.setContent(r,c,v)
        
        columnMap = {}
        for (n,x) in enumerate(other.headerRow):
            if x in self.headerRow:
                columnMap[n] = self.headerRow.index(x)
            else:
                res.headerRow.append(x)
                columnMap[n] = len(res.headerRow) - 1

        rowMap = {}
        for (n,x) in enumerate(other.headerColumn):
            res.headerColumn.append(x)
            rowMap[n] = len(res.headerColumn) - 1

        for (r,c,v) in other:
            res.setContent(rowMap[r], columnMap[c], v)

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
            self, includeHeaderColumn = True, includeHeaderRow = True):
        res = HtmlTable()
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
                if r == self.focusStrain and c == self.focusResult:
                    cell.addAttribute('bgcolor','#AAFFAA')
                if r == self.teamFocusStrain and c == self.teamFocusResult:
                    cell.addAttribute('bgcolor','#FFAAAA')
                row.append(cell)

            res.addRow(HtmlRow().addCells(row))
            
        return res
            
class HtmlWrapper(HtmlTag):
    def __init__(self):
        HtmlTag.__init__(self,'''<!doctype html public "-//W3C//DTD HTML 4.0//EN">
<html>\n''', '</html>')

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

#    def writeAsFile(self, name):
#        f = open(name, 'w')
#        f.write(self.render())
#        f.close()
#

class HtmlList(HtmlTag):
    def __init__(self, basedAt, masterName, header):
        self.basedAt = basedAt
        self.masterName = masterName
        self.list = []
        self.displayList = []
        self.header = header
        self.linkTemplate = '{}{}.html'

    def addElement(self, relListName, displayName):
        self.list.append(relListName)
        self.displayList.append(displayName)

    def getMasterName(self):
        return os.path.join(self.masterName + '.html')

    def getLinkFileName(self, n):
        return os.path.join(self.linkTemplate.format(
                self.masterName, self.list[n].replace(' ','')))

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
            nextLink = HtmlLink('n�ste', self.getMasterName())
        else:
            nextLink = HtmlLink('n�ste', self.getNextName(n))
        return nextLink


    def render(self):
        br = HtmlBreak() #same break for all breaks
        masterFileName = os.path.join(self.basedAt, self.masterName )
        header = HtmlTag('<h2>',None, self.header)
        body = HtmlTag('<body>')
        body.addAttribute("style","font-size:18pt")
        wrap= HtmlWrapper()
        wrap.addContent(body)
        body.addContent(header)

        last = None
        for n in range(len(self.list)):
            link = HtmlLink(self.displayList[n], self.getLinkFileName(n))
            body.addContent(link)
            body.addContent(br)
        return wrap.render()    
            

def renderTable():
    table = HtmlTable()
    table.addRowWithCell('aaaø')
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


if __name__ == '__main__':
    #renderTable()
    #renderLinks()
    list = HtmlList(os.path.normpath('..\\data\\'), 'testlinks', 'title')
    for n in range(5):
        list.addElement('Game {:d}'.format(n))
    
    list.saveToFile(list.getMasterName())
