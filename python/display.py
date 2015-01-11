import itertools
class Display:
    def __init__(self, deal):
        self.deal = deal
        self.plays = []
        
    def addElement(self, play, focus = None):
        if focus:
            self.focus = play
        else:
            self.plays.append(play)
    
    def print(self):
        if self.focus.bid.bidder.getPair() == 'NS':
            sign = 1
        else:
            sign = -1
        
        columns = {}
        rows = {}
        for p in self.plays:
            if not(p.NSResult in columns.keys()):
                columns[p.NSResult] = [p]
            else:
                columns[p.NSResult].append(p)
        
        for p in self.plays:
            if not(p.bid.strain.id in rows.keys()):
                rows[p.bid.strain.id] = dict(itertools.zip_longest(columns.keys(),[],fillvalue = None))
            if not(rows[p.bid.strain.id][p.NSResult]):
                rows[p.bid.strain.id][p.NSResult] = []
            rows[p.bid.strain.id][p.NSResult].append(p.NSResult)
                
        c = [x for x in columns.keys()]
        c.sort()
        r = [x for x in rows.keys()]
        r.sort()

        lines = []
        line = ','
        for cKey in c:
            line = line + '{:d}'.format(cKey) + ',' 
        lines.append(line[:-1])

        for rKey in r:
            line = rKey+','
            for cKey in c:
                if rows[rKey][cKey] and len(rows[rKey][cKey])>0:
                    line = line + '{:d}'.format(len(rows[rKey][cKey])) + ','
                else:
                    line = line + ','
            lines.append(line[:-1])
             
        print('game: ', self.deal)
        for l in lines:
            print(l)
        print()
