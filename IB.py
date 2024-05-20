import discord
import random
import dicemod
import math
import re

random.seed()

async def check(arg, a, b, channel):
  # Compares two values and return the degrees of success (in positive numberals) or failure (negative numerals).
  
  # When called by another function, gives a simple result of the degrees of success.
  if arg == "func":
    comp = a-b
    if comp >= 0:
      # Add 1 to correctly calculate degrees of success, as 0-4 are one degree of success.
      comp += 1
      return math.ceil(comp/5)
    else:
      return math.floor(comp/5)
    
  # When called directuly, gives a more verbose result.
  else:
    if "?" in arg:
      # Produces a help message explaining how to use the command.
      await channel.send("""**Comparison**
    To compare two numbers, you can use `$c`, `$check`, or `$compare`. Usage is as follows:
        `$c [Number] [DC to compare to]`
        
    This command does not accept any additional arguments.""")
      return
    
    if len(arg) == 3 and arg[1].isnumeric() and arg[2].isnumeric():
      # Only runs if it has the correct number of arguments and the arguments are numeric.
      a = int(arg[1])
      b = int(arg[2])
      
      comp = await check("func", a, b, channel)
      
      if comp == 1:
        await channel.send(arg[1] + " compared to a DC of " + arg[2] + " is 1 degree of success!")
      elif comp > 1:
        await channel.send(arg[1] + " compared to a DC of " + arg[2] + " is " + str(comp) + " degrees of success!")
      elif comp == -1:
        await channel.send(arg[1] + " compared to a DC of " + arg[2] + " is 1 degree of failure!")
      elif comp < -1:
        await channel.send(arg[1] + " compared to a DC of " + arg[2] + " is " + str(comp * -1) + " degrees of failure!")
      else:
        await channel.send("An error has occured. Please contact theVoidWatches at jc.weston@yahoo.com to report this bug.")
    else:
      await channel.send("Usage error. Please input 2 numbers to compare.")

async def graded(arg, channel, author):
  # Rolls a d20, adds the bonus if there is one, and compares to a given DC, or to 10 if no DC is provided. Can roll multiple times. Improved critical is permitted, as are hero points.

  if "?" in arg:
    await channel.send("""**Graded Check**
    To roll a generic check against a given DC, you can use `$g`, `$graded`, or `$dc`. Usage is as follows:
        `$a (Resistance Bonus) (DC) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no DC is provided, the DC will be assumed to be 10. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
       `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
       `imp1` `imp2` `imp3` `imp4` If any of these arguments are included, rolls will be counted as critical successes on numbers below 20, as if this roll was made using a number of ranks of Improved Critical.""")
    return

  #sets default values
  bonus = 0
  DC = 10
  rolls = 1

  #sets the value of the bonus and DC if args are provided
  if len(arg) > 1:
    try:
      bonus = int(arg[1])
    except:
      "Nothing here"
    if len(arg) > 2:
      try:
        DC = int(arg[2])
      except:
        "Nothing here"
      if len(arg) > 3:
        try:
          rolls = int(arg[3])
        except:
          "Nothing here"

  # Turns the bonus into a string
  if bonus == 0:
    bonusPrint = ""
  elif bonus > 0:
    bonusPrint = "+" + str(bonus)
  else:
    bonusPrint = str(bonus)

  # Creates the string to be populated and printed into the channel.
  printString = author + "\n"

  # Labels the string if a % argument is provided.
  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      printString += arg[a] + " "
    printString += "\n"

  for roll in range(rolls):
    # Generators a random number for the roll.
    result = random.randint(1,20)
    # The total and the result are different - the total will include bonuses.
    total = result

    # Checks if the roll was a crit
    crit = await dicemod.critCheck(arg, result, True)
    
    # Improves the result if you spent a hero point
    if "hp" in arg and result < 11:
      hp = ", increased by a hero point to " + str(total + 10)
      total += 10
    else:
      hp = ""

    # Adds the bonus to the total result.
    total += bonus

    # Checks the number of degrees of success
    degrees = await check("func", total, DC, channel)
    # Turns that into a verbose string
    degrees = await dicemod.degrees(degrees, DC, crit)

    # Adds the final result to the string that will be printd.
    printString += await dicemod.printResult(result, hp, bonusPrint, total, crit, degrees)

    # Adds a newline to the string that will be printed if this isn't the final roll to be made.
    if roll+1 != rolls:
      printString += "\n"

  # If the string is too long for a single Discord message, split it into individual lines. Otherwise, just send it.
  if len(printString) > 2000:
    finPrint = printString.splitlines()
    for line in finPrint:
      await channel.send(line)
  else:
    await channel.send(printString)
  return

