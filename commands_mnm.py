#imports for basic bot functionality
from discord import app_commands, Interaction
from discord.ext import commands

#imports for basic dicebot functionality
import random

from utilities_text import pluralize
import dicemod

random.seed()

# Helper functions

def build_arg_flags(hero_point=False, improved_critical=0, minion=False, defense=False):
    """Build a synthetic arg list for dicemod.critCheck() compatibility."""
    flags = ["$slash"]  # placeholder command name so flags aren't at index 0
    if hero_point:
        flags.append("hp")
    if improved_critical >= 1:
        flags.append(f"imp{min(improved_critical, 4)}")
    if minion:
        flags.append("min")
    if defense:
        flags.append("def")
    return flags

def _bonus_str(bonus):
    """Format a bonus as +X, -X, or empty string."""
    if bonus > 0:
        return f"+{bonus}"
    elif bonus < 0:
        return str(bonus)
    return ""

async def _send_long(interaction, text):
    """Send a message, splitting into lines if it exceeds Discord's 2000 char limit."""
    if len(text) > 2000:
        lines = text.splitlines()
        first = True
        for line in lines:
            if line.strip():
                if first:
                    await interaction.response.send_message(line)
                    first = False
                else:
                    await interaction.followup.send(line)
    else:
        await interaction.response.send_message(text)

