import itertools
import htmllayout

class Cell:
    def __init__(self, row, col, **Kwargs):
        self.row = row
        self.col = col
        for (k,v) in Kwargs.items():
            setattr(self,k,v)

class DisplayFocusResults:
    def __init__(self, tournament, focus):
        self.deal = focus.deal
        self.plays = []
        self.defences = []
        self.tournament = tournament
        self.cells = {}
        self.focus = focus
        
    def addElement(self, play):
        if play.bid.relevantFor(self.focus.bid):
            self.plays.append(play)
        else:
            self.defences.append(play)


    def renderAsHtmlTable(self):
        self.tableContent = htmllayout.ArrayContent('{:d}'.format)
        columns = []
        rows = []
        

        sameDirection = []
        otherDirection = []
        for p in self.plays:
            if not(p.NSResult in columns):
                columns.append(p.NSResult)
            
            if not(p.bid.strain in rows):
                rows.append(p.bid.strain)


        self.tableContent.setHeaderRow(columns, '{:d}'.format)
        self.tableContent.setHeaderColumn(rows)
        self.tableContent.setFocus(self.focus.bid.strain, self.focus.NSResult)

        for p in self.plays:
            (r,c) = self.tableContent.getCoord(p.bid.strain, p.NSResult)
            if self.tableContent.hasCell(r,c):
                self.tableContent.setContent(
                    r, c, self.tableContent.getContent(r,c) + 1)
            else:
                self.tableContent.setContent(r, c, 1)
        self.tableContent.sortRows(True)

        if len(self.defences) > 0:
            self.tableContent.addHeaderColumnValue('other direction')

            for p in self.defences:
                if not(p.NSResult in self.tableContent.headerRow):
                    self.tableContent.addHeaderRowValue(p.NSResult)

                if not(p.bid.strain in self.tableContent.headerColumn):
                    self.tableContent.addHeaderColumnValue(p.bid.strain)

            for p in self.defences:
                (r,c) = self.tableContent.getCoord(p.bid.strain, p.NSResult)
                if self.tableContent.hasCell(r,c):
                    self.tableContent.setContent(
                        r, c, self.tableContent.getContent(r,c) + 1)
                else:
                    self.tableContent.setContent(r, c, 1)
            #self.tableContent.sortRows(True)


        if self.focus.bid.bidder.getPair() == 'NS':
            self.tableContent.sortColumns()
        else:
            self.tableContent.sortColumns(True)
            res = []
            for x in self.tableContent.headerRow:
                res.append(-x)
            self.tableContent.headerRow = res


        res = self.tableContent.makeTable()
        res.addRowWithCell('')
        res.addRowWithCell('')
        res.addRowWithCell('')
        res.addRowWithCell('')
        return res

        #(r,c) = getCoord(self.focus, rows, columns)
        #self.cells[r][c].focus = '*'

        #for cKey in columns:
        #    line.append('{:d}'.format(sign*cKey))
        #lines.append(line)
        #
        #for r in range(len(rows)):
        #    line = [rows[r]]
        #    for c in range(len(columns)):
        #        cell = self.cells[r][c]
        #        if cell.value == 0:
        #            v = ''
        #        else:
        #            v = '{:d}'.format(cell.value)
        #        line.append(v+cell.focus)
        #    lines.append(line)
        #     
        #for l in lines:
        #    print(l)
        #print()
        #return lines