async def other(arg, channel, author):
  if "?" in arg:
    await channel.send("""**Other Dice**
    To roll dice that are not d20s, you can use `$o` or `$other`. Usage is as follows:
        `$o (number of rolls)d[number of sides]+[bonus]`
    If no number of rolls is provided, a single roll will be made. If no number of sides is provided, an error will result. If no bonus is provided, nothing will be added.
    
    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.""")
    return

  # The regex search looks for a format of [number]d[number], possibly followed by + or - and another number.
  if len(arg) >= 2 and not re.search("^[1-9]*[dD][1-9]+0*[-\\+]?[0-9]*$", arg[1]) or len(arg) < 2:
    await channel.send("Usage error. Please input a number of dice with a given number of sides in the format #d# or #d#+#.")
    return

  # Splits the argument into a number of rolls, number of dice sides, and a bonus if there is one
  dice = re.split("[\\+\\-dD]", arg[1])

  # Saves the number of rolls to make and the number of sides to the die
  rolls = int(dice[0])  
  sides = int(dice[1])
  
  # Extracts the bonus from the dice array if it includes them.
  if len(dice) > 2:
    bonus = int(dice[2])
    if "-" in arg[1]:
      bonus = bonus * -1
    if bonus > 0:
      bonusPrint = "+" + dice[2]
    elif bonus < 0:
      bonusPrint = str(dice[2])
    else:
      bonus = ""
  else:
    bonus = 0
    bonusPrint = ""
  
  # Creates a string that will be printed to Discord.
  printString = author + "\n"

  # Adds messages preceded by the % argument, if there are any.
  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      printString += arg[a] + " "
    printString += "\n"

  # Rolls dice of the appropriate size and totals their results.
  total = 0
  for roll in range(rolls):
    result = random.randint(1,sides)
    total += result
    printString += "Rolled a " + str(result) + " on a d" + str(sides) + "!\n"
  total += bonus

  # Finishes the final message to print.
  printString += "\nThe final total is **" + str(total) + "!**"
    
  # If the string is too long for a single Discord message, split it into individual lines. Otherwise, just send it.
  if len(printString) > 2000:
    finPrint = printString.splitlines()
    for line in finPrint:
      await channel.send(line)
  else:
    await channel.send(printString)
  return

async def roll(arg, channel, author):
  if "?" in arg:
    await channel.send("""**Roll**
    To make a miscellaneous d20 roll, use `$r` or `$roll`. Usage is as follows:
        `$r (Bonus) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no affliction rank is provided, the DC will be assumed to be 0. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
        `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
        `imp1` `imp2` `imp3` `imp4` If any of these arguments are included, rolls will be counted as critical successes on numbers below 20, as if this roll was made using a number of ranks of Improved Critical.""")
    return
  
  #sets default values
  bonus = 0
  rolls = 1

  #sets the value of the bonus and DC if args are provided
  if len(arg) > 1:
    try:
      bonus = int(arg[1])
    except:
      "Nothing here"
    if len(arg) > 2:
      try:
        rolls = int(arg[2])
      except:
        "Nothing here"

  #turns the bonus into a string
  if bonus == 0:
    bonusPrint = ""
  else:
    if bonus > 0:
      bonusPrint = "+" + str(bonus)
    else:
      bonusPrint = str(bonus)

  printString = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      printString += arg[a] + " "
    printString += "\n"
  
  for roll in range(rolls):
    #rolls the number
    result = random.randint(1,20)
    total = result


    #checks if it was a crit
    crit = await dicemod.critCheck(arg, result, True)
    #improves the number if you spent a hero point or if this was a defense roll.
    if "hp" in arg and result < 11:
      total += 10
      hp = ", increased by a hero point to " + str(total)
    elif "def" in arg and result < 11:
      total += 10
      hp = ", increased as a Defend to " + str(total)
    else:
      hp = ""
    
    #adds the bonus
    total += bonus

    printString += await dicemod.printResult(result, hp, bonusPrint, total, crit, "")

    if roll + 1 != rolls:
      printString += "\n"

  # If the string is too long to be sent in a single Discord message, split it into individual lines. Otherwise, just send it.
  if len(printString) > 2000:
    finPrint = printString.splitlines()
    for line in finPrint:
      await channel.send(line)
  else:
    await channel.send(printString)
  return

