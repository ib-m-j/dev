import sys
import re
import json

class JsObject:
    def __init__(self, content, start = '', end = ''):
        self.start = start
        self.end = end
        self.content = content
        self.tabs = 0

    def render(self, tabs = 0):
        return self.start+self.content.__str__()+self.end

    @staticmethod
    def makeJsObject(content):
        if isinstance(content, str):
            return JsStr(content)
        elif isinstance(content, list):
            jsContent = []
            for x in content:
                jsContent.append(JsObject.makeJsObject(x))
            return JsList(jsContent)
        elif isinstance(content, dict):
            jsContent = {}
            for (k,v) in content.items():
                jsContent[k] = JsObject.makeJsObject(v)
            return JsMap(jsContent)
        elif isinstance(content, JsObject):
            return content
        else:
            return JsObject(content, indent = 1)

class JsList(JsObject):
    def __init__(self, content):
        JsObject.__init__(self, content, '[',']')
        if not isinstance(content, list):
            raise (BaseException('need list in JsList'))
            

    def render(self, tabs):
        res = self.start
        for x in self.content:
            res = res + x.render(tabs + 1) + ', '
        return res[:-2] + self.end

    def addContent(self, element):
        self.content.append(element)
        
class JsMap(JsObject):
    def __init__(self, content):
        JsObject.__init__(self, content, '{','}')
        if not isinstance(content, dict):
            raise (BaseException('need dict in JsMap'))
            

    def render(self, tabs):
        res = self.start
        for (k,v) in self.content.items():
            res = res + '{}: {}, '.format(k, v.render(tabs + 1))
        return res[:-2] + self.end

    def addContent(self, key, value):
        self.content[key] = value
        
class JsStr(JsObject):
    def __init__(self, content):
        JsObject.__init__(self, content, "'","'")
        if not isinstance(content, str):
            raise (BaseException('need dict in JsMap'))
            

    def renderContent(self, tabs):
        res = self.content 
        return (res)




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
        
def makeGoogleValue(value, format = None):
    return {'v': value, 'f': format}

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

def makeGoogleDataRow(listOfValues):
    #res = '\n{c: ['
    #for (v, h) in zip(listOfValues, headers):
    #    res = res + v.getRowPart(h)
    #res = res[:-1]+']},'
    #return res
    row = {}
    row['c'] = listOfValues
    return json.dumps(row) + ','

def makeGoogleDataRows(listOfListOfValues):
    rows = []
    for listOfValues in listOfListOfValues:
        row = {'c': listOfValues}
        rows.append(row)
    return json.dumps(rows) 

def testJsObjects():
    testing = ['a', 4, ['a','b',3], {1:'a', 2:'b'}, 
               {3:['c','d'], 4:{1:1, 4:[1,2,3]}}]

    for x in testing:
        y = JsObject.makeJsObject(x)
        print( x, 'as JavaObject: ', y.render(0))
        
    compound = JsObject.makeJsObject(testing[-1])
    compound.addContent(6, JsObject.makeJsObject(testing[-2]))
                     
    print(compound.content, compound.render(0))
if __name__ == '__main__':
    testJsObjects()
