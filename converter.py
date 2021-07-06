import json
import os
import re
from copy import deepcopy

from bs4 import BeautifulSoup

import misc_functions
from get_aurora_files import AuroraReader as AR


def get_abillity_scores(char_race, bs_data, reader):
    ability_score = {"strength": 0, "dexterity": 0, "wisdom": 0, "constitution": 0, "intelligence": 0, "charisma": 0}
    ability_mod = {"strength": 0, "dexterity": 0, "wisdom": 0, "constitution": 0, "intelligence": 0, "charisma": 0}
    abilities = char_race[0].find_all('element', {"type": "Ability Score Improvement"})
    for ability in ability_score:
        base = int(bs_data.find(ability).text)
        ability_score[ability] = base
        ability_mod[ability] = int((ability_score[ability] - 10) / 2)
    if len(abilities) > 0:
        for ability in abilities:
            stat_increase = (reader.full_data_find({"id": ability["registered"]}).find("stat"))
            ability_score[stat_increase["name"]] += int(stat_increase["value"])
            ability_mod[stat_increase["name"]] = int((ability_score[stat_increase["name"]] - 10) / 2)
    else:
        increase = reader.full_data_find({"id": char_race[1]['id']}).find_all("stat")
        increase = [stat for stat in increase if stat["name"] in ability_score]
        for stat in increase:
            ability_score[stat["name"]] += int(stat["value"])
            ability_mod[stat["name"]] = int((ability_score[stat["name"]] - 10) / 2)
    return ability_score, ability_mod


def read_data(filename):
    with open(filename, 'r') as f:
        data = f.read()
    data = misc_functions.bomstrip(data)
    # Passing the stored data inside the beautifulsoup parser
    bs_data = BeautifulSoup(data, 'xml')
    json_data = json.load(open('character sheet.json', 'r'))
    character_sheet = json_data["character"]
    reader = AR()
    return bs_data, json_data, character_sheet, reader


def get_skills(ability_mod, bs_data):
    skill_proficiencies = bs_data.find_all("element",
                                           {"type": "Proficiency", "id": re.compile('ID_PROFICIENCY_SKILL_.*')})
    skill_proficiencies = [proficiency["id"].replace("ID_PROFICIENCY_SKILL_", "").lower() for proficiency in
                           skill_proficiencies]
    skill_proficiencies = set(skill_proficiencies)
    skills = {"athletics": ability_mod["strength"], "acrobatics": ability_mod["dexterity"],
              "sleight_of_hand": ability_mod["dexterity"], "stealth": ability_mod["dexterity"],
              "arcana": ability_mod["intelligence"], "history": ability_mod["intelligence"],
              "investigation": ability_mod["intelligence"], "nature": ability_mod["intelligence"],
              "religion": ability_mod["intelligence"], "animal_handling": ability_mod["wisdom"],
              "insight": ability_mod["wisdom"], "medicine": ability_mod["wisdom"],
              "perception": ability_mod["wisdom"], "survival": ability_mod["wisdom"],
              "deception": ability_mod["charisma"], "intimidation": ability_mod["charisma"],
              "performance": ability_mod["charisma"], "persuasion": ability_mod["charisma"]}
    return skill_proficiencies, skills


def get_saves(ability_mod, bs_data, prof_bonus):
    save_proficiencies = bs_data.find_all("element",
                                          {"type": "Proficiency", "id": re.compile('ID_PROFICIENCY_SAVINGTHROW_.*')})
    save_proficiencies = [proficiency["id"].replace("ID_PROFICIENCY_SAVINGTHROW_", "").lower() for proficiency in
                          save_proficiencies]
    save_proficiencies = set(save_proficiencies)
    saves = deepcopy(ability_mod)
    for save in save_proficiencies:
        saves[save] += prof_bonus
    return save_proficiencies, saves