async def tough(arg, channel, author):
  #will roll a d20, add the arg if there is one, and compare to a given number, or to 10 if no number is provided. Can roll multiple times. Skill Adept is permitted, as is improved critical and hero points.

  if "?" in arg:
    await channel.send("""**Toughness Check**
    To roll a check against an attack which deals damage, you can use `$t`, `$tough`, or `$toughness`. Usage is as follows:
        `$a (Resistance Bonus) (Damage Rank) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no Damage rank is provided, the rank will be assumed to be 0. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
       `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.""")
    return

  #sets default values
  bonus = 0
  DC = 15
  rolls = 1

  #sets the value of the bonus, DC, and number of rolls if args are provided
  if len(arg) > 1:
    try:
      bonus = int(arg[1])
    except:
      "Nothing here"
    if len(arg) > 2:
      try:
        DC += int(arg[2])
      except:
        "Nothing here"
      if len(arg) > 3:
        try:
          rolls = int(arg[3])
        except:
          "Nothing here"

  #turns the bonus into a string
  if bonus == 0:
    bonusPrint = ""
  else:
    if bonus > 0:
      bonusPrint = "+" + str(bonus)
    else:
      bonusPrint = str(bonus)

  printString = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      printString += arg[a] + " "
    printString += "\n"

  for roll in range(rolls):
    #rolls the number
    result = random.randint(1,20)
    total = result

    #checks if it was a crit
    crit = await dicemod.critCheck(arg, result, False)
    #improves the result if you spent a hero point
    if "hp" in arg and result < 11:
      total += 10
      hp = ", increased by a hero point to " + str(result + 10)
    else:
      hp = ""

    #gets the total result
    total += bonus

    #checks the number of degrees of success
    degrees = await check("func", total, DC, channel)
    #turns that into a string
    degreesPrint = await dicemod.degrees(degrees, DC, crit)

    #corrects degrees if it was a crit
    if crit != "":
      degrees += 1

    printString += await dicemod.printResult(result, hp, bonusPrint, total, crit, degreesPrint)

    if degrees >= 0:
      printString += " You take no penalty!"
    elif degrees == -1:
      printString += " That's a **Bruise!**"
    elif degrees == -2:
      printString += " That's a **Bruise** and you are **Dazed** until the end of your next turn!"
    elif degrees == -3:
      printString += " That's a **Bruise** and you are **Staggered!**"
    else:
      printString += " You are **Incapacitated!**"

    if roll + 1 != rolls:
      printString += "\n"

  # If the string is too long for a single Discord message, split it into individual lines. Otherwise, just send it.
  if len(printString) > 2000:
    finPrint = printString.splitlines()
    for line in finPrint:
      await channel.send(line)
  else:
    await channel.send(printString)
  return

async def weak(arg, channel, author):
  if "?" in arg:
    await channel.send("""**Toughness Check**
    To roll a check against an attack which deals damage, you can use `$t`, `$tough`, or `$toughness`. Usage is as follows:
        `$a (Resistance Bonus) (Damage Rank) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no Damage rank is provided, the rank will be assumed to be 0. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
       `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.""")
    return

  #sets default values
  bonus = 0
  DC = 10
  rolls = 1

  #sets the value of the bonus and DC if args are provided
  if len(arg) > 1:
    try:
      bonus = int(arg[1])
    except:
      "Nothing here"
    if len(arg) > 2:
      try:
        DC = 10+int(arg[2])
      except:
        "Nothing here"
      if len(arg) > 3:
        try:
          rolls = int(arg[3])
        except:
         "Nothing here"

  #turns the bonus into a string
  if bonus == 0:
    bonusPrint = ""
  else:
    if bonus > 0:
      bonusPrint = "+" + str(bonus)
    else:
      bonusPrint = str(bonus)

  printString = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      printString += arg[a] + " "
    printString += "\n"

  for roll in range(rolls):
    #rolls the number
    result = random.randint(1,20)
    total = result

    #improves the result if you spent a hero point
    if "hp" in arg and result < 11:
      total += 10
      hp = ", increased by a hero point to " + str(result + 10)
    else:
      hp = ""

    #gets the total result
    total += bonus

    pointsLost = DC - total

    printString += await dicemod.printResult(result, hp, bonusPrint, total, "", "") + "With a DC of " + str(DC) + ","

    if pointsLost > 0:
      printString += " you lose **" + str(pointsLost) + " PP** from the affected trait or traits!"
    else:
      printString += " you take no penalty!"

    if roll + 1 != rolls:
      printString += "\n"

  # If the string is too long for a single Discord message, split it into individual lines. Otherwise, just send it.
  if len(printString) > 2000:
    finPrint = printString.splitlines()
    for line in finPrint:
      await channel.send(line)
  else:
    await channel.send(printString)
  return

