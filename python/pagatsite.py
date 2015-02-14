# -*- coding: iso-8859-1 -*-
import htmllayout
import readtournament
import os.path    
import display
import bridgecore

def getTeamFocusHtml(t):
    return ('Orion','Einar Poulsen')

def getEventId(t):
    #eventId, 
    return (1)

def makeTeamFocusPlay(t, play, focusTeamPlayer):
        print('starting play team focus', play.deal)
        br1 = htmllayout.HtmlBreak() #same break for all breaks
        wrap1 = htmllayout.HtmlWrapper()
        body1 = htmllayout.HtmlTag('<body>')
        body1.addAttribute("style","font-size:18pt")
        server = htmllayout.HtmlTag('<div>','', t.server)
        header = htmllayout.HtmlTag('','', t.name)
        space = htmllayout.HtmlTag('<div>','')
        bidString = htmllayout.HtmlTag('<div>','', play.bid.__str__())
        playedBy =  htmllayout.HtmlTag(
            '<div>','','Spillet af {}'.format(play.playedBy()[1]))
        scoreType = htmllayout.HtmlTag(
            '<div>','', 'Viser {} scoren'.format(play.pairOf(focusTeamPlayer)))
        iframe = htmllayout.HtmlTag('<iframe>','</iframe>')

        playerList = []
        #print(play.players)
        for seat in ['S','W','N','E']:
            playerList.append(
                (seat.lower(), play.players[bridgecore.Seat.fromId(seat)][1]))
            
        #print(playerList)
            

        iframe.addAttribute(
            'src', t.deals[play.deal].bridgebaseHand(
                playerList, play.bid.bridgebaseBid()))
        iframe.addAttribute('width', '400px')
        iframe.addAttribute('height', '400px')
        #table = htmllayout.HtmlTable()
        d = display.DisplayFocusResults(t, play, focusTeamPlayer)
        for p in t.plays:
            if p.deal == play.deal:
                d.addElement(p)
                #if p.hasTeamParticipant(play.playedBy()[0]) and p.playedBy() != play.playedBy():
                #    d.addTeamFocus(p)
    
        resulttable  = d.renderAsHtmlTable()

        wrap1.addContent(body1)
        #body1.addContent(header)
        #body1.addContent(server)
        body1.addContent(space)
        body1.addContent(iframe)
        body1.addContent(br1)
        body1.addContent(bidString)
        #body1.addContent(playedBy)
        body1.addContent(scoreType)
        body1.addContent(resulttable)

        return (
            getEventId(t), play.deal, play.pairOf(focusTeamPlayer), wrap1, body1)
        # need id for individual plays
        
def makeTeamTournamentHtml(t):
    focusTeamPlayer = getTeamFocusHtml(t)
    for team in t.teams:
        print(team)
        for p in t.teams[team].teamPlayers:
            print('\t',p)
    
    (playedByFocus, defendedByFocus) = t.getPlayedByPair(focusTeamPlayer)
    
    (wrap1, body1, br1) = htmllayout.getHtmlStart()

    list = htmllayout.HtmlList(
        os.path.normpath('..\\..\\..\\einarftp\\pagaten'), 'index', t.name)
    listElements = []

    for play in playedByFocus:
        (eventId, gameNo, focusPair, wrap1, body1) = makeTeamFocusPlay(
            t, play, focusTeamPlayer)
        list.addElement(
            '{:d}-{:d}{}'.format(eventId, gameNo, focusPair), 
            'Spil {:d} Svingscore  {:d} Rang {:d} af {:d}'.format(
                play.deal, 
                play.getResult(focusPair)- \
                t.getPlayedByTeamOther(focusTeamPlayer).getResult(focusPair),
                t.getRank(play, focusPair)[0], t.getRank(play, focusPair)[1]))

        listElements.append((wrap1, body1))

    for play in defendedByFocus:
        (eventId, gameNo, focusPair, wrap1, body1) = makeTeamFocusPlay(
            t, play, focusTeamPlayer)
        list.addElement(
            '{:d}-{:d}{}'.format(eventId, gameNo, focusPair), 
            'Spil {:d} Svingscore  {:d} Rang {:d} af {:d}'.format(
                play.deal, 
                play.getResult(focusPair)- \
                t.getPlayedByTeamOther(focusTeamPlayer).getResult(focusPair),
                t.getRank(play, focusPair)[0], t.getRank(play, focusPair)[1]))

        listElements.append((wrap1, body1))


    list.saveToFile(list.getFileNameAtBase(list.getMasterName()))
    for (n, (wrap, body)) in enumerate(listElements):
        body.addContent(list.getPreviousLink(n))
        body.addContent(list.getNextLink(n))
        wrap.saveToFile(list.getFileNameAtBase(list.getLinkFileName(n)))



def makePairTournament(t):
    pass

def makeTournamentHtml(server, url):
    (type, t) = readtournament.readTournament(server, url)
    print(len(t.teams), len(t.deals))
    if type == 'team':
        makeTeamTournamentHtml(t)
    else:
        makePairTournamentHtml(t)


if __name__ == '__main__':
    makeTournamentHtml('islevbridge.dk',
                       '/Resultat/Klub1/Turneringer/Resultat1082.html')

