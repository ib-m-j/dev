import html
import os

class HtmlTable:
    def __init__(self, rows = []):
        self.rows = rows

    def addRow(self, row):
        self.rows.append(row)

    def addRows(self, rows):
        self.rows.extend(rows)
    
    def render(self):
        res = '''<!doctype html public "-//W3C//DTD HTML 4.0//EN">
<html>
<table>\n'''
        for r in self.rows:
            res = res + '<tr>\n'
            for d in r:
                res = res + '<td>{}</td>\n'.format(html.escape(d))
            res = res + '</tr>\n'
        res = res + '</table>\n</html>\n'
        return res

    def writeAsFile(self, name):
        f = open(name, 'w')
        f.write(self.render())
        f.close()

if __name__ == '__main__':
    rows = []
    for r in ['a', 'b', 'c', 'd']:
        row = []
        for d in range(5):
            row.append('{}'.format(d))
        rows.append(row)
            
    table = HtmlTable(rows)
    f = open(os.path.normpath('../data/htmlformat.html'), 'w')
    f.write(table.render())
    f.close()
