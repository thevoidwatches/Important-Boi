import discord

async def critCheck(arg, result, improved):
  #closes immediately if this is a roll for minions
  if "min" in arg or "minion" in arg or "m" in arg:
    return ""

  #sets critical value
  critVal = 20
  if improved == True:
    if "imp4" in arg:
      critVal = 16
    elif "imp3" in arg:
      critVal = 17
    elif "imp2" in arg:
      critVal = 18
    elif "imp1" in arg:
      critVal = 19
      
  #checks if it was a crit
  if result >= critVal:
    return "**, which is a **crit"
  else:
    return ""

async def degrees(degrees, DC, crit):
  #takes in the degrees of success, the DC, and if the roll was a crit, and returns a verbose string string of it
  if crit != "":
    degrees += 1
  if degrees >= 0:
    if degrees <= 1:
      ret = "Against a DC of " + str(DC) + ", that's 1 degree of success!"
    else:
      ret = "Against a DC of " + str(DC) + ", that's " + str(degrees) + " degrees of success!"
  else:
    if degrees == -1:
      ret = "Against a DC of " + str(DC) + ", that's 1 degree of failure!"
    else:
      ret = "Against a DC of " + str(DC) + ", that's " + str(degrees * -1) + " degrees of failure!"
  return ret

async def printResult(result, sa, hp, bonus, total, crit, degrees):
  crit5 = ""
  if crit != "":
    crit5 = "That's an effective **" + str(total + 5) + "!** "

  if result == total:
    return "Rolled a **" + str(result) + crit + "!** " + crit5 + degrees
  return "Rolled a " + str(result) + sa + hp + bonus + ", for a total of **" + str(total) + crit + "**! " + crit5 + degrees