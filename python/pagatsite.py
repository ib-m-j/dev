# -*- coding: iso-8859-1 -*-
import htmllayout
import readtournament
import os.path    
import display
import bridgecore

def getTeamFocusHtml(t):
    return ('Orion','Einar Poulsen')


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
            t.getId(), play.deal, play.pairOf(focusTeamPlayer), wrap1, body1)
        # need id for individual plays
        
def makeTeamTournamentHtml(t, root):
    focusTeamPlayer = getTeamFocusHtml(t)
    for team in t.teams:
        print(team)
        for p in t.teams[team].teamPlayers:
            print('\t',p)
    
    print("eventid ", t.getId())
    (playedByFocus, defendedByFocus) = t.getPlayedByPair(focusTeamPlayer)
    
    #(wrap1, body1, br1) = htmllayout.getHtmlStart()


    list1 = htmllayout.HtmlList(root, 
        t.getId(), 'Spillet af par med {}'.format(focusTeamPlayer[1]))
    list2 = htmllayout.HtmlList(
        os.path.normpath(
            '..\\..\\..\\einarftp\\pagaten'), 
        t.getId(), 
        'Forsvaret af par med {}'.format(focusTeamPlayer[1]))
    listElements1 = []
    listElements2 = []

    for play in playedByFocus:
        (eventId, gameNo, focusPair, wrap1, body1) = makeTeamFocusPlay(
            t, play, focusTeamPlayer)
        list1.addElement(
            '{}-{}{}'.format(eventId, gameNo, focusPair), 
            'Spil {:d} Svingscore  {:d} Rang {:d} af {:d}'.format(
                play.deal, 
                play.getResult(focusPair)- \
                t.getPlayedByTeamOther(focusTeamPlayer).getResult(focusPair),
                t.getRank(play, focusPair)[0], t.getRank(play, focusPair)[1]))

        
        listElements1.append((wrap1, body1))

    for play in defendedByFocus:
        (eventId, gameNo, focusPair, wrap1, body1) = makeTeamFocusPlay(
            t, play, focusTeamPlayer)
        list2.addElement(
            '{}-{}{}'.format(eventId, gameNo, focusPair), 
            'Spil {:d} Svingscore  {:d} Rang {:d} af {:d}'.format(
                play.deal, 
                play.getResult(focusPair)- \
                t.getPlayedByTeamOther(focusTeamPlayer).getResult(focusPair),
                t.getRank(play, focusPair)[0], t.getRank(play, focusPair)[1]))

        listElements2.append((wrap1, body1))


    header = htmllayout.HtmlTag('<h2>','</h2>', t.name)
    body = htmllayout.HtmlTag('<body>')
    body.addAttribute("style","font-size:12pt")
    wrap= htmllayout.HtmlWrapper()
    wrap.addContent(body)
    body.addContent(header)
    body.addContent(list1.getTag())
    body.addContent(list2.getTag())
    url = list1.getFileNameAtBase(list1.getMasterName())
    wrap.saveToFile(url)
    
    #list1.render()
    for (n, (wrap, body)) in enumerate(listElements1):
        body.addContent(list1.getPreviousLink(n))
        body.addContent(list1.getNextLink(n))
        wrap.saveToFile(list1.getFileNameAtBase(list1.getLinkFileName(n)))

    #list2.render()
    for (n, (wrap, body)) in enumerate(listElements2):
        body.addContent(list2.getPreviousLink(n))
        body.addContent(list2.getNextLink(n))
        wrap.saveToFile(list2.getFileNameAtBase(list2.getLinkFileName(n)))

    return url

    
def makePairTournament(t):
    pass

def makeTournamentHtml(server, url, root):
    (type, t) = readtournament.readTournament(server, url)
    print(len(t.teams), len(t.deals))
    if type == 'team':
        return makeTeamTournamentHtml(t, root)
    else:
        return makePairTournamentHtml(t)

        

if __name__ == '__main__':
    
    url1 = makeTournamentHtml('islevbridge.dk',
                              '/Resultat/Klub1/Turneringer/Resultat1082.html',
                              os.path.normpath('..\\..\\..\\einarftp\\pagaten'))
    
    url2 = makeTournamentHtml('islevbridge.dk',
                              '/Resultat/Klub1/Turneringer/Resultat1067.html',
                              os.path.normpath('..\\..\\..\\einarftp\\pagaten'))

    url3 = makeTournamentHtml('islevbridge.dk',
                              '/Resultat/Klub1/Turneringer/Resultat1068.html',
                              os.path.normpath('..\\..\\..\\einarftp\\pagaten'))

    url4 = makeTournamentHtml('islevbridge.dk',
                              '/Resultat/Klub1/Turneringer/Resultat1069.html',
                              os.path.normpath('..\\..\\..\\einarftp\\pagaten'))

    wrap, body, br = htmllayout.getHtmlStart()
    header = htmllayout.HtmlTag('<H2>','</H2>','Pagat hold 2014-2015')
    urlRef1 = htmllayout.HtmlLink('1', url1)
    urlRef2 = htmllayout.HtmlLink('2', url2)
    urlRef3 = htmllayout.HtmlLink('3', url3)
    urlRef4 = htmllayout.HtmlLink('4', url4)
    body.addContent(urlRef1)
    body.addContent(br)
    body.addContent(urlRef2)
    body.addContent(br)
    body.addContent(urlRef3)
    body.addContent(br)
    body.addContent(urlRef4)
    body.addContent(br)
    wrap.saveToFile(os.path.normpath('..\\..\\..\\einarftp\\pagaten\\index.html'))
    
