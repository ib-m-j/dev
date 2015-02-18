#import bridgecore

def getScore(bidValue, bidStrain, wonTricks, dbl, inZone):
    wonValue = wonTricks - 6 

    def gameBonus(inZone):
        if inZone:
            return 500
        return 300
            
    def smallSlamBonus(inZone):
        if inZone:
            return 750
        return 500

    def largeSlamBonus(inZone):
        if inZone:
            return 1500
        return 1000

    def overtrickValue(inZone, dbl, bidStrain, overTricks):
        if inZone:
            factor = 2
        else: 
            factor = 1

        if dbl == "P":
            return bidStrain.baseScore*overTricks
        elif dbl == "D":
            return 100*factor*overTricks
        else:
            return 200*factor*overTricks

    def defeatedScore(inZone, dbl, lostTricks):
        if inZone == True:
            factor = 2
        else:
            factor = 1

        if dbl == "D":
            dblFactor = 1
        elif dbl == "R":
            dblFactor = 2

        baseDbl = [100,300,500]
        baseDblInZone =[200,500,800]
        extraDownValue = 300
        simpleDown = 50
        extraDownTricks = lostTricks - 3
        if extraDownTricks < 0:
            extraDownTricks = 0

        if dbl == "P":
            return lostTricks*simpleDown*factor

        if lostTricks <= 3:
            if inZone:
                res = baseDblInZone[lostTricks - 1]
            else:
                res = baseDbl[lostTricks - 1]
        else:
            if inZone:
                res = baseDblInZone[-1]
            else:
                res = baseDbl[-1]
        res = res +  extraDownTricks*extraDownValue
        res = res *dblFactor
        return res
 
    if dbl == "P":
        factor = 1
    elif dbl == "D":
        factor = 2
    else:
        factor = 4

    
    if wonValue >= bidValue:
        #first the bid score
        res = (bidValue*bidStrain.baseScore + bidStrain.firstScore)*factor
        if res >= 100:
            res = res + gameBonus(inZone)
        else:
            res = res + 50
        
        if dbl == "D":
            res = res + 50
        elif dbl == "R":
            res = res + 100

        #other bonusses
        if bidValue == 6:
            res = res + smallSlamBonus(inZone)
        if bidValue == 7:
            res = res + largeSlamBonus(inZone)

        
        res = res + overtrickValue(inZone, dbl, bidStrain, wonValue - bidValue)

    else:
        res = -defeatedScore(inZone, dbl, bidValue - wonValue)


  #  return '{} {} - {} {} tricks {}\n'.format(
  #      bidValue, bidStrain, wonTricks, inZone, res)
    return res


def impScore(difference):
    thresholds = [0,20,50,90,130,170,220,270,320,370,430,500,600,750,900 \
                  ,1100,1300,1500,1750,2000,2250,2500,3000,3500,4000, 10000]

    if difference < 0:
        sign = -1
        difference = - difference
    else:
        sign = 1
    for (n,x) in enumerate(thresholds):
        if x>difference:
            break
    return sign*(n-1)

if __name__ == '__main__':
    for x in range(20):
        print(10*x*x, impScore(10*x*x))













