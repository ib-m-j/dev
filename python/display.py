import itertools
import htmllayout

class Cell:
    def __init__(self, row, col, **Kwargs):
        self.row = row
        self.col = col
        for (k,v) in Kwargs.items():
            setattr(self,k,v)

class DisplayFocusResults:
    def __init__(self, tournament, focus, focusOnDefender):
        self.deal = focus.deal
        self.plays = []
        self.defences = []
        self.tournament = tournament
        self.cells = {}
        self.focus = focus
        if self.focus.bid.bidder.getPair() == 'NS':
            if focusOnDefender:
                self.focusDirection == 'EW'
            else:
                self.focusDirection = 'NS'
        else:
            if focusOnDefender:
                self.focusDirection == 'NS'
            else:
                self.focusDirection = 'EW'

    def addElement(self, play):
        if play.bid.relevantFor(self.focus.bid):
            self.plays.append(play)
        else:
            self.defences.append(play)

    def getFocusResult(self, play):
        if self.focusDirection == 'NS':
            return play.NSResult
        else:
            return -play.NSResult
    

    def renderAsHtmlTable(self):
        self.tableContent = htmllayout.ArrayContent('{:d}'.format)
        columns = []
        rows = []
        
        for p in self.plays:
            if not(self.getFocusResult(p) in columns):
                    columns.append(self.getFocusResult(p))
            
            if not(p.bid.strain in rows):
                rows.append(p.bid.strain)


        self.tableContent.setHeaderRow(columns, '{:d}'.format)
        self.tableContent.setHeaderColumn(rows)
        self.tableContent.setFocus(
            self.focus.bid.strain, self.getFocusResult(self.focus))

        for p in self.plays:
            (r,c) = self.tableContent.getCoord(p.bid.strain, 
                                               self.getFocusResult(p))
            if self.tableContent.hasCell(r,c):
                self.tableContent.setContent(
                    r, c, self.tableContent.getContent(r,c) + 1)
            else:
                self.tableContent.setContent(r, c, 1)
        self.tableContent.sortRows(True)

        #this does not work must be passed as parameter to makeTable
        #dirText = 'Viser {} scoren'.format( self.focus.bid.bidder.getPair())
        #self.tableContent.headerColumn[0] ='xxxxx' # dirText

        if len(self.defences) > 0:
            defenceDir = self.focus.bid.bidder.getOtherPair()
            self.tableContent.addHeaderColumnValue(
                'Spillet af {}'.format(defenceDir))

            for p in self.defences:
                if not(self.getFocusResult(p) in self.tableContent.headerRow):
                    self.tableContent.addHeaderRowValue(self.getFocusResult(p))

                if not(p.bid.strain in self.tableContent.headerColumn):
                    self.tableContent.addHeaderColumnValue(p.bid.strain)

            for p in self.defences:
                (r,c) = self.tableContent.getCoord(
                    p.bid.strain, self.getFocusResult(p))
                if self.tableContent.hasCell(r,c):
                    self.tableContent.setContent(
                        r, c, self.tableContent.getContent(r,c) + 1)
                else:
                    self.tableContent.setContent(r, c, 1)
            #self.tableContent.sortRows(True)

        self.tableContent.sortColumns()

        #if self.focus.bid.bidder.getPair() == 'NS' and not FocusOnDefender:
        #else:
        #    self.tableContent.sortColumns(True)
        #    res = []
        #    for x in self.tableContent.headerRow:
        #        res.append(-x)
        #    self.tableContent.headerRow = res


        res = self.tableContent.makeTable()
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
