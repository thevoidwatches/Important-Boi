import discord
import random
import dicemod
import math
import re

random.seed()

async def check(arg, a, b, channel):
  #will compare two values and return the degrees of success (in positive numberals) or failure (negative numerals).
  #will be used by most other functions here so should be at the top.
  
  #one result when called from within another function
  if arg == "func":
    comp = a-b
    if comp >= 0:
      comp += 1
      return math.ceil(comp/5)
    else:
      return math.floor(comp/5)
  #another result when called from the readargs function
  else:
    if "help" in arg or "h" in arg:
      await channel.send("""**Comparison**
    To compare two numbers, you can use `$c`, `$check`, or `$compare`. Usage is as follows:
        `$c [Number] [DC to compare to]`
        
    This command does not accept any additional arguments.""")
    
    if len(arg) == 3 and arg[1].isnumeric() and arg[2].isnumeric():
      a = int(arg[1])
      b = int(arg[2])
      comp = a-b
      if comp >= 0:
        comp += 1
        comp = math.ceil(comp/5)
        if comp == 1:
          await channel.send(arg[1] + " compared to a DC of " + arg[2] + " for 1 degree of success!")
        else:
          await channel.send(arg[1] + " compared to a DC of " + arg[2] + " for " + str(comp) + " degrees of success!")
      else:
        comp = math.floor(comp/5)
        if comp == -1:
          await channel.send(arg[1] + " compared to a DC of " + arg[2] + " for 1 degree of failure!")
        else:
          await channel.send(arg[1] + " compared to a DC of " + arg[2] + " for " + str(comp * -1) + " degrees of success!")
    else:
      await channel.send("Usage error. Please input 2 numbers to compare.")

