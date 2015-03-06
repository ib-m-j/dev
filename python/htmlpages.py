import tournament
import htmllayout
import readtournament
import readresfile
import javascriptdata
import json
import os

def makeFocusViewTeam(tournament, focusTeamPlayer, id):
    (playedBy, defendedBy) = tournament.getParticipatedByPlayer(focusTeamPlayer)

    playRanks = {}
    defendRanks = {}

    playRanksList = []
    defendRanksList = []

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
                         javascriptdata.makeGoogleValue(
                             '{:d}'.format(played))])
        defendRows.append([googleTick, 
                           javascriptdata.makeGoogleValue(defended),
                           javascriptdata.makeGoogleValue(
                               '{:d}'.format(defended))] )
        
    playRowsString =  javascriptdata.makeGoogleDataRows(playRows) 
    defendRowsString =  javascriptdata.makeGoogleDataRows(defendRows) 
    ticksString = json.dumps(ticks)
    playDivTagName = 'play'
    defDivTagName = 'def'
    

    chartDef = htmllayout.GoogleChart(
        {'playdivtag' : 'play',
         'defdivtag' : 'def',
         'playrows' : playRowsString,
         'defrows' : defendRowsString,
         'ticks' : ticksString}, #neeed __str__()??
         os.path.join('..','javascript','focusviewteam.js')     
    )

    playTag = htmllayout.DivTag(playDivTagName)
    defTag = htmllayout.DivTag(defDivTagName)

    body = htmllayout.HtmlTag('<body>')
    head = htmllayout.HtmlTag('<head>')
    styles = htmllayout.HtmlTag('<style>')
    styles.addContent(
        'body {font-size: 36px;}\n \
        .theader {text-align: center; font-size : 1.2em;}\n \
        .title {text-align: center; font-size: 1.3em;}\n \
        .pageTitle {text-align: center; font-size: 1.5em;}\n',)
    head.addContent(styles)
    table = htmllayout.HtmlTable()
    table.addAttribute('width', '100%')
    (r,c) = table.addRowWithCell(tournament.name)
    c.addAttribute('class', 'pageTitle')
    (r,c) = table.addRowWithCell(
        'Antal spil fordelt efter parturnerings rang')
    c.addAttribute('class', 'title')
    link = htmllayout.HtmlLink(
        '{} spil med {} som spilfører'.format(
            len(playedBy), focusTeamPlayer[1]), 'url')
    (r,c) = table.addRowWithCell(link)
    c.addAttribute('class','theader')
    (r,c) = table.addRowWithCell(playTag)
    link = htmllayout.HtmlLink(
        '{} med {} som forsvarer'.format(
            len(defendedBy), focusTeamPlayer[1]),'url')
    (r,c) = table.addRowWithCell(link)
    c.addAttribute('class', 'theader')
    (r,c) = table.addRowWithCell(defTag)
    body.addContent(table)
    chartDef.setupData(head)
    wrap= htmllayout.HtmlWrapper()
    wrap.setHead(head)
    wrap.setBody(body)
    saveTo = os.path.normpath(
        '..\\..\\..\\einarftp\\pagaten\\{}.html'.format(id))
    wrap.saveToFile(saveTo)
    print("wrote file {}".format(saveTo));


def readTournament(server, url):
    res = readtournament.readOneTournament(server, url)

    #print(res)
    if res[0] == 'pair':
        for file in res[1]:
            readresfile.basicIslevPairs(
                readtournament.Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent())

    elif res[0] == 'team':
        t = tournament.Tournament()
        for file in res[1]: 
            readresfile.basicIslevTeams(
                readtournament.Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
   
        t.addOrigin(server, url)

    print(len(t.teams), len(t.deals))
    for team in t.teams:
        print(team)
        for p in t.teams[team].teamPlayers:
            print('\t', p, len(p))
    #only team implemented

    return (res[0], t)



def getTournamentFocus():
    (type, tournament) = readTournament(
        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1083.html')
    focus = ('Orion','Einar Poulsen')
    makeFocusViewTeam(tournament, focus, '1083')

    
if __name__ == '__main__':
    getTournamentFocus()