def add_traits(character_sheet, trait, type, source):
    if not trait.find("sheet", {"display": "false"}):
        display = trait.find("sheet").find("description").get_text()
        display = display.replace("\t", "")
        trait_name = trait["name"]
        character_sheet["attribs"].append(
            misc_functions.attribute("repeating_traits_{}_source".format(trait_name), source, ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("repeating_traits_{}_source_type".format(trait_name), type, ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("repeating_traits_{}_name".format(trait_name), trait_name, ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("repeating_traits_{}_description".format(trait_name), display))


def get_prof_bonus(char_level):
    prof_bonus = 2
    if char_level > 16:
        prof_bonus = 6
    elif char_level > 12:
        prof_bonus = 5
    elif char_level > 8:
        prof_bonus = 4
    elif char_level > 4:
        prof_bonus = 3
    return prof_bonus


def find_matching_traits(trait_list, reader, traits_search):
    for trait in traits_search:
        trait_list.append(reader.full_data_find({"id": trait}))


def set_traits(data, character_sheet, racial_traits, source):
    for trait in racial_traits:
        add_traits(character_sheet, trait, data, source)


def set_saves(character_sheet, saves, saves_proficiencies):
    for save in saves:
        character_sheet["attribs"].append(misc_functions.attribute("{}_save_bonus".format(save), saves[save], ""))
    for save in saves_proficiencies:
        character_sheet["attribs"].append(misc_functions.attribute("{}_save_prof".format(save), "(@{pb})", ""))


def set_skills(character_sheet, prof_bonus, skill_proficiencies, skills):
    for skill in skills:
        if skill in skill_proficiencies:
            character_sheet["attribs"].append(
                misc_functions.attribute("{}_prof".format(skill), "(@{{pb}}*@{{{}_type}})".format(skill), ""))
            skills[skill] += prof_bonus
        character_sheet["attribs"].append(misc_functions.attribute("{}_bonus".format(skill), skills[skill], ""))


def set_abillity_scores(ability_mod, ability_score, character_sheet):
    for ability in ability_score:
        character_sheet["attribs"].append(
            misc_functions.attribute("{}_base".format(ability), str(ability_score[ability]), ""))
        character_sheet["attribs"].append(misc_functions.attribute(ability, ability_score[ability], ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("{}_mod".format(ability), ability_mod[ability], ""))


def set_casting(ability_mod, character_sheet, prof_bonus, spell_casting):
    if spell_casting:
        spell_attack_bonus = prof_bonus + ability_mod[spell_casting]
        character_sheet["attribs"].append(
            misc_functions.attribute("spellcasting_ability", "@{{{}_mod}}+".format(spell_casting), ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("spell_save_dc", 8 + spell_attack_bonus, ""))
        character_sheet["attribs"].append(
            misc_functions.attribute("spell_attack_bonus", spell_attack_bonus, ""))


def set_personality(character_sheet, personality_traits):
    character_sheet["attribs"].append(
        misc_functions.attribute("personality_traits", "\n".join(personality_traits[0:2]), ""))
    character_sheet["attribs"].append(misc_functions.attribute("ideals", personality_traits[2], ""))
    character_sheet["attribs"].append(misc_functions.attribute("bonds", personality_traits[3], ""))
    character_sheet["attribs"].append(misc_functions.attribute("flaws", personality_traits[4], ""))


def set_char_appearence(char_appearance, character_sheet):
    character_sheet["attribs"].append(misc_functions.attribute("age", char_appearance.find("age").text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("height", char_appearance.find("height").text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("weight", char_appearance.find("weight").text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("eyes", char_appearance.find("eyes").text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("skin", char_appearance.find("skin").text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("hair", char_appearance.find("hair").text, ""))


def convert(filename):
    bs_data, json_data, character_sheet, reader = read_data(filename)

    name = bs_data.find('name')
    char_race = bs_data.find('race')
    char_class = bs_data.find('class')
    char_level = int(bs_data.find('level').text)
    prof_bonus = get_prof_bonus(char_level)
    char_appearance = bs_data.find("appearance")
    char_race_search = bs_data.find_all('element', {"type": "Race"})
    char_class_search = bs_data.find_all('element', {"type": "Class"})
    char_size = bs_data.find('element', {"type": "Size"})

    personality_traits = [trait.text for trait in bs_data.find_all("element", {"type": "List", "name": re.compile(
        "(Personality Trait)|(Ideal)|(Bond)|(Flaw)")})]
    ability_score, ability_mod = get_abillity_scores(char_race_search, bs_data, reader)
    skill_proficiencies, skills = get_skills(ability_mod, bs_data)

    saves_proficiencies, saves = get_saves(ability_mod, bs_data, prof_bonus)

    traits_search = char_race_search[0].find_all('element', {"type": "Racial Trait",
                                                             "registered": re.compile('.*_RACIAL_TRAIT_.*')})
    if len(traits_search) == 0:
        traits_search = char_race_search[0].find_all('element', {"type": "Racial Trait",
                                                                 "id": re.compile('.*_RACIAL_TRAIT_.*')})
        traits_search = [trait["id"] for trait in traits_search]
    else:
        traits_search = [trait["registered"] for trait in traits_search]

    racial_traits = []
    find_matching_traits(racial_traits, reader, traits_search)
    traits_search = char_class_search[0].find_all('element',
                                                  {"type": "Class Feature", "id": re.compile('.*_CLASS_FEATURE_.*')})
    traits_search = [trait["id"] for trait in traits_search]
    spell_casting = None
    class_traits = []
    for trait in traits_search:
        feature = reader.full_data_find({"id": trait})
        if feature["name"] == "Spellcasting":
            spell_casting = feature.find("spellcasting")["ability"].lower()
        class_traits.append(feature)

    traits_search = bs_data.find_all('element', {"type": "Feat", "id": re.compile('.*_FEAT_.*')})
    traits_search = [trait["id"] for trait in traits_search]
    feats = []
    find_matching_traits(feats, reader, traits_search)
    archetype = char_class_search[0].find("element", {"type": "Archetype"})

    archetype_traits = []
    if archetype is not None:
        traits_search = archetype.find_all('element',
                                           {"type": "Archetype Feature", "id": re.compile('.*_ARCHETYPE_.*')})
        traits_search = [trait["id"] for trait in traits_search]
        find_matching_traits(archetype_traits, reader, traits_search)
        archetype = reader.full_data_find({"id": archetype["registered"]})["name"]

    character_sheet["name"] = name.text
    character_sheet["attribs"][0]["current"] = misc_functions.hitdice[char_class.text]
    character_sheet["attribs"].append(misc_functions.attribute("class", char_class.text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("options-class-selection", "on", ""))
    character_sheet["attribs"].append(misc_functions.attribute("hitdie_final", "@{hitdietype}", ""))
    character_sheet["attribs"].append(
        misc_functions.attribute("hitdietype", misc_functions.hitdice[char_class.text], ""))
    character_sheet["attribs"].append(misc_functions.attribute("level", char_level, ""))
    character_sheet["attribs"].append(misc_functions.attribute("base_level", char_level, ""))
    character_sheet["attribs"].append(misc_functions.attribute("pb", prof_bonus, ""))
    character_sheet["attribs"].append(misc_functions.attribute("race", char_race.text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("race_display", char_race.text, ""))
    character_sheet["attribs"].append(misc_functions.attribute("size", char_size["name"], ""))
    character_sheet["attribs"].append(misc_functions.attribute("subclass", archetype, ""))
    character_sheet["attribs"].append(
        misc_functions.attribute("class_display", "{} {} {}".format(archetype, char_class.text, char_level), ""))
    set_char_appearence(char_appearance, character_sheet)
    set_personality(character_sheet, personality_traits)

    character_sheet["attribs"].append(misc_functions.attribute("ac", ability_mod["dexterity"] + 10, ""))
    set_casting(ability_mod, character_sheet, prof_bonus, spell_casting)

    set_abillity_scores(ability_mod, ability_score, character_sheet)
    set_skills(character_sheet, prof_bonus, skill_proficiencies, skills)

    set_saves(character_sheet, saves, saves_proficiencies)

    set_traits(char_race.text, character_sheet, racial_traits, "Race")
    set_traits(char_class.text, character_sheet, class_traits, "Class")
    set_traits(archetype, character_sheet, archetype_traits, "Class")
    set_traits("Feat", character_sheet, feats, "Feat")

    print(character_sheet["attribs"])
    with open(os.path.join("output", '{}.json'.format(name.text)), 'w') as f:
        json.dump(json_data, f)


def main():
    for folder, subs, files in os.walk(os.path.abspath(os.path.join(os.curdir, "input"))):
        files = [fi for fi in files if fi.endswith(".dnd5e")]
        for filename in files:
            convert(os.path.join(folder, filename))


main()