class MnM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Compare ---
    @app_commands.command(
        name="compare",
        description="Compare two numbers and report degrees of success or failure."
    )
    @app_commands.describe(
        number="The number to compare (e.g., a total roll result)",
        dc="The DC to compare against"
    )
    async def compare(self, interaction: Interaction, number: int, dc: int):
        degrees = dicemod.calc_degrees(number, dc)
        abs_deg = abs(degrees)
        word = "success" if degrees > 0 else "failure"
        await interaction.response.send_message(
            f"{number} compared to a DC of {dc} is "
            f"{abs_deg} {pluralize(abs_deg, 'degree')} of {word}!"
        )

    # --- Graded Check ---
    @app_commands.command(
        name="graded",
        description="Roll a d20 against a DC with degrees of success/failure."
    )
    @app_commands.describe(
        bonus="Bonus to add to the d20 roll",
        dc="The DC to roll against (default 10)",
        rolls="Number of rolls to make (default 1)",
        hero_point="Reroll results of 10 or below by adding 10",
        label="A label to print before the rolls"
    )
    async def graded(self, interaction: Interaction, bonus: int = 0, dc: int = 10, rolls: int = 1,
                     hero_point: bool = False, label: str = ""):
        await self._do_graded(interaction, bonus, dc, max(1, rolls), hero_point, label)

    async def _do_graded(self, interaction, bonus, dc, rolls, hero_point, label):
        """Shared graded check logic used by /graded and /affliction."""
        arg_flags = build_arg_flags(hero_point=hero_point)
        bonus_print = _bonus_str(bonus)
        print_string = f"{label}\n"

        for i in range(rolls):
            result = random.randint(1, 20)
            total = result

            crit = dicemod.crit_check(arg_flags, result, True)

            if hero_point and result < 11:
                hp = f", increased by a hero point to {total + 10}"
                total += 10
            else:
                hp = ""

            total += bonus

            deg = dicemod.calc_degrees(total, dc)
            deg_str = dicemod.degrees(deg, dc, crit)

            print_string += dicemod.print_result(result, hp, bonus_print, total, crit, deg_str)

            if i + 1 < rolls:
                print_string += "\n"

        await _send_long(interaction, print_string.strip())

    # --- Affliction ---
    @app_commands.command(
        name="affliction",
        description="Roll a resistance check against an Affliction."
    )
    @app_commands.describe(
        bonus="Resistance bonus to add to the d20 roll",
        rank="The Affliction rank (DC = rank + 10)",
        rolls="Number of rolls to make (default 1)",
        hero_point="Reroll results of 10 or below by adding 10",
        label="A label to print before the rolls"
    )
    async def affliction(self, interaction: Interaction, bonus: int = 0, rank: int = 0, rolls: int = 1,
                         hero_point: bool = False, label: str = ""):
        dc = rank + 10
        await self._do_graded(interaction, bonus, dc, max(1, rolls), hero_point, label)

    # --- Roll ---
    @app_commands.command(
        name="roll",
        description="Roll a d20 with a bonus (no DC comparison)."
    )
    @app_commands.describe(
        bonus="Bonus to add to the d20 roll",
        rolls="Number of rolls to make (default 1)",
        hero_point="Reroll results of 10 or below by adding 10",
        improved_critical="Ranks of Improved Critical (0-4)",
        label="A label to print before the rolls"
    )
    async def roll(self, interaction: Interaction, bonus: int = 0, rolls: int = 1,
                   hero_point: bool = False, improved_critical: int = 0,
                   label: str = ""):
        arg_flags = build_arg_flags(hero_point=hero_point, improved_critical=improved_critical)
        bonus_print = _bonus_str(bonus)
        print_string = f"{label}\n"

        for i in range(max(1, rolls)):
            result = random.randint(1, 20)
            total = result

            crit = dicemod.crit_check(arg_flags, result, True)

            if hero_point and result < 11:
                total += 10
                hp = f", increased by a hero point to {total}"
            else:
                hp = ""

            total += bonus

            print_string += dicemod.print_result(result, hp, bonus_print, total, crit, "")

            if i + 1 < rolls:
                print_string += "\n"

        await _send_long(interaction, print_string.strip())

    # --- Defense ---
    @app_commands.command(
        name="defense",
        description="Roll a Defend/Deflect check (results below 11 are raised to 11)."
    )
    @app_commands.describe(
        bonus="Defense bonus to add to the d20 roll",
        rolls="Number of rolls to make (default 1)",
        label="A label to print before the rolls"
    )
    async def defense(self, interaction: Interaction, bonus: int = 0, rolls: int = 1, label: str = ""):
        arg_flags = build_arg_flags(defense=True)
        bonus_print = _bonus_str(bonus)
        print_string = f"{label}\n"

        for i in range(max(1, rolls)):
            result = random.randint(1, 20)
            total = result
            hp = ""

            if result < 11:
                total += 10
                hp = f", increased as a Defend to {total}"

            total += bonus

            crit = dicemod.crit_check(arg_flags, result, True)

            print_string += dicemod.print_result(result, hp, bonus_print, total, crit, "")

            if i + 1 < rolls:
                print_string += "\n"

        await _send_long(interaction, print_string.strip())

    # --- Toughness ---
    @app_commands.command(
        name="toughness",
        description="Roll a Toughness save against Damage."
    )
    @app_commands.describe(
        bonus="Toughness bonus to add to the d20 roll",
        damage_rank="The Damage rank (DC = 15 + rank)",
        rolls="Number of rolls to make (default 1)",
        hero_point="Reroll results of 10 or below by adding 10",
        label="A label to print before the rolls"
    )
    async def toughness(self, interaction: Interaction, bonus: int = 0, damage_rank: int = 0,
                        rolls: int = 1, hero_point: bool = False, label: str = ""):
        dc = 15 + damage_rank
        arg_flags = build_arg_flags(hero_point=hero_point)
        bonus_print = _bonus_str(bonus)
        print_string = f"{label}\n"

        for i in range(max(1, rolls)):
            result = random.randint(1, 20)
            total = result

            crit = dicemod.crit_check(arg_flags, result, False)

            if hero_point and result < 11:
                total += 10
                hp = f", increased by a hero point to {total}"
            else:
                hp = ""

            total += bonus

            deg = dicemod.calc_degrees(total, dc)
            deg_str = dicemod.degrees(deg, dc, crit)

            # Adjust degrees for crit (matching IB.tough behavior)
            if crit != "":
                deg += 1

            print_string += dicemod.print_result(result, hp, bonus_print, total, crit, deg_str)

            if deg >= 0:
                print_string += " You take no penalty!"
            elif deg == -1:
                print_string += " That's a **Bruise!**"
            elif deg == -2:
                print_string += " That's a **Bruise** and you are **Dazed** until the end of your next turn!"
            elif deg == -3:
                print_string += " That's a **Bruise** and you are **Staggered!**"
            else:
                print_string += " You are **Incapacitated!**"

            if i + 1 < rolls:
                print_string += "\n"

        await _send_long(interaction, print_string.strip())

    # --- Weaken ---
    @app_commands.command(
        name="weaken",
        description="Roll a resistance check against a Weaken effect."
    )
    @app_commands.describe(
        bonus="Resistance bonus to add to the d20 roll",
        weaken_rank="The Weaken rank (DC = 10 + rank)",
        rolls="Number of rolls to make (default 1)",
        hero_point="Reroll results of 10 or below by adding 10",
        label="A label to print before the rolls"
    )
    async def weaken(self, interaction: Interaction, bonus: int = 0, weaken_rank: int = 0,
                     rolls: int = 1, hero_point: bool = False, label: str = ""):
        dc = 10 + weaken_rank
        bonus_print = _bonus_str(bonus)
        print_string = f"{label}\n"

        for i in range(max(1, rolls)):
            result = random.randint(1, 20)
            total = result

            if hero_point and result < 11:
                total += 10
                hp = f", increased by a hero point to {total}"
            else:
                hp = ""

            total += bonus

            points_lost = dc - total

            print_string += dicemod.print_result(result, hp, bonus_print, total, "", "")
            print_string += f"With a DC of {dc},"

            if points_lost > 0:
                print_string += f" you lose **{points_lost} PP** from the affected trait or traits!"
            else:
                print_string += " you take no penalty!"

            if i + 1 < rolls:
                print_string += "\n"

        await _send_long(interaction, print_string.strip())

# The setup function is required to load the cog
async def setup(bot):
    await bot.add_cog(MnM(bot))
