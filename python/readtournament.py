# -*- coding: iso-8859-1 -*-

import http.client
import codecs
import re
import os.path
import readresfile
import tournament
import display
import htmllayout
import sys

#resultlink only used to read all tounaments from one file
resultlink = re.compile(
    '<a href="([a-zA-Z/]+Resultat[0-9]+.html)"',re.IGNORECASE)


#observe finds all a-zA-Z0-9_ or '/' - not . so cannot go to parent folder
anylink = re.compile('<a href="([\w/]+.html)',re.IGNORECASE)

class Crawler:
    def __init__(self, connection, url, searchFor = anylink):
        self.connection = connection
        #print(url)
        self.path = os.path.dirname(url).replace('\\', '/')
        self.file = os.path.basename(url)
        self.url = url
        self.searchFor = searchFor

    @staticmethod
    def fromServerUrl(server, url):
        conn = http.client.HTTPConnection(server)
        return Crawler(conn, url)

    def getFileContent(self):
        #print("requesting", self.url)
        self.connection.request("GET", self.url)
        r1 = self.connection.getresponse()
        #print(r1.status, r1.reason)
        data = codecs.decode(r1.read(),'latin-1')
        self.connection.close()
        return data
        
    def search(self):
        #print("requesting", self.url)
        self.connection.request("GET", self.url)
        r1 = self.connection.getresponse()
        #print(r1.status, r1.reason)
        data = codecs.decode(r1.read(),'latin-1')
        #print(data)
        allLinks = self.searchFor.findall(data)
        #print('found links:', allLinks)
        res = []
        for link in allLinks:
            newLink =os.path.normpath(
                os.path.join(self.path, link)).replace('\\','/')
            res.append(newLink)
        self.children =  res
        #print (res)
        return res
        
    def getChildTree(self, taken):
        self.search()
        res = [self]
        for link in self.children:
            if not link in taken:
                taken.append(link)
                childTree = Crawler(self.connection, link).getChildTree(taken)
                res.append(childTree)
        return res

    def getAllChildrenList(self, taken):
        self.search()
        res = []
        for link in self.children:
            if not link in taken:
                res.append(link)
                taken.append(link)
                childList = Crawler(
                    self.connection, link).getAllChildrenList(taken)
                res.extend(childList)
        return res



#server: islevbridge.dk
#url: /Resultat/Klub1/Turneringer/resultat1042.hml
def readOneTournament(server, url):
    conn = http.client.HTTPConnection(server)
    children = Crawler(conn, url).getAllChildrenList([])
    record = []
    type = None
    for line in children:
        #print(line)
        if 'MultiBord' in line:
            record.append(line.strip())
            type = 'team'
        if 'CG1' in line:
            record.append(line.strip())
            type = 'pair'
    conn.close()
    return (type, record)

#debugging
def printTreeLink(tree, level):
    res = ''
    if level == 0:
        pass
        #print(tree[0])
    if isinstance(tree[0], Crawler):
        res = res + '{}{}\n'.format('  '*level, os.path.basename(tree[0].url))
    else:
        res = res + printTreeLink(tree[0], level + 1)
    if len(tree) > 1:
        res = res + printTreeLink(tree[1:], level)
    return res


#only used to read all tournaments
def getAllFiles():
    conn = http.client.HTTPConnection("islevbridge.dk")
    resultFiles = Crawler(
        conn, "/Resultat/Klub1/KlubTurn.html", resultlink).search()
    #print('found ',len(resultFiles), 'resultFiles')
    resultFiles.sort()
    #for f in resultFiles[0:100]:
    #    print(f)
    resLinks = resultFiles[100:110]
    return resLinks

    #tree = []
    #taken = []
    #for link in resLinks:
    #    print(link)
    #    tree.extend(Crawler(conn, link).getChildTree(taken))
    #
    #print(printTreeLink(tree, 0))

    #f = open('allIslev.txt','w')
    #
    #f.write(printTreeLink(tree, 0))
    #f.close()
    

#debugging
def readLog():
    f = open('allIslev.txt', 'r')
    data = f.readlines()
    #print(data)
    f.close()
    print(len(data))
    
    files = []
    record = []
    for line in data:
        #print(line)
        if line[0] != ' ':
            if len(record) > 0:
                #print('appending record')
                files.append(record)
            record = [line.strip()]
        if 'MultiBord' in line:
            record.append(line.strip())
        if 'CG1' in line:
            record.append(line.strip())
    
    print(len(record))
    for rec in files:
        print(rec)

