#!/usr/bin/python
# vim: set fileencoding=utf-8

# Change source code to omit mutliple function calls.

import sys
import os
import glob
import re

Mod = "PieAncientEuropeV"
ModOut = "PAE_Opt"

PyModPath = os.path.join("Mods", Mod, "Assets", "Python")
PyOutPath = os.path.join("Mods", ModOut, "Assets", "Python")
SourceFolders = [
    os.path.join("..", "Assets", "Python"),  # Vanilla
    os.path.join("..", "Warlords", "Assets", "Python"),  # WL
    os.path.join("Assets", "Python"),  # BTS
    PyModPath,  # Mod
]

try:
    from CvPythonExtensions import *
except:
    PyOutPath = os.path.join(os.path.sep, "dev", "shm", "Python")
    import os.path
    sys.path.append(os.path.expandvars("$HOME/python/PAE"))
    from CvPythonExtensions import *

    gc = CyGlobalContext()
    ArtFileMgr = CyArtFileMgr()
    localText = CyTranslator()


def undefined_warner(handler, *lArgs):
    s = str(handler(*lArgs))
    if(s) == "-1":
        print("Warning: %s(%s) returns %s" % (
            handler.__name__, ", ".join(lArgs), s))

    return s


def empty_str(_):
    return ""


def getInterfaceArtInfo(sArt):
    return "'" + ArtFileMgr.getInterfaceArtInfo(sArt).getPath() + "'"

Replace_descriptors = {
    __name__: (
        r'^.*'+__name__+'.*$', 0, '%s', empty_str
    ),
    "getInfoTypeForString": (
        r'(self\.)?gc.getInfoTypeForString\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
        2, '%s',  # Resolving of args for Function handler
        gc.getInfoTypeForString,  # Function handler
    ),
    "findInfoTypeNum": (
        r'CvUtil.findInfoTypeNum\([^,]*,[^,]*,\s*[\'"]([^\'"]*)[\'"]\s*\)',
        1, '%s',  # Resolving of args for Function handler
        gc.getInfoTypeForString,  # Function handler
    ),
    "getInterfaceArtInfo": (
        r'ArtFileMgr.getInterfaceArtInfo\(\s*[\'"]([^\'"]*)[\'"]\s*\).getPath\(\)',
        1, '%s',
        getInterfaceArtInfo,
    ),
}

Constant_substitutions = {
    "max_players": ["gc.getMAX_PLAYERS()", gc.getMAX_PLAYERS()],
    "max_teams": ["gc.getMAX_TEAMS()", gc.getMAX_TEAMS()],
    "barb_player": ["gc.getBARBARIAN_PLAYER()", gc.getBARBARIAN_PLAYER()],
    "barb_team": ["gc.getBARBARIAN_TEAM()", gc.getBARBARIAN_TEAM()],
}

Type_varname_splitter = list(" :),+-%\t")
Type_substitutions = {
    "WidgetTypes.WIDGET_GENERAL": [WidgetTypes.WIDGET_GENERAL],
    "FontTypes.TITLE_FONT": [FontTypes.TITLE_FONT],
    "WidgetTypes.WIDGET_PYTHON": [WidgetTypes.WIDGET_PYTHON],
    "FontTypes.GAME_FONT": [FontTypes.GAME_FONT],
    "DirectionTypes.DIRECTION_SOUTH": [DirectionTypes.DIRECTION_SOUTH],
    "ButtonPopupTypes.BUTTONPOPUP_TEXT": [ButtonPopupTypes.BUTTONPOPUP_TEXT],
    "UnitAITypes.NO_UNITAI": [UnitAITypes.NO_UNITAI],
    "ButtonPopupTypes.BUTTONPOPUP_PYTHON": [ButtonPopupTypes.BUTTONPOPUP_PYTHON],
    "CommandTypes.COMMAND_DELETE": [CommandTypes.COMMAND_DELETE],
    "FontTypes.SMALL_FONT": [FontTypes.SMALL_FONT],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION],
    "WidgetTypes.WIDGET_CLOSE_SCREEN": [WidgetTypes.WIDGET_CLOSE_SCREEN],
    "CommerceTypes.COMMERCE_CULTURE": [CommerceTypes.COMMERCE_CULTURE],
    "YieldTypes.NUM_YIELD_TYPES": [YieldTypes.NUM_YIELD_TYPES],
    "YieldTypes.YIELD_PRODUCTION": [YieldTypes.YIELD_PRODUCTION],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS],
    "CommerceTypes.COMMERCE_RESEARCH": [CommerceTypes.COMMERCE_RESEARCH],
    "YieldTypes.YIELD_FOOD": [YieldTypes.YIELD_FOOD],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH],
    "WidgetTypes.WIDGET_ACTION": [WidgetTypes.WIDGET_ACTION],
    "UnitAITypes.UNITAI_ATTACK": [UnitAITypes.UNITAI_ATTACK],
    "CommerceTypes.NUM_COMMERCE_TYPES": [CommerceTypes.NUM_COMMERCE_TYPES],
    "BuildingTypes.NO_BUILDING": [BuildingTypes.NO_BUILDING],
    "InfoBarTypes.INFOBAR_STORED": [InfoBarTypes.INFOBAR_STORED],
    "CommerceTypes.COMMERCE_GOLD": [CommerceTypes.COMMERCE_GOLD],
    "InfoBarTypes.INFOBAR_RATE": [InfoBarTypes.INFOBAR_RATE],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING],
    "WidgetTypes.WIDGET_HELP_SELECTED": [WidgetTypes.WIDGET_HELP_SELECTED],
    "WidgetTypes.WIDGET_PEDIA_MAIN": [WidgetTypes.WIDGET_PEDIA_MAIN],
    "InterfaceMessageTypes.MESSAGE_TYPE_INFO": [InterfaceMessageTypes.MESSAGE_TYPE_INFO],
    "DirectionTypes.NUM_DIRECTION_TYPES": [DirectionTypes.NUM_DIRECTION_TYPES],
    "DirectionTypes.NO_DIRECTION": [DirectionTypes.NO_DIRECTION],
    "InfoBarTypes.NUM_INFOBAR_TYPES": [InfoBarTypes.NUM_INFOBAR_TYPES],
    "CardinalDirectionTypes.NO_CARDINALDIRECTION": [CardinalDirectionTypes.NO_CARDINALDIRECTION],
    "EventContextTypes.EVENTCONTEXT_ALL": [EventContextTypes.EVENTCONTEXT_ALL],
    "HitTestTypes.HITTEST_NOHIT": [HitTestTypes.HITTEST_NOHIT],
    "CardinalDirectionTypes.CARDINALDIRECTION_NORTH": [CardinalDirectionTypes.CARDINALDIRECTION_NORTH],
    "CardinalDirectionTypes.CARDINALDIRECTION_EAST": [CardinalDirectionTypes.CARDINALDIRECTION_EAST],
    "OrderTypes.ORDER_CONSTRUCT": [OrderTypes.ORDER_CONSTRUCT],
    "YieldTypes.YIELD_COMMERCE": [YieldTypes.YIELD_COMMERCE],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT],
    "UnitTypes.NO_UNIT": [UnitTypes.NO_UNIT],
    "PlayerTypes.NO_PLAYER": [PlayerTypes.NO_PLAYER],
    "InfoBarTypes.INFOBAR_RATE_EXTRA": [InfoBarTypes.INFOBAR_RATE_EXTRA],
    "WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV],
    "WidgetTypes.WIDGET_LEADERHEAD": [WidgetTypes.WIDGET_LEADERHEAD],
    "UnitAITypes.UNITAI_EXPLORE": [UnitAITypes.UNITAI_EXPLORE],
    "GameOptionTypes.GAMEOPTION_NO_BARBARIANS": [GameOptionTypes.GAMEOPTION_NO_BARBARIANS],
    "WidgetTypes.WIDGET_HELP_RELIGION": [WidgetTypes.WIDGET_HELP_RELIGION],
    "WidgetTypes.WIDGET_HELP_PROMOTION": [WidgetTypes.WIDGET_HELP_PROMOTION],
