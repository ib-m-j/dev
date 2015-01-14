import itertools
import htmllayout

class Cell:
    def __init__(self, row, col, **Kwargs):
        self.row = row
        self.col = col
        for (k,v) in Kwargs.items():
            setattr(self,k,v)

class Display:
    def __init__(self, tournament, deal):
        self.deal = deal
        self.plays = []
        self.tournament = tournament
        self.cells = {}
        
    def addElement(self, play):
        self.plays.append(play)

    def addFocus(self,focus):
        self.focus = focus

    def print(self):
        if self.focus.bid.bidder.getPair() == 'NS':
            sign = 1
        else:
            sign = -1
        
        columns = []
        rows = []
        for p in self.plays:
            if not(p.NSResult in columns):
                columns.append(p.NSResult)
            
            if not(p.displayStrainId() in rows):
                rows.append(p.displayStrainId())

        if sign == 1:
            columns.sort()
        else:
            columns.sort(reverse = True)
        
        for r in range(len(rows)):
            if not r in self.cells.keys():
                self.cells[r] = {}
            for c in range(len(columns)):
                self.cells[r][c] = Cell(r,c,value=0,focus='')
                
        def getCoord(x, r, c):
            return (r.index(x.displayStrainId()), c.index(x.NSResult))
                                        
        for p in self.plays:
            (r,c) = getCoord(p, rows, columns)
            self.cells[r][c].value = self.cells[r][c].value + 1
    
        (r,c) = getCoord(self.focus, rows, columns)
        self.cells[r][c].focus = '*'

        lines = []
        #lines.extend([[self.tournament.name],['game: {:d}'.format(self.deal)]])
        #lines.append([self.focus.bid.__str__()])
        #lines.append(['played by {}'.format(self.focus.playedBy()[1])])
        line =['']
        for cKey in columns:
            line.append('{:d}'.format(sign*cKey))
        lines.append(line)

        for r in range(len(rows)):
            line = [rows[r]]
            for c in range(len(columns)):
                cell = self.cells[r][c]
                if cell.value == 0:
                    v = ''
                else:
                    v = '{:d}'.format(cell.value)
                line.append(v+cell.focus)
            lines.append(line)
             
        for l in lines:
            print(l)
        print()
        return lines
