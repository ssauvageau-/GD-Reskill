# GD-Reskill
Mod for Grim Dawn that allows users to 'extract' procs/skills from items into components!

## Usage:

### gd_reskill.py 

The main generation script. It contains parameters for a Grim Dawn installation directory on Steam in a C:\ drive. 
For the script to work, Grim Dawn's game files *must* be extracted to the installation directory. In addition, it requires a 
**database\reskill\creatures\reskillsmith_smith.dbr** file to exist inside the mod location (not provided here, is in the open-source download of the mod).

Beyond that, the entire process for generation is automatic.

***

The technical premise for how the script works is as follows:

* Obtain a list of items which may have procs/skills on them that we care about. (**main()**)

* Check each item and see if it has a skill on it. If it does, parse and save that item's data into a dictionary (of dictionaries). 
(**process_item()**)

* As part of that parsing process, determine the item's favored damage type: (**process_damage()**)

  * Check to see if the item has any conversion on it. If it does, use the output damage type as the item's "favorite".
  
  * Otherwise, sum up the % Damage Modifiers of the item, treating % DoT Damage as % Flat Damage.
  
  * If % Pierce exists on the item, ignore % Physical.
  
  * Take the highest sum. If the item has no % Damage on it, default to Physical.
  
  * Correspond a particular rare component of the base game to each damage type. 
  
  * The component of the item's favored damage type will be used for crafting the "Skill Rune" in the mod.
  
* When the parsing is completed, write a component file into the mod, using a dummy template file to build off of. 

* Store the filepath of that component file, and create a corresponding blueprint to construct that component in-game. Again,
use a dummy template file to build the blueprint.

* Store the filepath of every blueprint, and then add all of those blueprints to a premade blacksmith file. When this is done,
the mod is ready to be built and deployed.

***

### dir.txt

Used to select which items are considered for making components for. You can add or remove filepaths as you wish.

### 'dummy' files

Template files inside of /components and /blueprints with default parameters already set up. The generation script fills in any blanks
(tag information, component icon information, granted skill information, etc.) before writing the modified file to an actual component.
