import os

#may need to change this path depending on your system
install_prefix = r"C:\Program Files (x86)\Steam\steamapps\common\Grim Dawn"

non_mod_dbr = install_prefix + r"\database"
non_mod_comps = non_mod_dbr + r"\records\items\materia\compb_"
non_mod_tags_items = install_prefix + r"\resources\text_en\tags_items.txt"
gdx1_tags_items = install_prefix + r"\resources\text_en\tagsgdx1_items.txt"

#hardcoded tags
desc = "tagReskillCompDesc=\"Siphoned arcane power of an item into a component.\"^w^n(Used in Jewelry, Weapons, Head, and Hand armor)"
craft_desc = "tagReskillCraftCompDesc=^wSiphon arcane power from an item into a component."

mod = install_prefix + r"\mods\Reskill"
mod_text = mod + r"\source\text_en\tags_reskill_items.txt"
mod_tex = "reskill/skill_"
bp = mod + r"\database\reskill\blueprints"
comp = mod + r"\database\reskill\components"
#template blueprint/component files contained within mod itself
dummy_bp = r"blueprints\dummy.dbr"
dummy_comp = r"components\dummy.dbr"
#the smith we use in-game
smith_table = mod + r"\database\reskill\creatures\reskillsmith_smith.dbr" #add entries to defaultRecipes,,

#edit this to change when the components can be equipped on a character.
levelReq = 85

#set this to True to make the components require the level of the item the skill is from.
iLevel = False

targets = []
items = []
items_data = {}
tags_items = {}

mod_tags = []
smith = []

#sums up % modifier values of damage types/their DoT versions, returns the damage type with the highest value
def process_damage(item):
    with open(item) as f:
        pref = {
                "physical": 0,
                "bleeding": 0,
                "pierce": 0,
                "fire": 0,
                "cold": 0,
                "chaos": 0,
                "lightning": 0,
                "poison": 0,
                "aether": 0,
                "vitality": 0,
                "elemental": 0
                }
        component = {
                     "physical": "oleronblood.dbr",
                     "bleeding": "bloodywhetstone.dbr",
                     "pierce": "silvercorebolts.dbr",
                     "fire": "deviltouchedammo.dbr",
                     "cold": "arcanespark.dbr",
                     "chaos": "symbolofsolael.dbr",
                     "lightning": "lodestone.dbr",
                     "poison": "markofdreeg.dbr",
                     "aether": "spellwoventhreads.dbr",
                     "vitality": "hauntedsteel.dbr",
                     "elemental": "arcanelens.dbr"
                     }
        bad = [
               ",,",
               ",0.000000",
               "Crit",
               "TotalDamage",
               "Duration",
               "Stun",
               "Defensive"
               ]
        for line in f:
            if "conversionOutType" in line and ",," not in line:
                if "Life" in line:
                    return "vitality", non_mod_comps + component["vitality"]
                else:
                    dmg = line.split(",")[1].lower()
                    return dmg, non_mod_comps + component[dmg]
            else:
                if "offensive" in line and "Modifier" in line and not any(shit in line for shit in bad):
                    tmp = line.lower().replace("slow","")
                    if "life" in tmp:
                        pref["vitality"] += int(line.split(",")[1].split(".")[0])
                    else:
                        pref[tmp.split("offensive")[1].split("modifier")[0]] += int(tmp.split(",")[1].split(".")[0])
                        
        if pref["pierce"] != 0:
            pref["physical"] = 0 #favor pierce over physical if it exists on an item
        maximum = max(pref, key=pref.get)
        if pref[maximum] == 0:
            return "physical", non_mod_comps + component["physical"] #if all things are equal, default to physical/oleron's blood
        return maximum, non_mod_comps + component[maximum]

#assembles a dictionary pertaining to a particular item
def process_item(item):
    with open(item) as f:
        want = False
        for line in f:
            if "itemSkillName" in line and ",," not in line:
                want = True
                break
        if want:
            itemSkill = ""
            itemSkillLevel = ""
            itemSkillController = ""
            itemName = ""
            itemLevel = ""
            cmp = False #wanted to use 'complex' but evidently that's a python keyword
            f.seek(0)
            for line in f:
                if "itemSkillName" in line:
                    itemSkill = line.split(",")[1]
                elif "itemSkillLevelEq" in line:
                    raw = line.split(",")[1]
                    if "itemLevel" in raw:
                        cmp = True
                    itemSkillLevel = raw
                elif "itemSkillAutoController" in line and ",," not in line:
                    itemSkillController = line.split(",")[1]
                elif "itemNameTag" in line and ",," not in line:
                    itemName = tags_items.get(line.split(",")[1])
                elif "itemLevel" in line and ",," not in line:
                    itemLevel = line.split(",")[1]
            if cmp:
                itemSkillLevel = itemSkillLevel.replace("itemLevel", itemLevel)
                add = int(itemSkillLevel.split("+")[1])
                div = int(itemSkillLevel.split("/")[1].split("+")[0])
                num = int(itemSkillLevel.split("/")[0])
                itemSkillLevel = str(int(add + (num/div)))
            if itemName in items_data and int(items_data[itemName]["itemLevel"]) < int(itemLevel):
                del items_data[itemName]
            elif itemName in items_data and int(items_data[itemName]["itemLevel"]) > int(itemLevel):
                return
            damage = process_damage(item)
            items_data[itemName] = {
                "itemSkill": itemSkill,
                "itemSkillLevel": itemSkillLevel,
                "itemSkillController": itemSkillController,
                "itemLevel": itemLevel,
                "file": item,
                "icon": mod_tex + damage[0] + ".tex",
                "name": itemName,
                "component": damage[1]
            }

