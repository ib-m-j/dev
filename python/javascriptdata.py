class GoogleHeader:
    def __init__(self, label, type = 'string', formatter = None, id = None):
        self.elements = {}
        self.elements['label']= label
        self.elements['type']= type
        self.elements['id']= id
        self.formatter = formatter

    def getRowCell(self):
        res = '{'
        for (key, value) in self.elements.items():
            if value:
                res = res + " {}: '{}',".format(key, value) 
        res = res[:-1]+'},'
        return res

    def getType(self):
        return self.elements['type']
        
    def hasFormatter(self):
        if self.formatter:
            return True
        return False
        

class GoogleValue:
    def __init__(self, value, format = None):
        self.elements = {}
        self.elements['v']= value
        self.elements['f']= format
        
    def getRowPart(self, header):
        res = '{'
        if 'v' in self.elements:
            if not 'f' in self.elements:
                if header.hasFormatter():
                    self.elements['f'] = header.formatter.format(
                        self.elements['v'])
                
            for (key, info) in self.elements.items():
                if info != None:
                    if header.elements['type'] == 'string':
                        formatter = "{}: '{}',"
                    else:
                       formatter = "{}: {},"
                    res = res + formatter.format(key, info)

            res = res[:-1] + "},"
            return res
        else:
            return 'null,'


def makeGoogleHeaderRow(listOfHeaderElements):
    res = '\n{\ncols: ['
    for value in listOfHeaderElements:
        res = res + value.getRowCell()
    res = res[:-1]+'],'
    return res

def makeGoogleDataRow(headers, listOfValues):
    res = '\n{c: ['
    for (v, h) in zip(listOfValues, headers):
        res = res + v.getRowPart(h)
    res = res[:-1]+']},'
    return res

