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
        #res = makeTestRows(playRanksList,defendRanksList)

    playRows = []
    defendRows = []
    ticks = []
    max = 0
    for r in range(total + 1):
        played = playRanks.get(r, 0)
        if played > max:
            max = played
        defended = defendRanks.get(r, 0)
        if defended > max:
            max = defended
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
    hticksString = json.dumps(ticks)

    x = max // 6 + 1#max 6 ticks
    vticksMax = '{}'.format(max//x + 1)
    vticks = [x for x in range(max//x + 1)]
    vticksString = json.dumps(vticks)
    playDivTagName = 'play'
    defDivTagName = 'def'

    replace = {
        '¤playrows¤' : playRowsString,
        '¤defrows¤' : defendRowsString,
        '¤hticks¤' : hticksString,
        '¤vticks¤' : vticksString,
        '¤vmax¤' : vticksMax,
        '¤pagetitle¤' : tournament.name,
        '¤pagesubtitle¤' : 'Antal spil fordelt efter parturnerings rang',
        '¤playedtitle¤' : '{} spil med {} som spilfører'.format(
            len(playedBy), focusTeamPlayer[1]),
        '¤playedurl¤' : 'url',
        '¤playtabletag¤' : 'play',
        '¤deftitle¤' : '{} spil med {} som modspiller'.format(
            len(defendedBy), focusTeamPlayer[1]),
        '¤defurl¤' : 'url',
        '¤deftabletag¤' : 'def'
    }
        
    templateName = os.path.join('..','templates','focusteamview.html')
    f = open(templateName, 'r')
    content = f.read()
    f.close()

    res = content
    for (k,v) in replace.items():
        res = res.replace(k,v)
        
    
    saveTo = os.path.normpath(
        '..\\..\\..\\einarftp\\pagaten\\index.html')
    #saveTo = os.path.normpath(
    #    '..\\..\\..\\einarftp\\pagaten\\{}.html'.format(id))
    f = open(saveTo,'w')
    f.write(res)
    f.close()
    print("wrote file {}".format(saveTo));
    return os.path.basename(saveTo)

    

    #chartDef = htmllayout.GoogleChart(
    #    {'playdivtag' : 'play',
    #     'defdivtag' : 'def',
    #     'playrows' : playRowsString,
    #     'defrows' : defendRowsString,
    #     'ticks' : ticksString}, #neeed __str__()??
    #     os.path.join('..','javascript','focusviewteam.js')     
    #)
    #
    ##playTag = htmllayout.DivTag(playDivTagName)
    #defTag = htmllayout.DivTag(defDivTagName)
    #
    #body = htmllayout.HtmlTag('<body>')
    #head = htmllayout.HtmlTag('<head>')
    #styles = htmllayout.HtmlTag('<style>')
    #
    #
    #
    #styles.addContent(
    #    'body {font-size: 36px;}\n \
    #    .theader {text-align: center; font-size : 1.2em;}\n \
    #    .title {text-align: center; font-size: 1.3em;}\n \
    #    .pageTitle {text-align: center; font-size: 1.5em;}\n',)
    #head.addContent(styles)

    #table = htmllayout.HtmlTable()
    #table.addAttribute('width', '100%')
    #(r,c) = table.addRowWithCell(tournament.name)
    #c.addAttribute('class', 'pageTitle')
    #(r,c) = table.addRowWithCell(
    #    'Antal spil fordelt efter parturnerings rang')
    #c.addAttribute('class', 'title')
    #link = htmllayout.HtmlLink(
    #    '{} spil med {} som spilfører'.format(
    #        len(playedBy), focusTeamPlayer[1]), 'url')
    #(r,c) = table.addRowWithCell(link)
    #c.addAttribute('class','theader')
    #(r,c) = table.addRowWithCell(playTag)
    #link = htmllayout.HtmlLink(
    #    '{} med {} som forsvarer'.format(
    #        len(defendedBy), focusTeamPlayer[1]),'url')
    #(r,c) = table.addRowWithCell(link)
    #c.addAttribute('class', 'theader')
    #(r,c) = table.addRowWithCell(defTag)
    #body.addContent(table)
    #chartDef.setupData(head)
    #wrap= htmllayout.HtmlWrapper()
    #wrap.setHead(head)
    #wrap.setBody(body)
    #saveTo = os.path.normpath(
    #    '..\\..\\..\\einarftp\\pagaten\\{}.html'.format(id))
    #wrap.saveToFile(saveTo)
    #print("wrote file {}".format(saveTo));


# start hereXXXXXXdef makeFocusViewPair()
#below moved to readtournament
def old_readTournament(server, url):
    res = readtournament.readOneTournament(server, url)

    t = tournament.Tournament()
    t.addOrigin(server, url)
    t.type = res[0]
    if t.type == 'pair':
        for file in res[1]:
            readresfile.basicIslevPairs(
                readtournament.Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)

    elif t.type == 'team':
        for file in res[1]: 
            readresfile.basicIslevTeams(
                readtournament.Crawler.fromServerUrl(
                    'islevbridge.dk',file).getFileContent(), t)
   

        print(len(t.teams), len(t.deals))
        for team in t.teams:
            print(team)
            for p in t.teams[team].teamPlayers:
                print('\t', p, len(p))

    return (res[0], t)



#def getTournamentFocus():
#    (type, tournament) = readTournament(
#        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1083.html')
#    focus = ('Orion','Einar Poulsen')
#    makeFocusViewTeam(tournament, focus, '1083')
#
def getTournamentFocus():
    (type, tournament) = readTournament(
        'islevbridge.dk','/Resultat/Klub1/Turneringer/Resultat1140.html')
    focus = ('14877','Einar Poulsen')
    makeFocusViewTeam(tournament, focus, '1140')

    
if __name__ == '__main__':
    getTournamentFocus()