async def readArgs(arg, channel, author):
  #should be a series of ifs that ends with an else for a command it doesn't recognize
  for a in range(1,len(arg)):
    if not re.search("\\?|[a-z]|[A-Z]|%", arg[a]):
      arg[a] = str(eval(arg[a]))
    else:
      break


  match arg[0]:
    case "$help" | "$h" | "$?":
      await channel.send("""**Help**
    I recognize the following commands:
        `$affliction`, alias `$a` or `$aff`. This command is designed for rolling resistance checks against Afflictions. Usage is as follows:
            `$a (bonus) (Affliction rank) (number of rolls)`
        `$compare`, alias `$c` or `$check`. This command is designed for checking the degree of success between two numbers. Usage is as follows:
            `$c [number] [DC to compare to]`
        `$defense`, alias `$d` or `$def`. This command is designed for rolling Defend or Deflect rolls. Usage is as follows:
            `$d (defense) (number of rolls)`
        `$graded`, alias `$g` or `$dc`. This command is designed for comparing a roll to a specified DC. Usage is as follows:
            `$g (bonus) (dc)`
        `$other`, alias `$o`. This command is for rolling dice other than d20s. Usage is as follows:
            `$o (number of rolls)d[number of sides](+bonus)`
        `$roll`, alias `$r`. This command is for rolling d20s without comparing them to a DC. Usage is as follows:
            `$r (bonus) (number of rolls)`
        `$toughness`, alias `$t` or `$tough`. This command is designed for rolling resistance checks against Damage, typically using your Toughness bonus. Usage is as follows:
            `$t (bonus) (Damage rank) (number of rolls)`
        `$weaken`, alias `$w` or `$weak`. This command is designed for rolling resistance checks against Weakens. Usage is as follows:
            `$w (bonus) (Weaken rank) (number of rolls)`""")
      await channel.send("""** **
    Additional details on all of these commands can be seen by using the command with the `?` argument. Commands may also respond to the following arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
        `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
        `imp1` `imp2` `imp3` `imp4` If any of these arguments are included, rolls will be counted as critical successes on numbers below 20, as if this roll was made using a number of ranks of Improved Critical.""")
    case "$a" | "$aff"  "$affliction":
      if "?" in arg:
        await channel.send("""**Afflictions**
    To roll a resistance check against an affliction, you can use `$a`, `$aff`, or `$affliction`. Usage is as follows:
        `$a (Resistance Bonus) (Affliction Rank) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no affliction rank is provided, the DC will be assumed to be 0. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
        `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
           
    This is an alias for the *Graded Check* command (`$g` `$graded` `dc`)""")
      else:
        #removes disallowed commands
        while "imp1" in arg:
          arg.remove("imp1")
        while "imp2" in arg:
          arg.remove("imp2")
        while "imp3" in arg:
          arg.remove("imp3")
        while "imp4" in arg:
          arg.remove("imp4")
      
        #turns rank into DC
        if len(arg) > 2 and arg[2].isnumeric():
          arg[2] = str( int(arg[2]) + 10 )

        #calls graded
        await graded(arg, channel, author)
    case "$c" | "$compare" | "$check":
      await check(arg, 0, 0, channel)
    case "$d" | "$def" | "$defense":
      if "?" in arg:
        await channel.send("""**Defense**
    To roll a defense check using Deflect or the Defend action, you can use `$d`, `$def`, or `$defend`. Usage is as follows:
        `$d (Defense) (Number of Rolls)`
    If no defense bonus is provided, nothing will be added to the roll. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
    
    This is an alias for the *Roll* Command (`$r` `$roll`)""")
      else:
        while "imp1" in arg:
          arg.remove("imp1")
        while "imp2" in arg:
          arg.remove("imp2")
        while "imp3" in arg:
          arg.remove("imp3")
        while "imp4" in arg:
          arg.remove("imp4")
        while "hp" in arg:
          arg.remove("hp")
        arg.append("def")
        await roll(arg, channel, author)
    case "$g" | "$graded" | "$dc":
      await graded(arg, channel, author)
    case "$o" | "$other":
      await other(arg, channel, author)
    case "$r" | "$roll":
      await roll(arg, channel, author)
    case "$t" | "$tough" | "$toughness":
      await tough(arg, channel, author)
    case "$w" | "$weak" | "$weaken":
      await weak(arg, channel, author)
    case "$reset" | "$seed":
      random.seed()
      await channel.send("`I've reset my random number generator.`")
    case "$close" | "$kill":
      await channel.send("`Closing the Important Boi. The boi will restart in one minute.`")
      quit()
    case _:
      await channel.send("`I don't recognize that command.`")
