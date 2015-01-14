import html
import os

class HtmlTag:
    def __init__(self, start, end = None, content = None):
        self.start = start
        if end == None:
            self.end = self.start[0]+'/'+self.start[1:]
        else:
            self.end = end
        self.content = content

    def addContent(self, content):
        self.content = content

    def renderContent(self):
        if isinstance(self.content, str):
            contentStr = html.escape(self.content)
        elif self.content:
            contentStr = self.content.render()
        else:
            contentStr = ''
        return contentStr

    def render(self):
        #print(self, self.start, self.end)
        contentStr = self.renderContent()
        return self.start + contentStr + self.end #html.escape(contentStr missing

class HtmlCell(HtmlTag):
    def __init__(self, content):
        HtmlTag.__init__(self, '<td>')
        self.content = content
        
class HtmlRow(HtmlTag):
    def __init__(self):
        self.cells = []
        HtmlTag.__init__(self, '<tr>\n','\n</tr>\n')
        
    def addCell(self, cell):
        self.cells.append(cell)

    def addCells(self, cells):
        self.cells = self.cells + cells

    def renderContent(self):
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

    def addRows(self, rows):
        self.rows.extend(rows)

    def renderContent(self):
        res = ''
        for r in self.rows:
            res = res + r.render()
        return res

    def addRowWithCell(self, content):
        c = HtmlCell(content)
        r = HtmlRow()
        r.addCell(c)
        self.addRow(r)

class HtmlWrapper(HtmlTag):
    def __init__(self):
        HtmlTag.__init__(self,'''<!doctype html public "-//W3C//DTD HTML 4.0//EN">
<html>\n''', '</html>')
    
#    def writeAsFile(self, name):
#        f = open(name, 'w')
#        f.write(self.render())
#        f.close()
#

if __name__ == '__main__':
 

    table = HtmlTable()
    table.addRowWithCell('aaaø')
    print(table.rows)
    print(table.render())
       
#    table = HtmlTable()
#    table1 = HtmlTable()
#    table2 = HtmlTable()
#    for r in range(6): 
#        row = HtmlRow()
#        for d in range(6):
#            c = HtmlCell('{}'.format(d))
#            #print(c.render())
#            row.addCell(c)
#        #print(row.render())
#        table.addRow(row)
#        table1.addRow(row)
#        table2.addRow(row)
#    row = HtmlRow()
#    c = HtmlCell(table1)
#    c1 = HtmlCell(table2)
#    row.addCells([c,c1])
#    table.addRow(row)
#
#
#    wrap= HtmlWrapper()
#    wrap.addContent(table)
#
#    f = open(os.path.normpath('../data/htmlformat.html'), 'w')
#    f.write(wrap.render())
#    f.close()
#    print(wrap.render())
