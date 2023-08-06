# The Elder Scrolls Toolkit
`tes-toolkit` is a tool to help you track progress in thoroughly minmaxing characters in the Elder Scrolls games.

Currently, **only TES4: Oblivion** is supported.
Morrowind will definitely be added next but other games only if I get round to playing them - patches are welcome if you feel strongly.

## Background
I love Oblivion and decided to properly minmax a character to avoid [the leveling problem](https://en.uesp.net/wiki/Oblivion:Leveling#The_Leveling_Problem).
Copying character information from the game to handwritten notes and tracking progress was tedious and error-prone, so this project was born.
The result is a basic interface written in Python 3  which automates the tedious bookkeeping of the process.

Unlike tools like [Oblivion Character Planner](https://github.com/rdoll/ocp), this tool expects you to know what you're doing and simply makes journaling your progress easier, rather than guiding you by the hand.
Therefore a good grasp of the game's mechanics is required.
If you're a new player check out the [required reading section](#required-reading), which points you to the peerless UESP.

## Installation
`tes-toolkit` is published on [PyPI](https://pypi.org/), so you can simply `pip install tes-toolkit`.
It has no dependencies so won't clutter your machine with junk and can easily be `pip uninstall`ed.
Note the PyPI name `tes-toolkit` vs the module name `tes_toolkit` - [blame the Python developers](https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization).

If you prefer you can also just download `tes_toolkit.py` from [the GitHub repo](https://github.com/WillOnGit/tes-toolkit).

## Quickstart
### Setup
The module is designed to be used from an interactive Python session:
```
someone@computer ~ $ python
>>> import tes_toolkit
```

Most people will want to create a class with a name, specialisation, favoured attributes and major skills, then create a character with a race, gender, class and birthsign.
The 21 default classes are included for completeness' sake, however.
```
# create a custom class - use this to follow the rest of the quickstart
>>> myclass = tes_toolkit.CharacterClass('Class name','magic',['endurance','luck'],['alchemy','alteration','block','conjuration','hand to hand','light armor','marksman'])
>>> c = tes_toolkit.Character('breton','f',myclass,'apprentice')

# alternative - use a default class
>>> alt = tes_toolkit.Character('imperial','m',tes_toolkit.default_classes['battlemage'],'lady')
```

### Core usage loop
Python's autocomplete is highly recommended, e.g. `c.i <TAB> 'someskill')`
```
# print core character info. easy to compare with in-game journal
>>> c.journal()
  ____ _                          _
 / ___| |__   __ _ _ __ __ _  ___| |_ ___ _ __
| |   | '_ \ / _` | '__/ _` |/ __| __/ _ \ '__|
| |___| | | | (_| | | | (_| | (__| ||  __/ |
 \____|_| |_|\__,_|_|  \__,_|\___|\__\___|_|
   _                              _
  (_) ___  _   _ _ __ _ __   __ _| |
  | |/ _ \| | | | '__| '_ \ / _` | |
  | | (_) | |_| | |  | | | | (_| | |
 _/ |\___/ \__,_|_|  |_| |_|\__,_|_|
|__/

LEVEL             1       STRENGTH         30
CLASS    Class name       INTELLIGENCE     50
SIGN     Apprentice       WILLPOWER        50
AGILITY          30
HEALTH           70       SPEED            40
MAGICKA         250       ENDURANCE        35
FATIGUE         145       PERSONALITY      40
ENCUMBRANCE     150       LUCK             55

==================
MAJOR SKILLS
==================
block           25
hand to hand    25
alchemy         35
alteration      35
conjuration     40
light armor     25
marksman        25
==================
MINOR SKILLS
==================
armorer          5
athletics        5
blade            5
blunt            5
heavy armor      5
destruction     10
illusion        15
mysticism       20
restoration     20
acrobatics       5
mercantile       5
security         5
sneak            5
speechcraft      5


# print "hidden" information about this level-up so far
>>> c.progressToLevelUp()
Working towards level 2
majors           0/10
------------------
STRENGTH         0
INTELLIGENCE     0
WILLPOWER        0
AGILITY          0
SPEED            0
ENDURANCE        0
PERSONALITY      0
------------------
Times trained    0/5


# increase a skill when it happens in-game
>>> c.increaseSkill('heavy armor')
heavy armor increased to 6

# increase a single skill by more than one - useful when catching up or at low levels with rapid increases
>>> c.increaseSkill('armorer',9)
armorer increased to 14

>>> c.progressToLevelUp()
Working towards level 2
majors           0/10
------------------
STRENGTH         0
INTELLIGENCE     0
WILLPOWER        0
AGILITY          0
SPEED            0
ENDURANCE       10
PERSONALITY      0
------------------
Times trained    0/5


# track training sessions
>>> c.increaseSkill('alchemy',3,True)
alchemy increased to 38

>>> c.progressToLevelUp()
Working towards level 2
majors           3/10
------------------
STRENGTH         0
INTELLIGENCE     3
WILLPOWER        0
AGILITY          0
SPEED            0
ENDURANCE       10
PERSONALITY      0
------------------
Times trained    3/5


# level up - increase tenth major skill and call levelUp
# endurance, intelligence and luck will be automatically detected as the best attributes to raise
# confirm interactively and you're level 2
>>> c.increaseSkill('conjuration',7)
conjuration increased to 47
Level up available

>>> c.levelUp()
Autodetection succeeded - detected ['intelligence', 'endurance', 'luck']
Are you happy with these attributes? Type 'yes' to proceed
yes

>>> c.journal()
  ____ _                          _
 / ___| |__   __ _ _ __ __ _  ___| |_ ___ _ __
| |   | '_ \ / _` | '__/ _` |/ __| __/ _ \ '__|
| |___| | | | (_| | | | (_| | (__| ||  __/ |
 \____|_| |_|\__,_|_|  \__,_|\___|\__\___|_|
   _                              _
  (_) ___  _   _ _ __ _ __   __ _| |
  | |/ _ \| | | | '__| '_ \ / _` | |
  | | (_) | |_| | |  | | | | (_| | |
 _/ |\___/ \__,_|_|  |_| |_|\__,_|_|
|__/

LEVEL             2       STRENGTH         30
CLASS    Class name       INTELLIGENCE     55
SIGN     Apprentice       WILLPOWER        50
AGILITY          30
HEALTH           84       SPEED            40
MAGICKA         260       ENDURANCE        40
FATIGUE         150       PERSONALITY      40
ENCUMBRANCE     150       LUCK             56

==================
MAJOR SKILLS
==================
block           25
hand to hand    25
alchemy         38
alteration      35
conjuration     47
light armor     25
marksman        25
==================
MINOR SKILLS
==================
armorer         14
athletics        5
blade            5
blunt            5
heavy armor      6
destruction     10
illusion        15
mysticism       20
restoration     20
acrobatics       5
mercantile       5
security         5
sneak            5
speechcraft      5


# save character to file, by default "saved-character.json"
>>> tes_toolkit.saveCharacter(c)
```

### Extras
If you're calling Python from a directory with a `saved-character.json` file, you can invoke the module directly:
```
someone@computer ~ $ python -i -m tes_toolkit
Saved character loaded successfully
>>> 
```
Note the `-i` flag is required so we can actually use our character.
This method also means that you can omit the initial `tes_toolkit.` from calls, e.g. `saveCharacter(c)`.

```
# manually specify attributes to increase on level-up. useful when increasing luck
>>> c.levelUp(['strength','agility','luck'])

# show magic skills by mastery level - leave blank for all skills
>>> c.skillLevels('magic')
==================
   SKILL LEVELS
==================
--- APPRENTICE ---
alchemy         38
alteration      35
conjuration     47

----- NOVICE -----
destruction     10
illusion        15
mysticism       20
restoration     20


# show how we're doing in the overall scheme of minmaxing
>>> c.minmax()
==================
SKILL UP MARGINS
==================
STRENGTH
  0 .................................................. 125
INTELLIGENCE
  0 .................................................. 105
WILLPOWER
  0 .................................................. 135
AGILITY
  0 .................................................. 125
SPEED
  0 .................................................. 145
ENDURANCE
  0 .................................................. 135
PERSONALITY
  0 .................................................. 155
LUCK
  0 ..................................................   4

==================
ATTRIBUTE ORDERING
==================

Status: OK

Increase attributes in any order, although there are only
28 spare level ups until you need to increase AGILITY

==================
IDEAL STATISTICS
==================
LEVEL
  2 ##................................................  50
HEALTH
 84 ######............................................ 648
MAGICKA
260 #####################################............. 350
FATIGUE
150 ###################............................... 400
ENCUMBRANCE
150 ###############................................... 500


# apply the Oghma Infinium bonus interactively
>>> c.oghmaInfinium()
Choose a path from 'steel', 'shadow' or 'spirit'

        STEEL        |        SHADOW       |        SPIRIT
---------------------|---------------------|----------------------
Strength    +10 =  40|Agility     +10 =  40|Intelligence +10 =  65
Speed       +10 =  50|Speed       +10 =  50|
---------------------|---------------------|----------------------
Blade       +10 =  15|Sneak       +10 =  15|Conjuration  +10 =  57
Blunt       +10 =  15|Security    +10 =  15|Restoration  +10 =  30
Heavy Armor +10 =  16|Light Armor +10 =  35|Destruction  +10 =  20

steel
        STEEL
---------------------
Strength    +10 =  40
Speed       +10 =  50
---------------------
Blade       +10 =  15
Blunt       +10 =  15
Heavy Armor +10 =  16

Are you happy with this path? Type 'yes' to proceed
yes


# import an existing character at a level greater than 1.
# only works assuming a level up has just taken place
>>> attributes = {'strength': 35, 'intelligence': 80, 'willpower': 100, 'agility': 30, 'speed': 50, 'endurance': 100, 'personality': 40, 'luck': 65}
>>> skills = {'acrobatics': 24, 'alchemy': 50, 'alteration': 88, 'armorer': 55, 'athletics': 43, 'blade': 30, 'block': 53, 'blunt': 11, 'conjuration': 61, 'destruction': 69, 'hand to hand': 34, 'heavy armor': 58, 'illusion': 47, 'light armor': 36, 'marksman': 28, 'mercantile': 29, 'mysticism': 54, 'restoration': 55, 'security': 22, 'sneak': 13, 'speechcraft': 26}
>>> health = 298
>>> level = 15
>>> c.override(attributes,skills,health,level)
# make sure everything checks out
>>> c.validate()
Everything looks good :)
0

# save characters with a different file name to e.g. keep backups or maintain multiple characters
>>> tes_toolkit.saveCharacter(c,'other filename')

# load a saved character
>>> c = tes_toolkit.loadCharacter('savename')

# last resort in case we didn't save anything here - undoes all progress this level
# WARNING: no prompt
>>> c.resetToLastLevel()
```

## Reference documentation
Full documentation for each class, method etc. is available as docstrings.
Examine the code or browse them interactively for details.
In particular, the module-level documentation has overviews of what's available.

## Required reading
- https://en.uesp.net/wiki/Oblivion:Character_Creation
- https://en.uesp.net/wiki/Oblivion:Attributes
- https://en.uesp.net/wiki/Oblivion:Skills
- https://en.uesp.net/wiki/Oblivion:Leveling
- https://en.uesp.net/wiki/Oblivion:Efficient_Leveling
- https://en.uesp.net/wiki/Oblivion:Increasing_Skills
- https://en.uesp.net/wiki/Oblivion:Endurance (especially the Health Gains section)
