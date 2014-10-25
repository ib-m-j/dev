import bridgecore


def evalHand(hand):
    eval = {}
    bestColour = None
    bestLength = 0

    for c in bridgecore.Colour.colours.values():
        cardOfColour = hand.getCardsOfColour(c)
        #points = points(cordOfColour)
        length = len(cardOfColour)
        eval[c] = length
        if bestLength < length:
            bestLength = length
            bestColour = c

    return (bestColour, bestLength)


def getBestHandAndColour(dealt):
    bestSeat = None
    bestLength = 0
    bestColour = None
    print(dealt)
    for (seat, hand) in dealt.items():
        print(seat, hand)
        (colour, length) = evalHand(hand)
        if bestLength < length:
            bestLength = length
            bestSeat = seat
            bestColour = colour

    return (bestSeat, bestLength, bestColour)

if __name__ == '__main__':
    dealt = {}
    shuffled = bridgecore.deck.shuffle()
    dealtList = shuffled.deal([13,13,13])
    #    print(dealtList[0].cardsByColour())
    #    print (evalHand(dealtList[0]))
    for (place, cards) in zip(bridgecore.Seat.all, dealtList):
        dealt[place] = bridgecore.Cards(cards)

    (bestSeat, bestLength, bestColour) = getBestHandAndColour(dealt)
    print (bestSeat, bestLength, bestColour)
