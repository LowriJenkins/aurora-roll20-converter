r"""
Strip leading byte-order-mark from utf-8 files.
"""


def bomstrip(string):
    """
     Function to delete UTF-8 BOM character in "string"
    """
    if string[:3] != "<?x":
        return string[3:]
    else:
        return string


def attribute(name, current="", max=""):
    return {"name": name, "current": current, "max": max, "id": ""}


hitdice = {"Sorcerer": "6", "Wizard": "6", "Artificer": "8", "Bard": "8", "Cleric": "8", "Druid": "8", "Monk": "8",
           "Rogue": "8", "Warlock": "8", "Fighter": "10", "Paladin": "10", "Ranger": "10", "Barbarian": "12"}