async def graded(arg, channel, author):
  #will roll a d20, add the arg if there is one, and compare to a given number, or to 10 if no number is provided. Can roll multiple times. Skill Adept is permitted, as is improved critical and hero points.

  if "help" in arg or "h" in arg:
    await channel.send("""**Graded Check**
    To roll a generic check against a given DC, you can use `$g`, `$graded`, or `$dc`. Usage is as follows:
        `$a (Resistance Bonus) (DC) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no DC is provided, the DC will be assumed to be 10. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
       `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
       `sa` If this argument is included, any roll of 4 or below will be increased to 5, as if this roll was made using the Skill Adept advantage.
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

  #turns the bonus into a string
  if bonus == 0:
    bonusPrint = ""
  else:
    if bonus > 0:
      bonusPrint = "+" + str(bonus)
    else:
      bonusPrint = str(bonus)

  finPrint = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      finPrint += arg[a] + " "
    finPrint += "\n"

  for roll in range(rolls):
    #rolls the number
    result = random.randint(1,20)
    total = result

    #checks if it was a crit
    crit = await dicemod.critCheck(arg, result, True)
    #improves the result if you have skill adept
    if "sa" in arg and result < 5:
      total = 5
      sa = ", increased by Skill Adept to 5"
    else:
      sa = ""
    #improves the result if you spent a hero point
    if "hp" in arg and result < 11:
      hp = ", increased by a hero point to " + str(total + 10)
      total += 10
    else:
      hp = ""

    #gets the total result
    total += bonus

    #checks the number of degrees of success
    degrees = await check("func", total, DC, channel)
    #turns that into a string
    degrees = await dicemod.degrees(degrees, DC, crit)

    finPrint += await dicemod.printResult(result, sa, hp, bonusPrint, total, crit, degrees)

    if roll + 1 != rolls:
      finPrint += "\n"

  if len(finPrint) > 2000:
    await channel.send("Too many characters in return. Please make fewer rolls, " + author)
  else:
    await channel.send(finPrint)

async def other(arg, channel, author):
  if "help" in arg or "h" in arg:
    await channel.send("""**Other Dice**
    To roll dice that are not d20s, you can use `$o` or `$other`. Usage is as follows:
        `$o (number of rolls)d[number of sides]+[bonus]`
    If no number of rolls is provided, a single roll will be made. If no number of sides is provided, an error will result. If no bonus is provided, nothing will be added.
    
    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.""")
    return

  if len(arg) >= 2 and not re.search("^[0-9]*d[0-9]+\+*[0-9]*$", arg[1]) or len(arg) < 2:
    await channel.send("Usage error. Please input a number of dice with a given number of sides in the format #d# or #d#+#.")
    return

  dice = re.split("[\+|d]", arg[1])

  rolls = int(dice[0])
  if rolls < 1:
    rolls = 1
  
  sides = int(dice[1])
  if sides < 1:
    sides = 1
  
  if len(dice) > 2:
    bonus = int(dice[2])
    bonusPrint = "+" + dice[2]
  else:
    bonus = 0
    bonusPrint = ""
  
  finPrint = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      finPrint += arg[a] + " "
    finPrint += "\n"

  acc = 0

  for roll in range(rolls):
    result = random.randint(1,sides)
    total = result + bonus
    acc += total

    finPrint += await dicemod.printResult(result, "", "", bonusPrint, total, "", "") + "\n"

  finPrint += "The final total is **" + str(acc) + "**!"


  if len(finPrint) > 2000:
    await channel.send("Too many characters in return. Please make fewer rolls, " + author)
  else:
    await channel.send(finPrint)

async def roll(arg, channel, author):
  if "help" in arg or "h" in arg:
    await channel.send("""**Roll**
    To make a miscellaneous d20 roll, use `$r` or `$roll`. Usage is as follows:
        `$r (Bonus) (Number of Rolls)`
    If no resistance bonus is provided, nothing will be added to the roll. If no affliction rank is provided, the DC will be assumed to be 0. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
        `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
        `sa` If this argument is included, any roll of 4 or below will be increased to 5, as if this roll was made using the Skill Adept advantage.
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

  finPrint = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      finPrint += arg[a] + " "
    finPrint += "\n"
  
  for roll in range(rolls):
    #rolls the number
    result = random.randint(1,20)
    total = result


    #checks if it was a crit
    crit = await dicemod.critCheck(arg, result, True)
    #improves the result if you have skill adept
    if "sa" in arg and result < 5:
      total = 5
      sa = ", increased by Skill Adept to 5"
    else:
      sa = ""
    #improves the number if you spent a hero point or if this was a defense roll
    if "hp" in arg and result < 11:
      hp = ", increased by a hero point to " + str(total + 10)
      total += 10
    elif "def" in arg and result < 11:
      hp = ", increased to " + str(total + 10)
      total += 10
    else:
      hp = ""
    
    #adds the bonus
    total += bonus

    finPrint += await dicemod.printResult(result, sa, hp, bonusPrint, total, crit, "")

    if roll + 1 != rolls:
      finPrint += "\n"

  if len(finPrint) > 2000:
    await channel.send("Too many characters in return. Please make fewer rolls, " + author)
  else:
    await channel.send(finPrint)

async def tough(arg, channel, author):
  #will roll a d20, add the arg if there is one, and compare to a given number, or to 10 if no number is provided. Can roll multiple times. Skill Adept is permitted, as is improved critical and hero points.

  if "help" in arg or "h" in arg:
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

  #sets the value of the bonus and DC if args are provided
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

  finPrint = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      finPrint += arg[a] + " "
    finPrint += "\n"

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

    finPrint += await dicemod.printResult(result, "", hp, bonusPrint, total, crit, degreesPrint)

    if degrees >= 0:
      finPrint += " You take no penalty!"
    elif degrees == -1:
      finPrint += " That's a **Bruise!**"
    elif degrees == -2:
      finPrint += " That's a **Bruise** and you are **Dazed** until the end of your next turn!"
    elif degrees == -3:
      finPrint += " That's a **Bruise** and you are **Staggered!**"
    else:
      finPrint += " You are **Incapacitated!**"

    if roll + 1 != rolls:
      finPrint += "\n"

  if len(finPrint) > 2000:
    await channel.send("Too many characters in return. Please make fewer rolls, " + author)
  else:
    await channel.send(finPrint)

async def weak(arg, channel, author):
  if len(arg) > 1 and arg[1] == "help" or len(arg) > 1 and arg[1] == "h":
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
        DC = int(arg[2])
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

  finPrint = author + "\n"

  if "%" in arg:
    for a in range(arg.index("%") + 1, len(arg)):
      finPrint += arg[a] + " "
    finPrint += "\n"

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

    finPrint += await dicemod.printResult(result, "", hp, bonusPrint, total, "", "") + "With a DC of " + str(DC) + ","

    if pointsLost > 0:
      finPrint += " you lose **" + str(pointsLost) + " PP** from the affected trait or traits!"
    else:
      finPrint += " you take no penalty!"

    if roll + 1 != rolls:
      finPrint += "\n"

  if len(finPrint) > 2000:
    await channel.send("Too many characters in return. Please make fewer rolls, " + author)
  else:
    await channel.send(finPrint)
 

async def readArgs(arg, channel, author):
  #should be a series of ifs that ends with an else for a command it doesn't recognize
  for a in range(1,len(arg)):
    if not re.search("[a-z]|[A-Z]|%", arg[a]):
      arg[a] = str(eval(arg[a]))
    else:
      break

  if arg[0] == "$help":
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
    Additional details on all of these commands can be seen by using the command with the `h` or `help` arguments. Commands may also respond to the following arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
        `hp` If this argument is included, any roll of 10 or below will have 10 added to it, as if this roll was rerolled using a hero point. This will not trigger a critical success if it occurs.
        `sa` If this argument is included, any roll of 4 or below will be increased to 5, as if this roll was made using the Skill Adept advantage.
        `imp1` `imp2` `imp3` `imp4` If any of these arguments are included, rolls will be counted as critical successes on numbers below 20, as if this roll was made using a number of ranks of Improved Critical.""")
  elif arg[0] == "$a" or arg[0] == "$aff" or arg[0] == "$affliction":
    if "help" in arg or "h" in arg:
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
      while "sa" in arg:
        arg.remove("sa")
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
        arg[2] = str( int(arg[2]) + 10)

      #calls graded
      await graded(arg, channel, author)
  elif arg[0] == "$c" or arg[0] == "$compare" or arg[0] == "$check":
    await check(arg, 0, 0, channel)
  elif arg[0] == "$d" or arg[0] == "$def" or arg[0] == "$defense":
    if "help" in arg or "h" in arg:
      await channel.send("""**Defense**
    To roll a defense check using Deflect or the Defend action, you can use `$d`, `$def`, or `$defend`. Usage is as follows:
        `$d (Defense) (Number of Rolls)`
    If no defense bonus is provided, nothing will be added to the roll. If no number of rolls is provided, a single roll will be made.

    This command accepts the following additional arguments:
        `%` If this argument is included, all arguments following it will be printed prior to rolls being made, allowing you to label your rolls.
    
    This is an alias for the *Roll* Command (`$r` `$roll`)""")
    else:
      while "sa" in arg:
        arg.remove("sa")
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
  elif arg[0] == "$g" or arg[0] == "$graded" or arg[0] == "$dc":
    await graded(arg, channel, author)
  elif arg[0] == "$o" or arg[0] == "$other":
    await other(arg, channel, author)
  elif arg[0] == "$r" or arg[0] == "$roll":
    await roll(arg, channel, author)
  elif arg[0] == "$t" or arg[0] == "$tough" or arg[0] == "$toughness":
    await tough(arg, channel, author)
  elif arg[0] == "$w" or arg[0] == "$weak" or arg[0] == "$weaken":
    await weak(arg, channel, author)
  else:
    await channel.send("`I don't recognize that command.`")