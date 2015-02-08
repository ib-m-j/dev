# -*- coding: iso-8859-1 -*-
import htmllayout
import readtournament
import os.path    
import display
import bridgecore

def makeTournamentHtml(server, tournament, focus):
    t = readtournament.oneTournament(server, tournament)
    print(len(t.teams), len(t.deals))
    for team in t.teams:
        print(team)
        for p in t.teams[team].teamPlayers:
            print('\t',p)

    relevant = t.getPlayedByPair(focus)
    br = htmllayout.HtmlBreak()
    list = htmllayout.HtmlList(
        os.path.normpath('..\\..\\..\\einarftp\\pagaten'), 'index', t.name)
    listElements = []
    for play in relevant:
        print('starting play', play.deal)
        list.addElement('spil{:d}'.format(play.deal))
        wrap1 = htmllayout.HtmlWrapper()
        body1 = htmllayout.HtmlTag('<body>')
        body1.addAttribute("style","font-size:36pt")
        server = htmllayout.HtmlTag('<div>','', server)
        header = htmllayout.HtmlTag('','', t.name)
        space = htmllayout.HtmlTag('<div>','')
        bidString = htmllayout.HtmlTag('<div>','', play.bid.__str__())
        playedBy =  htmllayout.HtmlTag(
            '<div>','','Spillet af {}'.format(play.playedBy()[1]))
        scoreType = htmllayout.HtmlTag(
            '<div>','', 'Viser {} scoren'.format(play.pairOf(focus)))
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
        iframe.addAttribute('width', '600px')
        iframe.addAttribute('height', '600px')
        #table = htmllayout.HtmlTable()
        d = display.DisplayFocusResults(t, play, None)
        for p in t.plays:
            if p.deal == play.deal:
                d.addElement(p)
        resTable = d.renderAsHtmlTable()
        resTable.addAttribute('cellpadding','24')
        
        wrap1.addContent(body1)
        #body1.addContent(header)
        #body1.addContent(server)
        body1.addContent(space)
        body1.addContent(iframe)
        body1.addContent(br)
        body1.addContent(bidString)
        #body1.addContent(playedBy)
        body1.addContent(scoreType)
        body1.addContent(resTable)
        listElements.append((wrap1, body1))

    list.saveToFile(list.getFileNameAtBase(list.getMasterName()))
    for (n, (wrap, body)) in enumerate(listElements):
        body.addContent(list.getPreviousLink(n))
        body.addContent(list.getNextLink(n))
        wrap.saveToFile(list.getFileNameAtBase(list.getLinkFileName(n)))


if __name__ == '__main__':
    makeTournamentHtml('islevbridge.dk',
                       '/Resultat/Klub1/Turneringer/Resultat1082.html',
                       ('Orion','Einar Poulsen'))

