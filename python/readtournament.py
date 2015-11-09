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
import javascriptdata
import json



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
    t = tournament.Tournament()
    t.addOrigin(server, url)

    #print(res)
    if res[0] == 'pair':
        for file in res[1]:
            readresfile.basicIslevPairs(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
    
    elif res[0] == 'team':
        for file in res[1]: 
            readresfile.basicIslevTeams(
                Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
   
 
        #t = tournament.Tournament()
        #t.addOrigin(server, url)
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

    all = t.getParticipatedByPlayer(focusTeamPlayer)
    if asPlayer:
        relevant=all[0]
    else:
        relevant = all[1]
    for play in relevant[:1]:
        d = display.DisplayFocusResults(
            t, play, focusTeamPlayer, 
            'Viser {} scoren'.format(play.pairOf(focusTeamPlayer)))
        print(play)
        print(play.deal,t.getPlayedByTeamOther(play.deal, focusTeamPlayer).deal)
        print(play.getResult('NS'))
        print(t.getPlayedByTeamOther(play.deal, focusTeamPlayer).getResult('NS'))
        for p in t.plays:
            if p.deal == play.deal:
                d.addElement(p)

def makeTestRows(playRankList, defendRankList):
    header1 = javascriptdata.GoogleHeader('rang', 'number')
    header2 = javascriptdata.GoogleHeader('spil', 'number')
    header3 = javascriptdata.GoogleHeader('type', 'string')

    headers = [header1, header2, header3]
    tableDataString = javascriptdata.makeGoogleHeaderRow(headers)
    tableDataString = tableDataString  + '\nrows: '

    #    for (r,p) in playRankList:
    #        tableDataString = tableDataString + javascriptdata.makeGoogleDataRow(
    #                [javascriptdata.makeGoogleValue(r), 
    #                javascriptdata.makeGoogleValue(p), 
    #                javascriptdata.makeGoogleValue('play')])
    #    for (r,p) in defendRankList:
    #        tableDataString = tableDataString + javascriptdata.makeGoogleDataRow(
    #            #headers, [
    #            [javascriptdata.makeGoogleValue(r), 
    #            javascriptdata.makeGoogleValue(p), 
    #            javascriptdata.makeGoogleValue('defend')])
    
    rows = []
    for (r,p) in playRankList:
        rows.append([javascriptdata.makeGoogleValue(r), 
                     javascriptdata.makeGoogleValue(p), 
                     javascriptdata.makeGoogleValue('play')])
    for (r,p) in defendRankList:
        rows.append([javascriptdata.makeGoogleValue(r), 
                     javascriptdata.makeGoogleValue(p), 
                     javascriptdata.makeGoogleValue('defend')])
        
    tableDataString = tableDataString + javascriptdata.makeGoogleDataRows(rows) 
                           
    tableDataString = tableDataString[:-1] + ']}'
    return tableDataString

def displayRanks(t, focusTeamPlayer, asPlayer):
    all = t.getPlayedByPair(focusTeamPlayer)
    if asPlayer:
        relevant=all[0]
    else:
        relevant = all[1]

    playRanks = {}
    defendRanks = {}
    playRanksList = []
    defendRanksList = []
    countPlays = 0
    countDefends = 0
    #crossImps = {}
    print(all)
    for (n, inputList) in enumerate(list(all)):
        for play in inputList:
            direction = play.pairOf(focusTeamPlayer)
            if n == 0:
                target = playRanks
                targetList = playRanksList
                countPlays += 1
            else:
                target = defendRanks
                targetList = defendRanksList
                countDefends += 1

            (r, total) = t.getRank(play, direction)
            targetList.append((r, play.deal))
            if r in target.keys():
                target[r] = target[r] + 1
            else:
                target[r] = 1
            print(n, r, target[r])


#    header1 = javascriptdata.GoogleHeader('rang')
#    header2 = javascriptdata.GoogleHeader(
#        'som spiller: {} i alt'.format(countPlays), 'number')
#    header3 = javascriptdata.GoogleHeader(
#        'som forsvarer: {} i alt'.format(countDefends), 'number')
#
#    headers = [header1, header2, header3]
#    tableDataString = javascriptdata.makeGoogleHeaderRow(headers)
#    tableDataString = tableDataString + 'rows:  '
#    for x in range(total + 1):
#        values = []
#        values.append(javascriptdata.GoogleValue('{:.0f}%'.format(x*100/total)))
#        if x in playRanks:
#            player =  playRanks[x]
#        else:
#            player = 0
#        if x in defendRanks:
#            defender = defendRanks[x]
#        else:
#            defender = 0
#        values.extend([javascriptdata.GoogleValue(player),
#                       javascriptdata.GoogleValue(defender)])
#        
#        tableDataString = tableDataString + javascriptdata.makeGoogleDataRow(headers, values)
#                           
#        tableDataString = tableDataString[:-1] + '}'
#
#    #trying with test res


    res = makeTestRows(playRanksList,defendRanksList)


    chartDef = htmllayout.GoogleChart(
        'rang', t.name, res, 'Antal spil med rang for {}'.format(
            focusTeamPlayer[1]))
    
    divtag = htmllayout.DivTag('rang')
    divtag.addAttribute('style',"width: 40%; height: 400px;")
    body = htmllayout.HtmlTag('<body>')
    body.addContent(divtag)
    
    chartDef.setupData()

    
    wrap= htmllayout.HtmlWrapper()
    wrap.setHead(chartDef)
    wrap.setBody(body)

    print(wrap.render())
    wrap.saveToFile('../data/testChart.html')
   
def makeFocusViewTeam(tournament, focusTeamPlayer):
    (playedBy, defendedBy) = tournament.getParticipatedByPlayer(focusTeamPlayer)

    playRanks = {}
    defendRanks = {}

    playRanksList = []
    defendRanksList = []

    #crossImps = {}
    for play in playedBy:
        direction = play.pairOf(focusTeamPlayer)
        (r, total) = tournament.getRank(play, direction)
        playRanksList.append((r, play.deal))
        playRanks[r] = playRanks.get(r, 0) + 1
        
    for play in defendedBy:
        direction = play.pairOf(focusTeamPlayer)
        (r, total) = tournament.getRank(play, direction)
        defendRanksList.append((r, play.deal))
        defendRanks[r] = defendRanks.get(r, 0) + 1
        res = makeTestRows(playRanksList,defendRanksList)

    playRows = []
    defendRows = []
    ticks = []
    for r in range(total + 1):
        played = playRanks.get(r, 0)
        defended = defendRanks.get(r, 0)
        tick = round(r/total, 2) 
        tickFormat = '{:.0f}%'.format(tick*100) 
        googleTick = javascriptdata.makeGoogleValue(tick, tickFormat)
        ticks.append(googleTick)
        playRows.append([googleTick, 
                         javascriptdata.makeGoogleValue(played),
                         javascriptdata.makeGoogleValue('{:d}'.format(played))])
        defendRows.append([googleTick, 
                           javascriptdata.makeGoogleValue(defended),
                           javascriptdata.makeGoogleValue('{:d}'.format(defended))] )
        
    playRowsString =  javascriptdata.makeGoogleDataRows(playRows) 
    defendRowsString =  javascriptdata.makeGoogleDataRows(defendRows) 
    ticksString = json.dumps(ticks)

    chartDef = htmllayout.GoogleChart(
        'play', 'def', 'TITLE', playRowsString, defendRowsString, ticksString)
    
    (playTag, defTag) = chartDef.getDivTags()
    playTag.addAttribute('height', 500)
    defTag.addAttribute('height', 500)

    body = htmllayout.HtmlTag('<body>')
    head = htmllayout.HtmlTag('<head>')
    styles = htmllayout.HtmlTag('<style>')
    styles.addContent(
        'body {font-size: 100%;} \
        .theader {text-align: center; font-size : 1.2em;} \
        .title {text-align: center; font-size: 1.5em;')
    head.addContent(styles)
    table = htmllayout.HtmlTable()
    table.addAttribute('width', '500px')
    (r,c) = table.addRowWithCell(
        'Antal spil fordelt efter parturnerings rang')
    c.addAttribute('class', 'title')
    link = htmllayout.HtmlLink(
        '- med {} som spilfører'.format(focusTeamPlayer[1]),'url')
    (r,c) = table.addRowWithCell(link)
    c.addAttribute('class','theader')
    table.addRowWithCell(playTag)
    (r,c) = table.addRowWithCell(
        '- med {} som forsvarer'.format(focusTeamPlayer[1]))
    c.addAttribute('class', 'theader')
    (r,c) = table.addRowWithCell(defTag)
    body.addContent(table)
    chartDef.setupData(head)
    wrap= htmllayout.HtmlWrapper()
    wrap.setHead(head)
    wrap.setBody(body)
    wrap.saveToFile('../data/testChart.html')
    print("wrote file ../data/testChart.html");
 
def makeFocusViewPair(tournament, focusPlayer):
#XXXXXXXXXX
    (playedBy, defendedBy) = tournament.getParticipatedByPlayer(focusPlayer)

    #print(playedBy, defendedBy)

    playRanks = {}
    defendRanks = {}

    playRanksList = []
    defendRanksList = []

    #crossImps = {}
    for play in playedBy:
        direction = play.pairOf(focusPlayer)
        (r, total) = tournament.getRank(play, direction)
        playRanksList.append((r, play.deal))
        playRanks[r] = playRanks.get(r, 0) + 1
        
    for play in defendedBy:
        direction = play.pairOf(focusPlayer)
        (r, total) = tournament.getRank(play, direction)
        defendRanksList.append((r, play.deal))
        defendRanks[r] = defendRanks.get(r, 0) + 1
        res = makeTestRows(playRanksList,defendRanksList)

    playRows = []
    defendRows = []
    ticks = []
    for r in range(total + 1):
        played = playRanks.get(r, 0)
        defended = defendRanks.get(r, 0)
        tick = round(r/total, 2) 
        tickFormat = '{:.0f}%'.format(tick*100) 
        googleTick = javascriptdata.makeGoogleValue(tick, tickFormat)
        ticks.append(googleTick)
        playRows.append([googleTick, 
                         javascriptdata.makeGoogleValue(played),
                         javascriptdata.makeGoogleValue('{:d}'.format(played))])
        defendRows.append([googleTick, 
                           javascriptdata.makeGoogleValue(defended),
                           javascriptdata.makeGoogleValue('{:d}'.format(defended))] )
        
    playRowsString =  javascriptdata.makeGoogleDataRows(playRows) 
    defendRowsString =  javascriptdata.makeGoogleDataRows(defendRows) 
    ticksString = json.dumps(ticks)

    chartDef = htmllayout.GoogleChart(
        'play', 'def', 'TITLE', playRowsString, defendRowsString, ticksString)
    
    (playTag, defTag) = chartDef.getDivTags()
    playTag.addAttribute('height', 500)
    defTag.addAttribute('height', 500)

    body = htmllayout.HtmlTag('<body>')
    head = htmllayout.HtmlTag('<head>')
    styles = htmllayout.HtmlTag('<style>')
    styles.addContent(
        'body {font-size: 100%;} \
        .theader {text-align: center; font-size : 1.2em;} \
        .title {text-align: center; font-size: 1.5em;')
    head.addContent(styles)
    table = htmllayout.HtmlTable()
    table.addAttribute('width', '500px')
    (r,c) = table.addRowWithCell(
        'Antal spil fordelt efter parturnerings rang')
    c.addAttribute('class', 'title')
    link = htmllayout.HtmlLink(
        '- med {} som spilfører'.format(focusPlayer[1]),'url')
    (r,c) = table.addRowWithCell(link)
    c.addAttribute('class','theader')
    table.addRowWithCell(playTag)
    (r,c) = table.addRowWithCell(
        '- med {} som forsvarer'.format(focusPlayer[1]))
    c.addAttribute('class', 'theader')
    (r,c) = table.addRowWithCell(defTag)
    body.addContent(table)
    chartDef.setupData(head)
    wrap= htmllayout.HtmlWrapper()
    wrap.setHead(head)
    wrap.setBody(body)
    wrap.saveToFile('../data/testChart.html')
    print("wrote file ../data/testChart.html");
 



def doDefenderFocus():
    pass

if __name__ == '__main__':
    pass
# belwo may be used for trestingf
#    (type, tournament) = readTournament(
#        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1140.html')
#        #'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1069.html')
#    focus = ('14877','Einar Poulsen')
#    if type == 'team':
#        makeFocusViewTeam(tournament, focus)
#    else:
#        print('starting pairs')
#        makeFocusViewPair(tournament, focus)
#
    #focus = ('Lille O','Lars Sørensen')
 
    
    #displayFocus(tournament, focus, True, True)
    #asPlayer or asDefender
    #type = team or pairs
    #displayRanks(tournament, focus, False)
    #(a,b) = tournament.makeTableInput(focus)
    #print(a)
    #for r in b:
    #    print(r)
