import math

def crit_check(arg, result, improved):
    """Closes immediately if this is a roll being made by minions."""
    if "min" in arg or "minion" in arg or "m" in arg:
        return ""

    # Sets the critical value
    crit_val = 20
    if improved:
        if "imp4" in arg:
            crit_val = 16
        elif "imp3" in arg:
            crit_val = 17
        elif "imp2" in arg:
            crit_val = 18
        elif "imp1" in arg:
            crit_val = 19

    if result >= crit_val:
        return "**, which is a **crit"
    else:
        return ""

def degrees(deg, DC, crit):
    """Takes in the degrees of success, the DC, and if the roll was a crit, and returns a verbose string summarizing it."""
    if crit != "":
        deg += 1
    abs_deg = abs(deg)
    word = "success" if deg >= 0 else "failure"
    if abs_deg == 1:
        return f"Against a DC of {DC}, that's 1 degree of {word}!"
    else:
        return f"Against a DC of {DC}, that's {abs_deg} degrees of {word}!"

def print_result(result, hp, bonus, total, crit, degrees):
    """Takes in the various aspects of the roll, and returns a verbose string summarizing the result."""
    crit5 = ""
    if crit != "":
        crit5 = f"That's an effective **{total + 5}!** "

    if result == total:
        return f"Rolled a **{result}{crit}!** {crit5}{degrees}"
    else:
        return f"Rolled a {result}{hp}{bonus}, for a total of **{total}{crit}**! {crit5}{degrees}"

def calc_degrees(total, DC):
    """Calculate degrees of success (positive) or failure (negative) from a total and DC."""
    comp = total - DC
    if comp >= 0:
        comp += 1
        return math.ceil(comp / 5)
    else:
        return math.floor(comp / 5)