def main():
    #get vanilla tags for items
    for line in open(non_mod_tags_items):
        if "=" in line:
            tags_items.update({line.split("=")[0]:line.split("=")[1].replace("\n", "")})
    #get gdx1 tags for items        
    for line in open(gdx1_tags_items):
        if "=" in line:
            tags_items.update({line.split("=")[0]:line.split("=")[1].replace("\n", "")})
            
    #fetch all items listed in given directory file
    for line in open("dir.txt"):
        #mod items:
        if line[:1] == '+':
            targets.append(install_prefix + line[1:].rstrip().replace("/", "\\"))
        #mod tags, overwriting default tags as appropriate:
        elif line[:1] == '*':
            for line in open(install_prefix + line[1:].rstrip().replace("/", "\\")):
                if "=" in line:
                 tags_items.update({line.split("=")[0]:line.split("=")[1].replace("\n", "")})
        elif line[:1] == "#":
            continue
        targets.append(non_mod_dbr + "\\" + line.rstrip().replace("/", "\\"))
        
    for target in targets:
        for item in os.listdir(target):
            items.append(target + item)
    
    for item in items:
        process_item(item)
        
    cnt = 1
    #generate mod tags
    for item in items_data:
        mod_tags.append("tagReskillComp" + str(cnt) + "=Skill Rune of " + item)
        items_data[item]["tag"] = "tagReskillComp" + str(cnt)
        cnt+=1    
    with open(mod_text, 'w') as out:
        for line in mod_tags:
            out.write(line + "\n")
        out.write(desc + "\n")
        out.write(craft_desc + "\n")
        out.write("\n")
        out.close()
        
    #generate mod components, blueprints, and fill the smith's crafting table
    dict_comp = {}
    dict_bp = {}
    dict_smith = {}

    for line in open(dummy_bp):
        spl = line.split(",")
        dict_bp[spl[0]] = spl[1]
    for line in open(dummy_comp):
        spl = line.split(",")
        dict_comp[spl[0]] = spl[1]
    for line in open(smith_table):
        spl = line.split(",")
        dict_smith[spl[0]] = spl[1]
    
    bpl = []

    for item in items_data:
        dat = items_data[item]
        dict_comp["FileDescription"] = dat["name"].replace(",", "")
        dict_comp["shardBitmap"] = dat["icon"]
        dict_comp["relicBitmap"] = dat["icon"]
        dict_comp["itemText"] = "tagReskillCompDesc"
        dict_comp["description"] = dat["tag"]
        dict_comp["itemSkillName"] = dat["itemSkill"]
        dict_comp["itemSkillLevelEq"] = dat["itemSkillLevel"]
        dict_comp["itemSkillAutoController"] = dat["itemSkillController"]
        if iLevel:
            dict_comp["levelRequirement"] = dat["itemLevel"]
        else:
            dict_comp["levelRequirement"] = levelReq
        nm = r"\reskill_" + dat["name"].lower().replace(",","").replace(" ","").replace("'","") + ".dbr"
        with open(comp + nm, "w") as out:
            for entry in dict_comp:
                out.write(entry + "," + str(dict_comp[entry]) + ",\n")
            out.close()
        dict_bp["FileDescription"] = dat["name"].replace(",", "")
        dict_bp["artifactName"] = "reskill/components" + nm.replace("\\", "/")
        dict_bp["itemText"] = dat["tag"]
        dict_bp["reagentBaseBaseName"] = dat["file"].replace(non_mod_dbr + "\\", "").replace("\\","/")
        dict_bp["reagentBaseQuantity"] = "1"
        dict_bp["reagent1BaseName"] = dat["component"].replace(non_mod_dbr + "\\", "").replace("\\","/")
        dict_bp["reagent1Quantity"] = "1"
        dict_bp["reagent2BaseName"] = dat["component"].replace(non_mod_dbr + "\\", "").replace("\\","/")
        dict_bp["reagent2Quantity"] = "1"
        with open(bp + nm, "w") as out:
            for entry in dict_bp:
                out.write(entry + "," + dict_bp[entry] + ",\n")
            out.close()
        bpl.append("reskill/blueprints" + nm.replace("\\", "/"))
        
    with open(smith_table, "w") as out:
        dict_smith["defaultRecipes"] = ';'.join(bpl)
        for entry in dict_smith:
            out.write(entry + "," + dict_smith[entry] + ",\n")
        out.close()
    
if __name__ == '__main__':
    main()