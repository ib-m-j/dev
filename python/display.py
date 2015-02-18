import itertools
import htmllayout
import bridgecore

class Cell:
    def __init__(self, row, col, **Kwargs):
        self.row = row
        self.col = col
        for (k,v) in Kwargs.items():
            setattr(self,k,v)

class DisplayFocusResults:
    def __init__(self, tournament, focusPlay, focusTeamPlayer, caption):
        self.deal = focusPlay.deal
        self.primary = []
        self.secondary = []
        self.tournament = tournament
        self.cells = {}
        self.focusPlay = focusPlay
        self.focusTeamPlayer = focusTeamPlayer
        self.focusDirection = self.focusPlay.pairOf(focusTeamPlayer)
        self.otherDirection = self.focusPlay.seatOf(
            focusTeamPlayer).getOtherPairDK()
        self.caption = caption


    def addElement(self, play):
        if (play.hasTeamParticipant(self.focusTeamPlayer[0]) and 
            not play.hasParticipant(self.focusTeamPlayer)):
            isTeamPlay = True
        else: 
            isTeamPlay = False

        if (play.hasParticipant(self.focusTeamPlayer)):
            isFocusPlay = True
        else:
            isFocusPlay = False

        if (play.bid.isPassedBid() or 
            play.bid.bidder.getPair() == self.focusDirection):
            self.primary.append(play)
            if isTeamPlay:
                self.addTeamFocus(play, True)
            if isFocusPlay:
                self.focusIsPrimary = True
        else:
            self.secondary.append(play)
            if isTeamPlay:
                self.addTeamFocus(play, False)
            if isFocusPlay:
                self.focusIsPrimary = False



        #if play.hasTeamParticipant(
        #        self.focusPlay.playedBy()[0]) and play.playedBy(
        #        ) != self.focusPlay.playedBy():
        #    isTeamPlay = True
        #else:
        #    isTeamPlay = False

        #
        #if play.bid.relevantFor(self.focusPlay.bid):
        #    self.primary.append(play)
        #    if isTeamPlay:
        #        self.addTeamFocus(play, True)
        #else:
        #    self.secondary.append(play)
        #    self.addTeamFocus(play, False)
        #        #if p.hasTeamParticipant(play.playedBy()[0]) and p.playedBy() != play.playedBy():
        #        #    d.addTeamFocus(p)


    def addTeamFocus(self, play, isPrimary):
        self.teamFocusPlay = play
        self.teamFocusIsPrimary = isPrimary
    
    #def getTeamFocusPlay(self):
    #    return self.teamFocusPlay

    def getFocusResult(self, play):
        if self.focusDirection == 'NS':
            return play.NSResult
        else:
            return -play.NSResult
    

    def renderAsHtmlTable(self):
        self.primaryTableContent = htmllayout.ArrayContent('{:d}'.format)
        self.secondaryTableContent = htmllayout.ArrayContent('{:d}'.format)
        columns = []
        playerRows = []
        defenderRows = []
        
        for p in self.primary:
            if not(self.getFocusResult(p) in columns):
                    columns.append(self.getFocusResult(p))
            
            if not(p.bid.strain in playerRows):
                playerRows.append(p.bid.strain)


        for p in self.secondary:
            if not(self.getFocusResult(p) in columns):
                    columns.append(self.getFocusResult(p))

            if not(p.bid.strain in defenderRows):
                defenderRows.append(p.bid.strain)

        columns.sort()
        playerRows.sort()
        defenderRows.sort()

        self.primaryTableContent.setHeaderRow(columns, '{:d}'.format)
        self.primaryTableContent.setHeaderColumn(playerRows)
        self.secondaryTableContent.setHeaderRow(columns, '{:d}'.format)
        self.secondaryTableContent.setHeaderColumn(defenderRows)

        #if self.teamFocusIsPrimary:
        #    self.primaryTableContent.setTeamFocus(
        #        self.teamFocusPlay.bid.strain, 
        #        self.getFocusResult(self.teamFocusPlay))
        #else:
        #    self.secondaryTableContent.setTeamFocus(
        #        self.teamFocusPlay.bid.strain, 
        #        self.getFocusResult(self.teamFocusPlay))
            

        if len(self.primary) > 0:
            self.primaryTableContent.addFirstHeaderColumnValue(
                'Spillet af {}'.format(self.focusDirection))
            for p in self.primary:
                (r,c) = self.primaryTableContent.getCoord(p.bid.strain, 
                                               self.getFocusResult(p))
                if self.primaryTableContent.hasCell(r,c):
                    self.primaryTableContent.setContent(
                        r, c, self.primaryTableContent.getContent(r,c) + 1)
                else:
                    self.primaryTableContent.setContent(r, c, 1)

            if self.teamFocusIsPrimary:
                (r, c) = self.primaryTableContent.getCoord(
                    self.teamFocusPlay.bid.strain, 
                    self.getFocusResult(self.teamFocusPlay))
                self.primaryTableContent.setAttributes(
                    r,c,[('bgcolor','#FFAAAA')])
            if self.focusIsPrimary:
                (r, c) = self.primaryTableContent.getCoord(
                    self.focusPlay.bid.strain, 
                    self.getFocusResult(self.focusPlay))
                self.primaryTableContent.setAttributes(
                    r,c,[('bgcolor','#AAFFAA')])

        if len(self.secondary) > 0:
            self.secondaryTableContent.addFirstHeaderColumnValue(
                'Spillet af {}'.format(self.otherDirection))

            for p in self.secondary:
                (r,c) = self.secondaryTableContent.getCoord(
                    p.bid.strain, self.getFocusResult(p))
                if self.secondaryTableContent.hasCell(r,c):
                    self.secondaryTableContent.setContent(
                        r, c, self.secondaryTableContent.getContent(r,c) + 1)
                else:
                    self.secondaryTableContent.setContent(r, c, 1)
            if not(self.teamFocusIsPrimary):
                (r, c) = self.secondaryTableContent.getCoord(
                    self.teamFocusPlay.bid.strain, 
                    self.getFocusResult(self.teamFocusPlay))
                self.secondaryTableContent.setAttributes(
                    r,c,[('bgcolor','#FFAAAA')])
            if not(self.focusIsPrimary):
                (r, c) = self.secondaryTableContent.getCoord(
                    self.focusPlay.bid.strain, 
                    self.getFocusResult(self.focusPlay))
                self.secondaryTableContent.setAttributes(
                    r,c,[('bgcolor','#AAFFAA')])



            merged = self.primaryTableContent.expandRows(
                self.secondaryTableContent)
            return merged.makeTable(self.caption)

        return self.primaryTableContent.makeTable(self.caption)


