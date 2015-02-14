import itertools
import htmllayout

class Cell:
    def __init__(self, row, col, **Kwargs):
        self.row = row
        self.col = col
        for (k,v) in Kwargs.items():
            setattr(self,k,v)

class DisplayFocusResults:
    def __init__(self, tournament, focusPlay, focusTeamPlayer):
        self.deal = focusPlay.deal
        self.primary = []
        self.secondary = []
        self.tournament = tournament
        self.cells = {}
        self.focusPlay = focusPlay
        self.focusTeamPlayer = focusTeamPlayer
        self.focusDirection = self.focusPlay.pairOf(focusTeamPlayer)

        #if self.focus.bid.bidder.getPair() == 'NS':
        #    if focusOnDefender:
        #        self.focusDirection == 'EW'
        #    else:
        #        self.focusDirection = 'NS'
        #else:
        #    if focusOnDefender:
        #        self.focusDirection == 'NS'
        #    else:
        #        self.focusDirection = 'EW'

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
            self.primaryTableContent.setAttributes(r,c,[('bgcolor','#FFAAAA')])
        if self.focusIsPrimary:
            (r, c) = self.primaryTableContent.getCoord(
                self.focusPlay.bid.strain, self.getFocusResult(self.focusPlay))
            self.primaryTableContent.setAttributes(r,c,[('bgcolor','#AAFFAA')])

        if len(self.secondary) > 0:
            defenceDir = self.focusPlay.bid.bidder.getOtherPair()
            self.secondaryTableContent.addFirstHeaderColumnValue(
                'Spillet af {}'.format(defenceDir))

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
            return merged.makeTable()

        return self.primaryTableContent.makeTable()