"WidgetTypes.WIDGET_HELP_BUILDING": [WidgetTypes.WIDGET_HELP_BUILDING],
"OrderTypes.ORDER_TRAIN": [OrderTypes.ORDER_TRAIN],
"GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE": [GameOptionTypes.GAMEOPTION_ONE_CITY_CHALLENGE],
"CardinalDirectionTypes.CARDINALDIRECTION_WEST": [CardinalDirectionTypes.CARDINALDIRECTION_WEST],
"CardinalDirectionTypes.CARDINALDIRECTION_SOUTH": [CardinalDirectionTypes.CARDINALDIRECTION_SOUTH],
"DomainTypes.DOMAIN_SEA": [DomainTypes.DOMAIN_SEA],
"CommerceTypes.COMMERCE_ESPIONAGE": [CommerceTypes.COMMERCE_ESPIONAGE],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT_NEW],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_CONCEPT],
"ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN": [ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN],
"WidgetTypes.WIDGET_FOREIGN_ADVISOR": [WidgetTypes.WIDGET_FOREIGN_ADVISOR],
"WidgetTypes.WIDGET_CITIZEN": [WidgetTypes.WIDGET_CITIZEN],
"PlotTypes.PLOT_LAND": [PlotTypes.PLOT_LAND],
"MissionAITypes.NO_MISSIONAI": [MissionAITypes.NO_MISSIONAI],
"InfoBarTypes.INFOBAR_EMPTY": [InfoBarTypes.INFOBAR_EMPTY],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_TECH": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_TECH],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_BUILDING": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_BUILDING],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_BONUS": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_BONUS],
"AttitudeTypes.ATTITUDE_PLEASED": [AttitudeTypes.ATTITUDE_PLEASED],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT],
"WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT": [WidgetTypes.WIDGET_MINIMAP_HIGHLIGHT],
"UnitAITypes.UNITAI_MISSIONARY": [UnitAITypes.UNITAI_MISSIONARY],
"UnitAITypes.UNITAI_ATTACK_CITY_LEMMING": [UnitAITypes.UNITAI_ATTACK_CITY_LEMMING],
"UnitAITypes.UNITAI_ANIMAL": [UnitAITypes.UNITAI_ANIMAL],
"PlotTypes.PLOT_OCEAN": [PlotTypes.PLOT_OCEAN],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT_GROUP": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT_GROUP],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_TERRAIN": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_TERRAIN],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPECIALIST": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_SPECIALIST],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_RELIGION": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_RELIGION],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROMOTION": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROMOTION],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROJECT": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_PROJECT],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_LEADER": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_LEADER],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_IMPROVEMENT": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_IMPROVEMENT],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_FEATURE": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_FEATURE],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_CORPORATION": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_CORPORATION],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIVIC": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIVIC],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIV": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_CIV],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIVIC],
"FeatureTypes.NO_FEATURE": [FeatureTypes.NO_FEATURE],
"DomainTypes.DOMAIN_LAND": [DomainTypes.DOMAIN_LAND],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROJECT],
"PlotTypes.NUM_PLOT_TYPES": [PlotTypes.NUM_PLOT_TYPES],
"OrderTypes.ORDER_CREATE": [OrderTypes.ORDER_CREATE],
"BonusTypes.NO_BONUS": [BonusTypes.NO_BONUS],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION],
"WidgetTypes.WIDGET_PEDIA_DESCRIPTION": [WidgetTypes.WIDGET_PEDIA_DESCRIPTION],
"WidgetTypes.WIDGET_EMPHASIZE": [WidgetTypes.WIDGET_EMPHASIZE],
"WidgetTypes.WIDGET_CHANGE_PERCENT": [WidgetTypes.WIDGET_CHANGE_PERCENT],
"UnitAITypes.NUM_UNITAI_TYPES": [UnitAITypes.NUM_UNITAI_TYPES],
"MinimapModeTypes.MINIMAPMODE_REPLAY": [MinimapModeTypes.MINIMAPMODE_REPLAY],
"AttitudeTypes.ATTITUDE_FURIOUS": [AttitudeTypes.ATTITUDE_FURIOUS],
"WidgetTypes.WIDGET_TECH_TREE": [WidgetTypes.WIDGET_TECH_TREE],
"WidgetTypes.WIDGET_RESEARCH": [WidgetTypes.WIDGET_RESEARCH],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_IMPROVEMENT],
"WidgetTypes.WIDGET_HELP_GREAT_GENERAL": [WidgetTypes.WIDGET_HELP_GREAT_GENERAL],
"WidgetTypes.WIDGET_CONTACT_CIV": [WidgetTypes.WIDGET_CONTACT_CIV],
"TechTypes.NO_TECH": [TechTypes.NO_TECH],
"PlotTypes.PLOT_PEAK": [PlotTypes.PLOT_PEAK],
"PlotTypes.PLOT_HILLS": [PlotTypes.PLOT_HILLS],
"OrderTypes.ORDER_MAINTAIN": [OrderTypes.ORDER_MAINTAIN],
"FeatTypes.FEAT_UNITCOMBAT_ARCHER": [FeatTypes.FEAT_UNITCOMBAT_ARCHER],
"FeatTypes.FEAT_FOOD_CONNECTED": [FeatTypes.FEAT_FOOD_CONNECTED],
"DomainTypes.NUM_DOMAIN_TYPES": [DomainTypes.NUM_DOMAIN_TYPES],
"DomainTypes.DOMAIN_AIR": [DomainTypes.DOMAIN_AIR],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_HINTS": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_HINTS],
"AttitudeTypes.ATTITUDE_FRIENDLY": [AttitudeTypes.ATTITUDE_FRIENDLY],
"AttitudeTypes.ATTITUDE_ANNOYED": [AttitudeTypes.ATTITUDE_ANNOYED],
"ActivationTypes.ACTIVATE_MIMICPARENTFOCUS": [ActivationTypes.ACTIVATE_MIMICPARENTFOCUS],
"WidgetTypes.WIDGET_WB_EXIT_BUTTON": [WidgetTypes.WIDGET_WB_EXIT_BUTTON],
"WidgetTypes.WIDGET_TRAIN": [WidgetTypes.WIDGET_TRAIN],
"WidgetTypes.WIDGET_PLOT_LIST": [WidgetTypes.WIDGET_PLOT_LIST],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_TERRAIN],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_SPECIALIST],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_FEATURE],
"WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME": [WidgetTypes.WIDGET_HELP_FINANCE_FOREIGN_INCOME],
"WidgetTypes.WIDGET_CHANGE_SPECIALIST": [WidgetTypes.WIDGET_CHANGE_SPECIALIST],
"UnitAITypes.UNITAI_CITY_DEFENSE": [UnitAITypes.UNITAI_CITY_DEFENSE],
"PlayerOptionTypes.NUM_PLAYEROPTION_TYPES": [PlayerOptionTypes.NUM_PLAYEROPTION_TYPES],
"FeatTypes.FEAT_UNIT_SPY": [FeatTypes.FEAT_UNIT_SPY],
"FeatTypes.FEAT_TRADE_ROUTE": [FeatTypes.FEAT_TRADE_ROUTE],
"FeatTypes.FEAT_NATIONAL_WONDER": [FeatTypes.FEAT_NATIONAL_WONDER],
"FeatTypes.FEAT_CORPORATION_ENABLED": [FeatTypes.FEAT_CORPORATION_ENABLED],
"FeatTypes.FEAT_COPPER_CONNECTED": [FeatTypes.FEAT_COPPER_CONNECTED],
"DenialTypes.NO_DENIAL": [DenialTypes.NO_DENIAL],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_WONDER": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_WONDER],
"AttitudeTypes.ATTITUDE_CAUTIOUS": [AttitudeTypes.ATTITUDE_CAUTIOUS],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_UNIT],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_ROUTE],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_POP],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_IMPROVEMENT],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_BUILDING],
"ActivityTypes.ACTIVITY_SLEEP": [ActivityTypes.ACTIVITY_SLEEP],
"ActivityTypes.ACTIVITY_HOLD": [ActivityTypes.ACTIVITY_HOLD],
"ActivationTypes.ACTIVATE_NORMAL": [ActivationTypes.ACTIVATE_NORMAL],
"WidgetTypes.WIDGET_UNIT_NAME": [WidgetTypes.WIDGET_UNIT_NAME],
"WidgetTypes.WIDGET_HELP_WATER_WORK": [WidgetTypes.WIDGET_HELP_WATER_WORK],
"WidgetTypes.WIDGET_HELP_VASSAL_STATE": [WidgetTypes.WIDGET_HELP_VASSAL_STATE],
"WidgetTypes.WIDGET_HELP_TECH_TRADE": [WidgetTypes.WIDGET_HELP_TECH_TRADE],
"WidgetTypes.WIDGET_HELP_RELIGION_CITY": [WidgetTypes.WIDGET_HELP_RELIGION_CITY],
"WidgetTypes.WIDGET_HELP_PERMANENT_ALLIANCE": [WidgetTypes.WIDGET_HELP_PERMANENT_ALLIANCE],
"WidgetTypes.WIDGET_HELP_OPEN_BORDERS": [WidgetTypes.WIDGET_HELP_OPEN_BORDERS],
"WidgetTypes.WIDGET_HELP_MAP_TRADE": [WidgetTypes.WIDGET_HELP_MAP_TRADE],
"WidgetTypes.WIDGET_HELP_MAP_CENTER": [WidgetTypes.WIDGET_HELP_MAP_CENTER],
"WidgetTypes.WIDGET_HELP_LOS_BONUS": [WidgetTypes.WIDGET_HELP_LOS_BONUS],
"WidgetTypes.WIDGET_HELP_IRRIGATION": [WidgetTypes.WIDGET_HELP_IRRIGATION],
"WidgetTypes.WIDGET_HELP_IGNORE_IRRIGATION": [WidgetTypes.WIDGET_HELP_IGNORE_IRRIGATION],
"WidgetTypes.WIDGET_HELP_GOLD_TRADE": [WidgetTypes.WIDGET_HELP_GOLD_TRADE],
"WidgetTypes.WIDGET_HELP_DEFENSIVE_PACT": [WidgetTypes.WIDGET_HELP_DEFENSIVE_PACT],
"WidgetTypes.WIDGET_HELP_CORPORATION_CITY": [WidgetTypes.WIDGET_HELP_CORPORATION_CITY],
"WidgetTypes.WIDGET_HELP_BUILD_BRIDGE": [WidgetTypes.WIDGET_HELP_BUILD_BRIDGE],
"WidgetTypes.WIDGET_CONSTRUCT": [WidgetTypes.WIDGET_CONSTRUCT],
"WidgetTypes.WIDGET_CITY_TAB": [WidgetTypes.WIDGET_CITY_TAB],
"WidgetTypes.WIDGET_CITY_NAME": [WidgetTypes.WIDGET_CITY_NAME],
"UnitAITypes.UNITAI_PIRATE_SEA": [UnitAITypes.UNITAI_PIRATE_SEA],
"UnitAITypes.UNITAI_MERCHANT": [UnitAITypes.UNITAI_MERCHANT],
"PlotTypes.NO_PLOT": [PlotTypes.NO_PLOT],
"MissionTypes.MISSION_SKIP": [MissionTypes.MISSION_SKIP],
"MissionTypes.MISSION_MOVE_TO": [MissionTypes.MISSION_MOVE_TO],
"MinimapModeTypes.MINIMAPMODE_MILITARY": [MinimapModeTypes.MINIMAPMODE_MILITARY],
"InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT": [InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT],
"InputTypes.KB_RSHIFT": [InputTypes.KB_RSHIFT],
"InputTypes.KB_RETURN": [InputTypes.KB_RETURN],
"InputTypes.KB_LSHIFT": [InputTypes.KB_LSHIFT],
"GraphicOptionTypes.NUM_GRAPHICOPTION_TYPES": [GraphicOptionTypes.NUM_GRAPHICOPTION_TYPES],
"GameStateTypes.GAMESTATE_EXTENDED": [GameStateTypes.GAMESTATE_EXTENDED],
"GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS": [GameOptionTypes.GAMEOPTION_NO_GOODY_HUTS],
"GameOptionTypes.GAMEOPTION_ADVANCED_START": [GameOptionTypes.GAMEOPTION_ADVANCED_START],
"FeatTypes.FEAT_UNIT_PRIVATEER": [FeatTypes.FEAT_UNIT_PRIVATEER],
"FeatTypes.FEAT_UNITCOMBAT_SIEGE": [FeatTypes.FEAT_UNITCOMBAT_SIEGE],
"FeatTypes.FEAT_UNITCOMBAT_NAVAL": [FeatTypes.FEAT_UNITCOMBAT_NAVAL],
"FeatTypes.FEAT_UNITCOMBAT_MOUNTED": [FeatTypes.FEAT_UNITCOMBAT_MOUNTED],
"FeatTypes.FEAT_UNITCOMBAT_MELEE": [FeatTypes.FEAT_UNITCOMBAT_MELEE],
"FeatTypes.FEAT_UNITCOMBAT_HELICOPTER": [FeatTypes.FEAT_UNITCOMBAT_HELICOPTER],
"FeatTypes.FEAT_UNITCOMBAT_GUN": [FeatTypes.FEAT_UNITCOMBAT_GUN],
"FeatTypes.FEAT_UNITCOMBAT_ARMOR": [FeatTypes.FEAT_UNITCOMBAT_ARMOR],
"FeatTypes.FEAT_LUXURY_CONNECTED": [FeatTypes.FEAT_LUXURY_CONNECTED],
"FeatTypes.FEAT_IRON_CONNECTED": [FeatTypes.FEAT_IRON_CONNECTED],
"FeatTypes.FEAT_HORSE_CONNECTED": [FeatTypes.FEAT_HORSE_CONNECTED],
"EventContextTypes.NO_EVENTCONTEXT": [EventContextTypes.NO_EVENTCONTEXT],
"CivilopediaPageTypes.NUM_CIVILOPEDIA_PAGE_TYPES": [CivilopediaPageTypes.NUM_CIVILOPEDIA_PAGE_TYPES],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_VISIBILITY": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_VISIBILITY],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_CULTURE": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_CULTURE],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_CITY": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_CITY],
"WidgetTypes.WIDGET_WB_UNREVEAL_ALL_BUTTON": [WidgetTypes.WIDGET_WB_UNREVEAL_ALL_BUTTON],
"WidgetTypes.WIDGET_WB_UNIT_EDIT_BUTTON": [WidgetTypes.WIDGET_WB_UNIT_EDIT_BUTTON],
"WidgetTypes.WIDGET_WB_SAVE_BUTTON": [WidgetTypes.WIDGET_WB_SAVE_BUTTON],
"WidgetTypes.WIDGET_WB_REVEAL_TAB_MODE_BUTTON": [WidgetTypes.WIDGET_WB_REVEAL_TAB_MODE_BUTTON],
"WidgetTypes.WIDGET_WB_REVEAL_ALL_BUTTON": [WidgetTypes.WIDGET_WB_REVEAL_ALL_BUTTON],
"WidgetTypes.WIDGET_WB_REGENERATE_MAP": [WidgetTypes.WIDGET_WB_REGENERATE_MAP],
"WidgetTypes.WIDGET_WB_NORMAL_PLAYER_TAB_MODE_BUTTON": [WidgetTypes.WIDGET_WB_NORMAL_PLAYER_TAB_MODE_BUTTON],
"WidgetTypes.WIDGET_WB_NORMAL_MAP_TAB_MODE_BUTTON": [WidgetTypes.WIDGET_WB_NORMAL_MAP_TAB_MODE_BUTTON],
"WidgetTypes.WIDGET_WB_LOAD_BUTTON": [WidgetTypes.WIDGET_WB_LOAD_BUTTON],
"WidgetTypes.WIDGET_WB_LANDMARK_BUTTON": [WidgetTypes.WIDGET_WB_LANDMARK_BUTTON],
"WidgetTypes.WIDGET_WB_ERASE_BUTTON": [WidgetTypes.WIDGET_WB_ERASE_BUTTON],
"WidgetTypes.WIDGET_WB_DIPLOMACY_MODE_BUTTON": [WidgetTypes.WIDGET_WB_DIPLOMACY_MODE_BUTTON],
"WidgetTypes.WIDGET_WB_CITY_EDIT_BUTTON": [WidgetTypes.WIDGET_WB_CITY_EDIT_BUTTON],
"WidgetTypes.WIDGET_PLOT_LIST_SHIFT": [WidgetTypes.WIDGET_PLOT_LIST_SHIFT],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_REQUIRED_TECH": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_REQUIRED_TECH],
"WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH": [WidgetTypes.WIDGET_PEDIA_JUMP_TO_DERIVED_TECH],
"WidgetTypes.WIDGET_PEDIA_FORWARD": [WidgetTypes.WIDGET_PEDIA_FORWARD],
"WidgetTypes.WIDGET_PEDIA_BACK": [WidgetTypes.WIDGET_PEDIA_BACK],
"WidgetTypes.WIDGET_MAINTAIN": [WidgetTypes.WIDGET_MAINTAIN],
"WidgetTypes.WIDGET_HURRY": [WidgetTypes.WIDGET_HURRY],
"WidgetTypes.WIDGET_HELP_TRADE_ROUTE_CITY": [WidgetTypes.WIDGET_HELP_TRADE_ROUTE_CITY],
"WidgetTypes.WIDGET_HELP_TERRAIN_TRADE": [WidgetTypes.WIDGET_HELP_TERRAIN_TRADE],
"WidgetTypes.WIDGET_HELP_TECH_PREPREQ": [WidgetTypes.WIDGET_HELP_TECH_PREPREQ],
"WidgetTypes.WIDGET_HELP_OBSOLETE_SPECIAL": [WidgetTypes.WIDGET_HELP_OBSOLETE_SPECIAL],
"WidgetTypes.WIDGET_HELP_OBSOLETE_BONUS": [WidgetTypes.WIDGET_HELP_OBSOLETE_BONUS],
"WidgetTypes.WIDGET_HELP_OBSOLETE": [WidgetTypes.WIDGET_HELP_OBSOLETE],
"WidgetTypes.WIDGET_HELP_MAINTENANCE": [WidgetTypes.WIDGET_HELP_MAINTENANCE],
"WidgetTypes.WIDGET_HELP_GREAT_PEOPLE": [WidgetTypes.WIDGET_HELP_GREAT_PEOPLE],
"WidgetTypes.WIDGET_HELP_FINANCE_UNIT_COST": [WidgetTypes.WIDGET_HELP_FINANCE_UNIT_COST],
"WidgetTypes.WIDGET_HELP_FINANCE_INFLATED_COSTS": [WidgetTypes.WIDGET_HELP_FINANCE_INFLATED_COSTS],
"WidgetTypes.WIDGET_HELP_FINANCE_GROSS_INCOME": [WidgetTypes.WIDGET_HELP_FINANCE_GROSS_INCOME],
"WidgetTypes.WIDGET_HELP_FINANCE_CIVIC_UPKEEP": [WidgetTypes.WIDGET_HELP_FINANCE_CIVIC_UPKEEP],
"WidgetTypes.WIDGET_HELP_FINANCE_CITY_MAINT": [WidgetTypes.WIDGET_HELP_FINANCE_CITY_MAINT],
"WidgetTypes.WIDGET_HELP_FINANCE_AWAY_SUPPLY": [WidgetTypes.WIDGET_HELP_FINANCE_AWAY_SUPPLY],
"WidgetTypes.WIDGET_FLAG": [WidgetTypes.WIDGET_FLAG],
"WidgetTypes.WIDGET_CREATE": [WidgetTypes.WIDGET_CREATE],
"WidgetTypes.WIDGET_CITY_SCROLL": [WidgetTypes.WIDGET_CITY_SCROLL],
"WidgetTypes.WIDGET_ANGRY_CITIZEN": [WidgetTypes.WIDGET_ANGRY_CITIZEN],
"WarPlanTypes.WARPLAN_LIMITED": [WarPlanTypes.WARPLAN_LIMITED],
"WarPlanTypes.NO_WARPLAN": [WarPlanTypes.NO_WARPLAN],
"UnitAITypes.UNITAI_SETTLE": [UnitAITypes.UNITAI_SETTLE],
"UnitAITypes.UNITAI_RESERVE": [UnitAITypes.UNITAI_RESERVE],
"UnitAITypes.UNITAI_PILLAGE": [UnitAITypes.UNITAI_PILLAGE],
"UnitAITypes.UNITAI_CITY_COUNTER": [UnitAITypes.UNITAI_CITY_COUNTER],
"UnitAITypes.UNITAI_ATTACK_SEA": [UnitAITypes.UNITAI_ATTACK_SEA],
"UnitAITypes.UNITAI_ATTACK_CITY": [UnitAITypes.UNITAI_ATTACK_CITY],
"PlayerOptionTypes.PLAYEROPTION_MODDER_1": [PlayerOptionTypes.PLAYEROPTION_MODDER_1],
"PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS": [PlayerOptionTypes.PLAYEROPTION_ADVISOR_POPUPS],
"MultiplayerOptionTypes.MPOPTION_ANONYMOUS": [MultiplayerOptionTypes.MPOPTION_ANONYMOUS],
"MissionTypes.MISSION_TRADE": [MissionTypes.MISSION_TRADE],
"MissionTypes.MISSION_BUILD": [MissionTypes.MISSION_BUILD],
"InputTypes.KB_ESCAPE": [InputTypes.KB_ESCAPE],
"GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES": [GraphicOptionTypes.GRAPHICOPTION_NO_MOVIES],
"GameOptionTypes.GAMEOPTION_RAGING_BARBARIANS": [GameOptionTypes.GAMEOPTION_RAGING_BARBARIANS],
"GameOptionTypes.GAMEOPTION_PICK_RELIGION": [GameOptionTypes.GAMEOPTION_PICK_RELIGION],
"GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES": [GameOptionTypes.GAMEOPTION_NO_VASSAL_STATES],
"GameOptionTypes.GAMEOPTION_NO_ESPIONAGE": [GameOptionTypes.GAMEOPTION_NO_ESPIONAGE],
"GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV": [GameOptionTypes.GAMEOPTION_LEAD_ANY_CIV],
"GameOptionTypes.GAMEOPTION_ALWAYS_WAR": [GameOptionTypes.GAMEOPTION_ALWAYS_WAR],
"FeatTypes.FEAT_POPULATION_HALF_MILLION": [FeatTypes.FEAT_POPULATION_HALF_MILLION],
"FeatTypes.FEAT_POPULATION_2_BILLION": [FeatTypes.FEAT_POPULATION_2_BILLION],
"DiploEventTypes.DIPLOEVENT_DEMAND_WAR": [DiploEventTypes.DIPLOEVENT_DEMAND_WAR],
"CultureLevelTypes.NO_CULTURELEVEL": [CultureLevelTypes.NO_CULTURELEVEL],
"CommandTypes.COMMAND_UNLOAD_ALL": [CommandTypes.COMMAND_UNLOAD_ALL],
"AttitudeTypes.NUM_ATTITUDE_TYPES": [AttitudeTypes.NUM_ATTITUDE_TYPES],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_AUTOMATE],
"ActivityTypes.ACTIVITY_PLUNDER": [ActivityTypes.ACTIVITY_PLUNDER],
"ActivityTypes.ACTIVITY_PATROL": [ActivityTypes.ACTIVITY_PATROL],
"ActivityTypes.ACTIVITY_INTERCEPT": [ActivityTypes.ACTIVITY_INTERCEPT],
"ActivityTypes.ACTIVITY_HEAL": [ActivityTypes.ACTIVITY_HEAL],
"WorldSizeTypes.WORLDSIZE_TINY": [WorldSizeTypes.WORLDSIZE_TINY],
"WorldSizeTypes.WORLDSIZE_STANDARD": [WorldSizeTypes.WORLDSIZE_STANDARD],
"WorldSizeTypes.WORLDSIZE_SMALL": [WorldSizeTypes.WORLDSIZE_SMALL],
"WorldSizeTypes.WORLDSIZE_LARGE": [WorldSizeTypes.WORLDSIZE_LARGE],
"WorldSizeTypes.WORLDSIZE_HUGE": [WorldSizeTypes.WORLDSIZE_HUGE],
"WorldSizeTypes.WORLDSIZE_DUEL": [WorldSizeTypes.WORLDSIZE_DUEL],
"WorldBuilderPopupTypes.WBPOPUP_UNIT": [WorldBuilderPopupTypes.WBPOPUP_UNIT],
"WorldBuilderPopupTypes.WBPOPUP_START": [WorldBuilderPopupTypes.WBPOPUP_START],
"WorldBuilderPopupTypes.WBPOPUP_PLOT": [WorldBuilderPopupTypes.WBPOPUP_PLOT],
"WorldBuilderPopupTypes.WBPOPUP_PLAYER": [WorldBuilderPopupTypes.WBPOPUP_PLAYER],
"WorldBuilderPopupTypes.WBPOPUP_CITY": [WorldBuilderPopupTypes.WBPOPUP_CITY],
"WidgetTypes.WIDGET_ZOOM_CITY": [WidgetTypes.WIDGET_ZOOM_CITY],
"WidgetTypes.WIDGET_WB_ALL_PLOTS_BUTTON": [WidgetTypes.WIDGET_WB_ALL_PLOTS_BUTTON],
"WidgetTypes.WIDGET_UNIT_MODEL": [WidgetTypes.WIDGET_UNIT_MODEL],
"WidgetTypes.WIDGET_REVOLUTION": [WidgetTypes.WIDGET_REVOLUTION],
"WidgetTypes.WIDGET_PRODUCTION_MOD_HELP": [WidgetTypes.WIDGET_PRODUCTION_MOD_HELP],
"WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP": [WidgetTypes.WIDGET_PEDIA_DESCRIPTION_NO_HELP],
"WidgetTypes.WIDGET_MENU_ICON": [WidgetTypes.WIDGET_MENU_ICON],
"WidgetTypes.WIDGET_LIBERATE_CITY": [WidgetTypes.WIDGET_LIBERATE_CITY],
"WidgetTypes.WIDGET_HELP_YIELD_CHANGE": [WidgetTypes.WIDGET_HELP_YIELD_CHANGE],
"WidgetTypes.WIDGET_HELP_WORKER_RATE": [WidgetTypes.WIDGET_HELP_WORKER_RATE],
"WidgetTypes.WIDGET_HELP_TRADE_ROUTES": [WidgetTypes.WIDGET_HELP_TRADE_ROUTES],
"WidgetTypes.WIDGET_HELP_SPECIAL_BUILDING": [WidgetTypes.WIDGET_HELP_SPECIAL_BUILDING],
"WidgetTypes.WIDGET_HELP_PRODUCTION": [WidgetTypes.WIDGET_HELP_PRODUCTION],
"WidgetTypes.WIDGET_HELP_PROCESS_INFO": [WidgetTypes.WIDGET_HELP_PROCESS_INFO],
"WidgetTypes.WIDGET_HELP_POPULATION": [WidgetTypes.WIDGET_HELP_POPULATION],
"WidgetTypes.WIDGET_HELP_NATIONALITY": [WidgetTypes.WIDGET_HELP_NATIONALITY],
"WidgetTypes.WIDGET_HELP_MOVE_BONUS": [WidgetTypes.WIDGET_HELP_MOVE_BONUS],
"WidgetTypes.WIDGET_HELP_MAP_REVEAL": [WidgetTypes.WIDGET_HELP_MAP_REVEAL],
"WidgetTypes.WIDGET_HELP_IMPROVEMENT": [WidgetTypes.WIDGET_HELP_IMPROVEMENT],
"WidgetTypes.WIDGET_HELP_HEALTH_RATE": [WidgetTypes.WIDGET_HELP_HEALTH_RATE],
"WidgetTypes.WIDGET_HELP_HEALTH": [WidgetTypes.WIDGET_HELP_HEALTH],
"WidgetTypes.WIDGET_HELP_HAPPINESS_RATE": [WidgetTypes.WIDGET_HELP_HAPPINESS_RATE],
"WidgetTypes.WIDGET_HELP_HAPPINESS": [WidgetTypes.WIDGET_HELP_HAPPINESS],
"WidgetTypes.WIDGET_HELP_FREE_UNIT": [WidgetTypes.WIDGET_HELP_FREE_UNIT],
"WidgetTypes.WIDGET_HELP_FREE_TECH": [WidgetTypes.WIDGET_HELP_FREE_TECH],
"WidgetTypes.WIDGET_HELP_FOUND_RELIGION": [WidgetTypes.WIDGET_HELP_FOUND_RELIGION],
"WidgetTypes.WIDGET_HELP_FOUND_CORPORATION": [WidgetTypes.WIDGET_HELP_FOUND_CORPORATION],
"WidgetTypes.WIDGET_HELP_FINANCE_GOLD_RESERVE": [WidgetTypes.WIDGET_HELP_FINANCE_GOLD_RESERVE],
"WidgetTypes.WIDGET_HELP_FEATURE_PRODUCTION": [WidgetTypes.WIDGET_HELP_FEATURE_PRODUCTION],
"WidgetTypes.WIDGET_HELP_DOMAIN_EXTRA_MOVES": [WidgetTypes.WIDGET_HELP_DOMAIN_EXTRA_MOVES],
"WidgetTypes.WIDGET_HELP_DEFENSE": [WidgetTypes.WIDGET_HELP_DEFENSE],
"WidgetTypes.WIDGET_HELP_CULTURE": [WidgetTypes.WIDGET_HELP_CULTURE],
"WidgetTypes.WIDGET_HELP_CIVIC_REVEAL": [WidgetTypes.WIDGET_HELP_CIVIC_REVEAL],
"WidgetTypes.WIDGET_HELP_BONUS_REVEAL": [WidgetTypes.WIDGET_HELP_BONUS_REVEAL],
"WidgetTypes.WIDGET_HELP_ADJUST": [WidgetTypes.WIDGET_HELP_ADJUST],
"WidgetTypes.WIDGET_GLOBELAYER_OPTION": [WidgetTypes.WIDGET_GLOBELAYER_OPTION],
"WidgetTypes.WIDGET_GLOBELAYER": [WidgetTypes.WIDGET_GLOBELAYER],
"WidgetTypes.WIDGET_FREE_CITIZEN": [WidgetTypes.WIDGET_FREE_CITIZEN],
"WidgetTypes.WIDGET_END_TURN": [WidgetTypes.WIDGET_END_TURN],
"WidgetTypes.WIDGET_DISABLED_CITIZEN": [WidgetTypes.WIDGET_DISABLED_CITIZEN],
"WidgetTypes.WIDGET_DELETE_GROUP": [WidgetTypes.WIDGET_DELETE_GROUP],
"WidgetTypes.WIDGET_DEAL_KILL": [WidgetTypes.WIDGET_DEAL_KILL],
"WidgetTypes.WIDGET_CREATE_GROUP": [WidgetTypes.WIDGET_CREATE_GROUP],
"WidgetTypes.WIDGET_CONVERT": [WidgetTypes.WIDGET_CONVERT],
"WidgetTypes.WIDGET_CONSCRIPT": [WidgetTypes.WIDGET_CONSCRIPT],
"WidgetTypes.WIDGET_COMMERCE_MOD_HELP": [WidgetTypes.WIDGET_COMMERCE_MOD_HELP],
"WidgetTypes.WIDGET_AUTOMATE_PRODUCTION": [WidgetTypes.WIDGET_AUTOMATE_PRODUCTION],
"WidgetTypes.WIDGET_AUTOMATE_CITIZENS": [WidgetTypes.WIDGET_AUTOMATE_CITIZENS],
"UnitCombatTypes.NO_UNITCOMBAT": [UnitCombatTypes.NO_UNITCOMBAT],
"UnitClassTypes.NO_UNITCLASS": [UnitClassTypes.NO_UNITCLASS],
"UnitAITypes.UNITAI_WORKER": [UnitAITypes.UNITAI_WORKER],
"UnitAITypes.UNITAI_UNKNOWN": [UnitAITypes.UNITAI_UNKNOWN],
"UnitAITypes.UNITAI_SPY": [UnitAITypes.UNITAI_SPY],
"UnitAITypes.UNITAI_PROPHET": [UnitAITypes.UNITAI_PROPHET],
"UnitAITypes.UNITAI_GENERAL": [UnitAITypes.UNITAI_GENERAL],
"TerrainTypes.NO_TERRAIN": [TerrainTypes.NO_TERRAIN],
"TeamTypes.NO_TEAM": [TeamTypes.NO_TEAM],
"TaskTypes.TASK_LIBERATE": [TaskTypes.TASK_LIBERATE],
"TabGroupTypes.TABGROUP_GRAPHICS": [TabGroupTypes.TABGROUP_GRAPHICS],
"TabGroupTypes.TABGROUP_GAME": [TabGroupTypes.TABGROUP_GAME],
"TabGroupTypes.TABGROUP_CLOCK": [TabGroupTypes.TABGROUP_CLOCK],
"TabGroupTypes.TABGROUP_AUDIO": [TabGroupTypes.TABGROUP_AUDIO],
"RouteTypes.NO_ROUTE": [RouteTypes.NO_ROUTE],
"ReplayMessageTypes.REPLAY_MESSAGE_PLOT_OWNER_CHANGE": [ReplayMessageTypes.REPLAY_MESSAGE_PLOT_OWNER_CHANGE],
"ReligionTypes.NO_RELIGION": [ReligionTypes.NO_RELIGION],
"ProjectTypes.NO_PROJECT": [ProjectTypes.NO_PROJECT],
"ProcessTypes.NO_PROCESS": [ProcessTypes.NO_PROCESS],
"PlayerOptionTypes.PLAYEROPTION_NO_UNIT_RECOMMENDATIONS": [PlayerOptionTypes.PLAYEROPTION_NO_UNIT_RECOMMENDATIONS],
"PlayerOptionTypes.PLAYEROPTION_MODDER_3": [PlayerOptionTypes.PLAYEROPTION_MODDER_3],
"PlayerOptionTypes.PLAYEROPTION_MODDER_2": [PlayerOptionTypes.PLAYEROPTION_MODDER_2],
"MissionTypes.MISSION_SPREAD": [MissionTypes.MISSION_SPREAD],
"MissionTypes.MISSION_SLEEP": [MissionTypes.MISSION_SLEEP],
"MissionTypes.MISSION_RANGE_ATTACK": [MissionTypes.MISSION_RANGE_ATTACK],
"MissionTypes.MISSION_IDLE": [MissionTypes.MISSION_IDLE],
"MissionTypes.MISSION_HEAL": [MissionTypes.MISSION_HEAL],
"MissionTypes.MISSION_FOUND": [MissionTypes.MISSION_FOUND],
"MissionTypes.MISSION_FORTIFY": [MissionTypes.MISSION_FORTIFY],
"MissionTypes.MISSION_BOMBARD": [MissionTypes.MISSION_BOMBARD],
"MinimapModeTypes.MINIMAPMODE_TERRITORY": [MinimapModeTypes.MINIMAPMODE_TERRITORY],
"MemoryTypes.NUM_MEMORY_TYPES": [MemoryTypes.NUM_MEMORY_TYPES],
"MemoryTypes.MEMORY_EVENT_GOOD_TO_US": [MemoryTypes.MEMORY_EVENT_GOOD_TO_US],
"LeaderHeadTypes.NO_LEADER": [LeaderHeadTypes.NO_LEADER],
"InterfaceModeTypes.INTERFACEMODE_SELECTION": [InterfaceModeTypes.INTERFACEMODE_SELECTION],
"InputTypes.KB_W": [InputTypes.KB_W],
"InputTypes.KB_T": [InputTypes.KB_T],
"InputTypes.KB_SPACE": [InputTypes.KB_SPACE],
"InputTypes.KB_RIGHT": [InputTypes.KB_RIGHT],
"InputTypes.KB_RBRACKET": [InputTypes.KB_RBRACKET],
"InputTypes.KB_P": [InputTypes.KB_P],
"InputTypes.KB_LEFT": [InputTypes.KB_LEFT],
"InputTypes.KB_LBRACKET": [InputTypes.KB_LBRACKET],
"InputTypes.KB_F4": [InputTypes.KB_F4],
"InputTypes.KB_F3": [InputTypes.KB_F3],
"InputTypes.KB_F2": [InputTypes.KB_F2],
"InputTypes.KB_F1": [InputTypes.KB_F1],
"InputTypes.KB_7": [InputTypes.KB_7],
"InputTypes.KB_6": [InputTypes.KB_6],
"InputTypes.KB_5": [InputTypes.KB_5],
"InputTypes.KB_4": [InputTypes.KB_4],
"InputTypes.KB_3": [InputTypes.KB_3],
"InputTypes.KB_2": [InputTypes.KB_2],
"InputTypes.KB_1": [InputTypes.KB_1],
"InputTypes.KB_0": [InputTypes.KB_0],
"ImprovementTypes.NO_IMPROVEMENT": [ImprovementTypes.NO_IMPROVEMENT],
"HandicapTypes.NO_HANDICAP": [HandicapTypes.NO_HANDICAP],
"GraphicOptionTypes.GRAPHICOPTION_SINGLE_UNIT_GRAPHICS": [GraphicOptionTypes.GRAPHICOPTION_SINGLE_UNIT_GRAPHICS],
"GraphicOptionTypes.GRAPHICOPTION_HIRES_TERRAIN": [GraphicOptionTypes.GRAPHICOPTION_HIRES_TERRAIN],
"GraphicOptionTypes.GRAPHICOPTION_FULLSCREEN": [GraphicOptionTypes.GRAPHICOPTION_FULLSCREEN],
"GameOptionTypes.NUM_GAMEOPTION_TYPES": [GameOptionTypes.NUM_GAMEOPTION_TYPES],
"GameOptionTypes.GAMEOPTION_RANDOM_PERSONALITIES": [GameOptionTypes.GAMEOPTION_RANDOM_PERSONALITIES],
"GameOptionTypes.GAMEOPTION_PERMANENT_ALLIANCES": [GameOptionTypes.GAMEOPTION_PERMANENT_ALLIANCES],
"GameOptionTypes.GAMEOPTION_ALWAYS_PEACE": [GameOptionTypes.GAMEOPTION_ALWAYS_PEACE],
"FeatTypes.FEAT_POPULATION_5_MILLION": [FeatTypes.FEAT_POPULATION_5_MILLION],
"FeatTypes.FEAT_POPULATION_50_MILLION": [FeatTypes.FEAT_POPULATION_50_MILLION],
"FeatTypes.FEAT_POPULATION_500_MILLION": [FeatTypes.FEAT_POPULATION_500_MILLION],
"FeatTypes.FEAT_POPULATION_2_MILLION": [FeatTypes.FEAT_POPULATION_2_MILLION],
"FeatTypes.FEAT_POPULATION_20_MILLION": [FeatTypes.FEAT_POPULATION_20_MILLION],
"FeatTypes.FEAT_POPULATION_200_MILLION": [FeatTypes.FEAT_POPULATION_200_MILLION],
"FeatTypes.FEAT_POPULATION_1_MILLION": [FeatTypes.FEAT_POPULATION_1_MILLION],
"FeatTypes.FEAT_POPULATION_1_BILLION": [FeatTypes.FEAT_POPULATION_1_BILLION],
"FeatTypes.FEAT_POPULATION_10_MILLION": [FeatTypes.FEAT_POPULATION_10_MILLION],
"FeatTypes.FEAT_POPULATION_100_MILLION": [FeatTypes.FEAT_POPULATION_100_MILLION],
"EventContextTypes.EVENTCONTEXT_SELF": [EventContextTypes.EVENTCONTEXT_SELF],
"EntityEventTypes.ENTEVENT_MOVE": [EntityEventTypes.ENTEVENT_MOVE],
"DomainTypes.DOMAIN_HELICOPTER": [DomainTypes.DOMAIN_HELICOPTER],
"DirectionTypes.DIRECTION_WEST": [DirectionTypes.DIRECTION_WEST],
"DirectionTypes.DIRECTION_SOUTHWEST": [DirectionTypes.DIRECTION_SOUTHWEST],
"DirectionTypes.DIRECTION_SOUTHEAST": [DirectionTypes.DIRECTION_SOUTHEAST],
"DirectionTypes.DIRECTION_NORTHWEST": [DirectionTypes.DIRECTION_NORTHWEST],
"DirectionTypes.DIRECTION_NORTHEAST": [DirectionTypes.DIRECTION_NORTHEAST],
"DirectionTypes.DIRECTION_NORTH": [DirectionTypes.DIRECTION_NORTH],
"DirectionTypes.DIRECTION_EAST": [DirectionTypes.DIRECTION_EAST],
"DiplomacyPowerTypes.NUM_DIPLOMACYPOWER_TYPES": [DiplomacyPowerTypes.NUM_DIPLOMACYPOWER_TYPES],
"DiplomacyPowerTypes.DIPLOMACYPOWER_WEAKER": [DiplomacyPowerTypes.DIPLOMACYPOWER_WEAKER],
"DiplomacyPowerTypes.DIPLOMACYPOWER_STRONGER": [DiplomacyPowerTypes.DIPLOMACYPOWER_STRONGER],
"DiplomacyPowerTypes.DIPLOMACYPOWER_EQUAL": [DiplomacyPowerTypes.DIPLOMACYPOWER_EQUAL],
"DiploEventTypes.DIPLOEVENT_TARGET_CITY": [DiploEventTypes.DIPLOEVENT_TARGET_CITY],
"DiploEventTypes.DIPLOEVENT_STOP_TRADING": [DiploEventTypes.DIPLOEVENT_STOP_TRADING],
"DiploEventTypes.DIPLOEVENT_REVOLUTION": [DiploEventTypes.DIPLOEVENT_REVOLUTION],
"DiploEventTypes.DIPLOEVENT_RESEARCH_TECH": [DiploEventTypes.DIPLOEVENT_RESEARCH_TECH],
"DiploEventTypes.DIPLOEVENT_REJECTED_DEMAND": [DiploEventTypes.DIPLOEVENT_REJECTED_DEMAND],
"DiploEventTypes.DIPLOEVENT_REFUSED_HELP": [DiploEventTypes.DIPLOEVENT_REFUSED_HELP],
"DiploEventTypes.DIPLOEVENT_NO_STOP_TRADING": [DiploEventTypes.DIPLOEVENT_NO_STOP_TRADING],
"DiploEventTypes.DIPLOEVENT_NO_REVOLUTION": [DiploEventTypes.DIPLOEVENT_NO_REVOLUTION],
"DiploEventTypes.DIPLOEVENT_NO_JOIN_WAR": [DiploEventTypes.DIPLOEVENT_NO_JOIN_WAR],
"DiploEventTypes.DIPLOEVENT_NO_CONVERT": [DiploEventTypes.DIPLOEVENT_NO_CONVERT],
"DiploEventTypes.DIPLOEVENT_MADE_DEMAND_VASSAL": [DiploEventTypes.DIPLOEVENT_MADE_DEMAND_VASSAL],
"DiploEventTypes.DIPLOEVENT_MADE_DEMAND": [DiploEventTypes.DIPLOEVENT_MADE_DEMAND],
"DiploEventTypes.DIPLOEVENT_JOIN_WAR": [DiploEventTypes.DIPLOEVENT_JOIN_WAR],
"DiploEventTypes.DIPLOEVENT_GIVE_HELP": [DiploEventTypes.DIPLOEVENT_GIVE_HELP],
"DiploEventTypes.DIPLOEVENT_CONVERT": [DiploEventTypes.DIPLOEVENT_CONVERT],
"DiploEventTypes.DIPLOEVENT_ASK_HELP": [DiploEventTypes.DIPLOEVENT_ASK_HELP],
"DiploEventTypes.DIPLOEVENT_ACCEPT_DEMAND": [DiploEventTypes.DIPLOEVENT_ACCEPT_DEMAND],
"ControlTypes.CONTROL_YIELDS": [ControlTypes.CONTROL_YIELDS],
"ControlTypes.CONTROL_VICTORY_SCREEN": [ControlTypes.CONTROL_VICTORY_SCREEN],
"ControlTypes.CONTROL_UNIT_ICONS": [ControlTypes.CONTROL_UNIT_ICONS],
"ControlTypes.CONTROL_TURN_LOG": [ControlTypes.CONTROL_TURN_LOG],
"ControlTypes.CONTROL_TECH_CHOOSER": [ControlTypes.CONTROL_TECH_CHOOSER],
"ControlTypes.CONTROL_SCORES": [ControlTypes.CONTROL_SCORES],
"ControlTypes.CONTROL_RESOURCE_ALL": [ControlTypes.CONTROL_RESOURCE_ALL],
"ControlTypes.CONTROL_RELIGION_SCREEN": [ControlTypes.CONTROL_RELIGION_SCREEN],
"ControlTypes.CONTROL_PREVUNIT": [ControlTypes.CONTROL_PREVUNIT],
"ControlTypes.CONTROL_PREVCITY": [ControlTypes.CONTROL_PREVCITY],
"ControlTypes.CONTROL_NEXTUNIT": [ControlTypes.CONTROL_NEXTUNIT],
"ControlTypes.CONTROL_NEXTCITY": [ControlTypes.CONTROL_NEXTCITY],
"ControlTypes.CONTROL_MILITARY_SCREEN": [ControlTypes.CONTROL_MILITARY_SCREEN],
"ControlTypes.CONTROL_INFO": [ControlTypes.CONTROL_INFO],
"ControlTypes.CONTROL_GRID": [ControlTypes.CONTROL_GRID],
"ControlTypes.CONTROL_GLOBELAYER": [ControlTypes.CONTROL_GLOBELAYER],
"ControlTypes.CONTROL_FREE_COLONY": [ControlTypes.CONTROL_FREE_COLONY],
"ControlTypes.CONTROL_FOREIGN_SCREEN": [ControlTypes.CONTROL_FOREIGN_SCREEN],
"ControlTypes.CONTROL_FINANCIAL_SCREEN": [ControlTypes.CONTROL_FINANCIAL_SCREEN],
"ControlTypes.CONTROL_ESPIONAGE_SCREEN": [ControlTypes.CONTROL_ESPIONAGE_SCREEN],
"ControlTypes.CONTROL_DOMESTIC_SCREEN": [ControlTypes.CONTROL_DOMESTIC_SCREEN],
"ControlTypes.CONTROL_CORPORATION_SCREEN": [ControlTypes.CONTROL_CORPORATION_SCREEN],
"ControlTypes.CONTROL_CIVILOPEDIA": [ControlTypes.CONTROL_CIVILOPEDIA],
"ControlTypes.CONTROL_CIVICS_SCREEN": [ControlTypes.CONTROL_CIVICS_SCREEN],
"ControlTypes.CONTROL_BARE_MAP": [ControlTypes.CONTROL_BARE_MAP],
"CommandTypes.COMMAND_UPGRADE": [CommandTypes.COMMAND_UPGRADE],
"CommandTypes.COMMAND_PROMOTION": [CommandTypes.COMMAND_PROMOTION],
"CivilopediaPageTypes.CIVILOPEDIA_PAGE_MAIN": [CivilopediaPageTypes.CIVILOPEDIA_PAGE_MAIN],
"CivilizationTypes.NO_CIVILIZATION": [CivilizationTypes.NO_CIVILIZATION],
"CityTabTypes.NUM_CITYTAB_TYPES": [CityTabTypes.NUM_CITYTAB_TYPES],
"CardinalDirectionTypes.NUM_CARDINALDIRECTION_TYPES": [CardinalDirectionTypes.NUM_CARDINALDIRECTION_TYPES],
"ButtonPopupTypes.BUTTONPOPUP_DETAILS": [ButtonPopupTypes.BUTTONPOPUP_DETAILS],
"ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC": [ButtonPopupTypes.BUTTONPOPUP_CHANGECIVIC],
"AnimationPathTypes.ANIMATIONPATH_RUN": [AnimationPathTypes.ANIMATIONPATH_RUN],
"AdvancedStartActionTypes.ADVANCEDSTARTACTION_TECH": [AdvancedStartActionTypes.ADVANCEDSTARTACTION_TECH],
"ActivityTypes.ACTIVITY_SENTRY": [ActivityTypes.ACTIVITY_SENTRY],
"ActivityTypes.ACTIVITY_AWAKE": [ActivityTypes.ACTIVITY_AWAKE],
}