def oneTournament():
    res = readOneTournament(
        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1041.html')
    print(res)
            

def largeTest():
    all = getAllFiles()
    for url in all:
        print(url)
        res = readOneTournament(
            'islevbridge.dk',url)
        #print(res)
        if res[0] == 'pair':
            for file in res[1]:
                readresfile.basicIslevPairs(
                    Crawler.fromServerUrl(
                        'islevbridge.dk',file).getFileContent())
                
        elif res[0] == 'team':
            for file in res[1]:
                readresfile.basicIslevTeams(
                    Crawler.fromServerUrl(
                        'islevbridge.dk',file).getFileContent())

 
def onePairTournament():
    res = readOneTournament('islevbridge.dk',
                            '/Resultat/Klub1/Turneringer/Resultat1034.html')
    print(res)
    if res[0] == 'pair':
        for file in res[1]:
            readresfile.basicIslevPairs(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent())

def oneTournament(server, file):
    res = readOneTournament(server, file)
    #print(res)
    if res[0] == 'pair':
        #not developed
        for file in res[1]:
            readresfile.basicIslevPairs(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent())

    elif res[0] == 'team':
        t = tournament.Tournament()
        for file in res[1]: 
            readresfile.basicIslevTeams(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
   
    return t

def doPlayerFocus():
    #largeTest()
    #oneTournament()
    #onePairTournament()
    t = oneTournament('islevbridge.dk',
                          '/Resultat/Klub1/Turneringer/Resultat1082.html')

def readTournament(server, url):
    res = readOneTournament(server, url)

    #print(res)
    if res[0] == 'pair':
        for file in res[1]:
            readresfile.basicIslevPairs(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent())

    elif res[0] == 'team':
        t = tournament.Tournament()
        for file in res[1]: 
            readresfile.basicIslevTeams(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
   
        t.addOrigin(server, url)

    print(len(t.teams), len(t.deals))
    for team in t.teams:
        print(team)
        for p in t.teams[team].teamPlayers:
            print('\t', p, len(p))
    #only team implemented

    return (res[0], t)

def displayFocus(t, focusTeamPlayer, asPlayer, isTeam):
    #largeTest()
    #oneTournament()
    #onePairTournament()
    
    #assumning team for now

    all = t.getPlayedByPair(focus)
    if asPlayer:
        relevant=all[0]
    else:
        relevant = all[1]
    for play in relevant[:1]:
        d = display.DisplayFocusResults(
            t, play, focusTeamPlayer, 
            'Viser {} scoren'.format(play.pairOf(focusTeamPlayer)))
        print(play.deal,t.getPlayedByTeamOther(play.deal, focusTeamPlayer).deal)
        print(play.getResult('NS'))
        print(t.getPlayedByTeamOther(play.deal, focusTeamPlayer).getResult('NS'))
        for p in t.plays:
            if p.deal == play.deal:
                d.addElement(p)
    
def displayRanks(t, focusTeamPlayer, asPlayer):
    all = t.getPlayedByPair(focusTeamPlayer)
    if asPlayer:
        relevant=all[0]
    else:
        relevant = all[1]

    ranks = {}
    crossImps = {}
    for play in relevant:
        direction = play.pairOf(focusTeamPlayer)
        
        (r, total) = t.getRank(play, direction)
        cI  = t.getCrossImps(play, direction)
        if r in ranks.keys():
            ranks[r] = ranks[r] + 1
            crossImps[r] = crossImps[r] + cI
        else:
            crossImps[r] = cI
            ranks[r] = 1
        print(r, cI, crossImps[r])

    googleRows = ["\n['rang', 'antal', 'krydsImps'],"]
    for x in range(total + 1):
        row = "\n['{}'".format(x)
        if x in ranks:
            val = ranks[x]
            cIVal = crossImps[x]/val
        else:
            val = 0
            cIVal = 0

        row = row + ",{},{:.2f}".format(val, cIVal)
        row = row + '],'
        googleRows.append(row)
    res = ''
    for r in googleRows:
        res = res + r
    res = res[:-1]
    chartDef = htmllayout.GoogleChart(
        'rang', t.name, res, 'Antal spil med rang for {}'.format(
            focusTeamPlayer[1]))
    
    divtag = htmllayout.DivTag('rang')
    divtag.addAttribute('style',"width: 400px; height: 300px;")
    body = htmllayout.HtmlTag('<body>')
    body.addContent(divtag)
    
    chartDef.setupData()

    
    wrap= htmllayout.HtmlWrapper()
    wrap.setHead(chartDef)
    wrap.setBody(body)

    print(wrap.render())
    wrap.saveToFile('../data/testChart.html')
   



def doDefenderFocus():
    pass

if __name__ == '__main__':
    (type, tournament) = readTournament(
        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1069.html')
    focus = ('Orion','Einar Poulsen')
    #focus = ('Lille O','Lars Sørensen')
 
    
    #displayFocus(tournament, focus, True, True)
    #asPlayer or asDefender
    #type = team or pairs
    #displayRanks(tournament, focus, False)
    (a,b) = tournament.makeTableInput(focus)
    print(a)
    for r in b:
        print(r)