class ScoreOverview:
    def __init__(self, t):
        self.tournament = t
        self.array = htmllayout.ArrayContent('{}'.format)
        self.array.setHeaderRow(['Svingscore', 'CrossImps', 'Rang'])
        strains = [x for x in bridgecore.Strain.strains.values()]
        strains.sort(reverse = True)
        self.array.setHeaderColumn([x.dkName() for x in strains])
        self.countArray = htmllayout.ArrayContent(str)
        self.countArray.setHeaderRow(self.array.headerRow)
        self.countArray.setHeaderColumn(self.array.headerColumn)

    def addPlay(self, focusPlay, focusPair, focusTeamPlayer):
        for column in self.array.headerRow:
            if column == 'CrossImps':
                toAdd = self.tournament.getCrossImps(focusPlay, focusPair)
            elif column == 'Rang':
                toAdd = self.tournament.getRank(focusPlay, focusPair)[0]
            else:
                toAdd = focusPlay.getResult(focusPair)- \
                self.tournament.getPlayedByTeamOther(
                    focusTeamPlayer).getResult(focusPair)

            (r,c) = self.array.getCoord(
                focusPlay.bid.strain.dkName(), column)

            if self.array.hasCell(r,c):
                self.array.setContent(r,c, self.array.getContent(r,c) + toAdd)
                self.countArray.setContent(r,c, self.countArray.getContent(r,c) + 1)
            else:
                self.array.setContent(r,c, toAdd)
                self.countArray.setContent(r,c, 1)

            
    def makeTable(self):
        for r in range(len(self.array.headerColumn)):
            for c in range(len(self.array.headerRow)):
                if self.array.hasCell(r,c):
                    self.array.setContent(r,c,
                        '{:.1f}'.format(
                    self.array.getContent(r,c)/self.countArray.getContent(r,c)))
        
        return self.array.makeTable('Oversigt')
                        