def replace_key_functions(fsource, ftarget):
    f = file(fsource, 'rU')
    f2 = file(ftarget, 'w')
    l = f.readline()
    while(l):
        # Ignore Lines without identation"
        if False:
        # if l[0] == "\t" or l[:2] == "  ":
            l2 = replaceLoop(l)
        else:
            l2 = l

        f2.write(l2)
        l = f.readline()

    f2.close()
    f.close()


def replaceLoop(codeline):
    out = codeline

    # check if single comment line
    if len(out[:out.find("#")].strip()) == 0:
        return out

    for fname in Constant_substitutions:
        tConst = Constant_substitutions[fname]
        out = out.replace(tConst[0], str(tConst[1]))

    for tname in Type_substitutions:
        tpos = 0  # Start index for multiple substitution candidates
        while tname in out[tpos:]:
            tpos = out.find(tname, tpos) + len(tname)
            if out[tpos:tpos+1] not in Type_varname_splitter:
                # Hey, tname is a real substring of the type name, i.e.
                # 'FooTypes.A' in 'FooTypes.ABC_DE'
                continue

            sType = str(Type_substitutions[tname][0])
            # import pdb; pdb.set_trace()
            tpos += (len(sType) - len(tname))  # Shrink
            out = out[:tpos-2] + sType + out[tpos-2+len(tname):]


    for fname in Replace_descriptors:
        if fname not in out:  # Skip most regex engine calls
            continue

        tDesc = Replace_descriptors[fname]  # Tuple
        matches = list(re.finditer(tDesc[0], out))
        if len(matches) == 0:
            continue

        out2 = ""
        prev_end = 0
        for m in matches:
            out2 += out[prev_end:m.start()]
            # Parse arg (currenty only one arg supported)
            arg1 = tDesc[2] % (m.group(tDesc[1]),)
            # Evaluate expression
            out2 += str(undefined_warner(tDesc[3], arg1))
            prev_end = m.end()

        out2 += out[prev_end:]
        out = out2

    return out


def main(forceUpdate=False, basedir=PyModPath, outdir=PyOutPath):

    # List of files, which already exists.
    target_files = glob.glob(outdir+"/*.py") +\
        glob.glob(outdir+"/*/*.py") + glob.glob(outdir+"/*/*/*.py")

    # Collection of files which should be parsed.
    # ("source path", timestamp_source, "target_path", timestamp_target)
    files = []

    # Map source file path to target file path and add timestamp.
    # This allows filtering of unchanged files
    # and filtering of double file (files with same target)
    # Note that basedir will vary.
    def addTargetTs(basedir, targets, s):
        t = s.replace(basedir, outdir, 1)
        if t in target_files:
            return (t, os.path.getctime(t))
        else:
            return (t, None)

    for basedir in SourceFolders:
        source_files = glob.glob(basedir+"/*.py") +\
            glob.glob(basedir+"/*/*.py") +\
            glob.glob(basedir+"/*/*/*.py")

        files.extend(
            [(x, os.path.getctime(x)) + addTargetTs(basedir, target_files, x)
             for x in source_files]
        )


    # Note that above list contain duplicates because some files exists at
    # multiple source folders. The duplicates had the same target paths.
    # We will just hold the latest instance.
    tmp = [(x[2], x) for x in files]
    files = dict(tmp).values()

    # Sort by timestamp, optional
    # files.sort(key=lambda xx: xx[1])
    # files = [files[10]]

    # Ignore this file due parsing
    this_file_name = __name__ + ".py"

    for tF in files:
        # Check if target file is newer as source file
        if(tF[3] is not None and tF[3] > tF[1] and not forceUpdate):
            print("Skip", tF[0])
            continue

        s = tF[0]
        t = tF[2]
        targetDir = t[:t.rfind(os.path.sep)]
        fname = t[t.rfind(os.path.sep)+1:]

        if fname == this_file_name:
            continue

        if not os.path.isdir(targetDir):
            os.makedirs(targetDir)

        print("Update '%s' -> '%s'" % (s, t))
        replace_key_functions(s, t)


if __name__ == "__main__":
    try:
        bForce = bool(int(sys.argv[1]))
    except:
        bForce = False

    main(bForce)
