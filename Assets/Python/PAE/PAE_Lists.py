#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Listen die an diversen Stellen für Vergleiche genutzt werden.
# Zur Unterscheidung von lokalen Variablen beginnen sie mit einem
# Großbuchstaben.
# Namenkonventionen: Vorne L/D für list/dict und danach meist der in der
#                    Liste verwendete Typ, z.B. 'Impr' für IMPROVMENT_XYZ
#
# Diese Datei sollte nur einmal, in CvUtil, importiert werden.
#

# Wrap definition of values into init() because during loading stage
# getInfoTypeForString() returns always -1
from CvPythonExtensions import CyGlobalContext
gc = CyGlobalContext()

# LTradeUnits = []
# LCultivationUnits = []
# LBonusCultivatable = []
# LBonusUntradeable = [] # List of untradeable bonuses
# LBonusCorn = [] # Lists of cultivatable bonuses
# LBonusLivestock = []
# LBonusPlantation = []
# LBonusLuxury = [] # List of bonuses which may create trade routes
# LBonusRarity = [] # List of bonuses which may create trade routes
# LUnitWarAnimals = []
# LUnitDomesticated = []
# LUnitLootLessSeaUnits = []
# LUnitCanBeDomesticated = []
# LUnitWildAnimals = []
# DJagd = {}
# LArcherCombats = []
# LMeleeCombats = []
# LMeleeSupplyCombats = []
# LMountedSupplyCombats = []
# LLimes = []
# LImprFort = []
# # LFeatureArray = []
# LImprFortShort = []
# DCaptureFromPirate = {}
# DCaptureByPirate = {}
# LFormationNoNaval = []
# LFormationMountedArcher = []
# LCivPirates = []
# LCivPartherschuss = []
# LUnitPartherschuss = []
# LKeilUnits = []
# LSchildwallUnits = []
# LDrillUnits = []
# LTestudoUnits = []
# LFluchtCombats = []
# LFormationen = []
# LUnitsNoAIReservists = []
# LUnitAuxiliar = []
# LUnitNoSlaves = []
# LCombatNoRuestung = []
# LUnitNoRuestung = []
# LUnitSkirmish = []
# LClassSkirmish = []
# LFernangriffNoCosts = []
# DFernangriffCosts = {}
# LSeewind = []
# LBuildArchers = []
# LBuildCatapults = []
# DManufakturen = {}
# DImprSupplyBonus = {}
# DBuildingPromo = {}
# DPromosForPromoBuilding = {}
# LLatifundien = []
# LFarms = []
# LMines = []
# LTemples = []
# LPromoPillage = []
# LWoodRemovedByLumberCamp = []
# LCityGarrison = []
# LVeteranForbiddenPromos1 = []
# LCityRaider = []
# LVeteranForbiddenPromos4 = []
# LCivGermanen = []
# DHorseDownMap = {}
# DHorseUpMap = {}
# LGGStandard = []
# DGGNames = {}
# # LRelis = []
# LGreeks = []
# LNearEast = []
# LNorthern = []
# LegioNames = []

def init():

    if gc.getInfoTypeForString("COLOR_EMPTY") == -1:
        raise Exception("Called init() to early. getInfoTypeForString() returns -1.")

    LTradeUnits = [
        gc.getInfoTypeForString("UNIT_TRADE_MERCHANT"),
        gc.getInfoTypeForString("UNIT_CARAVAN"),
        gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN"),
        gc.getInfoTypeForString("UNIT_GAULOS"),
        gc.getInfoTypeForString("UNIT_CARVEL_TRADE")
    ]
    LCultivationUnits = [gc.getInfoTypeForString("UNIT_SUPPLY_FOOD")]
    # Renegade Ausnahmen
    LUnitWarAnimals = [
        gc.getInfoTypeForString("UNIT_BEGLEITHUND"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"),
        gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"),
        gc.getInfoTypeForString("UNIT_BURNING_PIGS"),
    ]
    LUnitDomesticated = [
        gc.getInfoTypeForString("UNIT_HORSE"),
        gc.getInfoTypeForString("UNIT_CAMEL"),
        gc.getInfoTypeForString("UNIT_ELEFANT"),
    ]
    LUnitLootLessSeaUnits = [
        gc.getInfoTypeForString("UNIT_WORKBOAT"),
        gc.getInfoTypeForString("UNIT_TREIBGUT"),
        gc.getInfoTypeForString("UNIT_GAULOS"),
        gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN"),
    ]
    LUnitCanBeDomesticated = [
        gc.getInfoTypeForString("UNIT_WILD_HORSE"),
        gc.getInfoTypeForString("UNIT_WILD_CAMEL"),
        gc.getInfoTypeForString("UNIT_ELEFANT"),
    ]
    LUnitWildAnimals = [
        gc.getInfoTypeForString("UNIT_LION"),
        gc.getInfoTypeForString("UNIT_BEAR"),
        gc.getInfoTypeForString("UNIT_PANTHER"),
        gc.getInfoTypeForString("UNIT_WOLF"),
        gc.getInfoTypeForString("UNIT_BOAR"),
        gc.getInfoTypeForString("UNIT_TIGER"),
        gc.getInfoTypeForString("UNIT_LEOPARD"),
        gc.getInfoTypeForString("UNIT_DEER"),
        gc.getInfoTypeForString("UNIT_UR"),
        gc.getInfoTypeForString("UNIT_BERGZIEGE"),
    ]

    # Value = (iFoodMin, iFoodRand)
    DJagd = {
        None: (2, 2),  # Default for Lion, Wolf, etc. 2 - 3
        gc.getInfoTypeForString("UNIT_BOAR"): (5, 4),
        gc.getInfoTypeForString("UNIT_DEER"): (3, 4),
        gc.getInfoTypeForString("UNIT_WILD_CAMEL"): (3, 4),
        gc.getInfoTypeForString("UNIT_BEAR"): (4, 4),
        gc.getInfoTypeForString("UNIT_WILD_HORSE"): (4, 5),
        gc.getInfoTypeForString("UNIT_ELEFANT"): (6, 3)
    }

    LArcherCombats = [
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
        gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"),
    ]
    LMeleeCombats = [
        gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"),
    ]
    LMeleeSupplyCombats = LMeleeCombats+LArcherCombats

    LMountedSupplyCombats = [
        gc.getInfoTypeForString("UNITCOMBAT_CHARIOT"),
        gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"),
        gc.getInfoTypeForString("UNITCOMBAT_ELEPHANT"),
    ]
    LLimes = [
        gc.getInfoTypeForString("IMPROVEMENT_LIMES1"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES3"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES4"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES5"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES6"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES7"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES8"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES9"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_1"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_2"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_3"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_4"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_5"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_6"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_7"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_8"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_9"),
    ]

    LImprFort = [
        gc.getInfoTypeForString("IMPROVEMENT_TURM2"),
        gc.getInfoTypeForString("IMPROVEMENT_FORT"),
        gc.getInfoTypeForString("IMPROVEMENT_FORT2"),
        gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"),
    ]
    LImprFort.append(LLimes)

    # LFeatureArray = [
    #     gc.getInfoTypeForString("FEATURE_FOREST"),
    #     gc.getInfoTypeForString("FEATURE_DICHTERWALD"),
    # ]

    # Für Festungsformantion genutzt
    LImprFortShort = [
        gc.getInfoTypeForString("IMPROVEMENT_TURM2"),
        gc.getInfoTypeForString("IMPROVEMENT_FORT"),
        gc.getInfoTypeForString("IMPROVEMENT_FORT2"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES9"),
        gc.getInfoTypeForString("IMPROVEMENT_LIMES2_9"),
        gc.getInfoTypeForString("IMPROVEMENT_BARBARENFORT"),
    ]

    DCaptureFromPirate = {
        gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"): gc.getInfoTypeForString("UNIT_KONTERE"),
        gc.getInfoTypeForString("UNIT_PIRAT_BIREME"): gc.getInfoTypeForString("UNIT_BIREME"),
        gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"): gc.getInfoTypeForString("UNIT_TRIREME"),
        gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"): gc.getInfoTypeForString("UNIT_LIBURNE"),
    }
    DCaptureByPirate = dict((v, k) for k, v in DCaptureFromPirate.items())

    LFormationNoNaval = [
        gc.getInfoTypeForString("UNIT_WORKBOAT"),
        gc.getInfoTypeForString("UNIT_KILIKIEN"),
        gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"),
        gc.getInfoTypeForString("UNIT_PIRAT_BIREME"),
        gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"),
        gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"),
    ]
    LFormationMountedArcher = [
        gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"),
        gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),
    ]
    LCivPirates = [
        gc.getInfoTypeForString("CIVILIZATION_BERBER"),
        gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"),
        gc.getInfoTypeForString("CIVILIZATION_HETHIT"),
        gc.getInfoTypeForString("CIVILIZATION_IBERER"),
        gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"),
        gc.getInfoTypeForString("CIVILIZATION_LIBYA"),
        gc.getInfoTypeForString("CIVILIZATION_LYDIA"),
        gc.getInfoTypeForString("CIVILIZATION_NUBIA"),
        gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"),
        gc.getInfoTypeForString("CIVILIZATION_VANDALS"),
    ]
    LCivPartherschuss = [
        gc.getInfoTypeForString("CIVILIZATION_HETHIT"),
        gc.getInfoTypeForString("CIVILIZATION_PHON"),
        gc.getInfoTypeForString("CIVILIZATION_ISRAEL"),
        gc.getInfoTypeForString("CIVILIZATION_PERSIA"),
        gc.getInfoTypeForString("CIVILIZATION_BABYLON"),
        gc.getInfoTypeForString("CIVILIZATION_SUMERIA"),
        gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"),
        gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"),
        gc.getInfoTypeForString("CIVILIZATION_PARTHER"),
        gc.getInfoTypeForString("CIVILIZATION_HUNNEN"),
        gc.getInfoTypeForString("CIVILIZATION_INDIA"),
        gc.getInfoTypeForString("CIVILIZATION_BARBARIAN"),
    ]
    # Fast wie LFormationMountedArcher...
    LUnitPartherschuss = [
        #gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"),
        gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),
    ]
    LKeilUnits = [
        gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"),
        gc.getInfoTypeForString("UNIT_EQUITES"),
        gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2"),
        gc.getInfoTypeForString("UNIT_HORSEMAN_DECURIO"),
        gc.getInfoTypeForString("UNIT_LEGION_TRIBUN"),
        gc.getInfoTypeForString("UNIT_CATAPHRACT"),
        gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"),
        gc.getInfoTypeForString("UNIT_CLIBANARII"),
        gc.getInfoTypeForString("UNIT_CLIBANARII_ROME"),
        gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"),
        gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"),
        gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),
        gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"),
    ]
    LSchildwallUnits = [
        gc.getInfoTypeForString("UNIT_WARRIOR"),
        gc.getInfoTypeForString("UNIT_KURZSCHWERT"),
        gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"),
        gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"),
        gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
        gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
        gc.getInfoTypeForString("UNIT_AXEMAN"),
        gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"),
        gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"),
    ]
    LDrillUnits = [
        gc.getInfoTypeForString("UNIT_LEGION"),
        gc.getInfoTypeForString("UNIT_LEGION2"),
        gc.getInfoTypeForString("UNIT_LEGION_OPTIO"),
        gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"),
        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"),
        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN2"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN3"),
    ]
    LTestudoUnits = [
        gc.getInfoTypeForString("UNIT_LEGION"),
        gc.getInfoTypeForString("UNIT_LEGION2"),
        gc.getInfoTypeForString("UNIT_LEGION_OPTIO"),
        gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"),
        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"),
        gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN2"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN3"),
    ]
    LFluchtCombats = [
        gc.getInfoTypeForString("UNITCOMBAT_MELEE"),
        gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"),
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
        gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"),
    ]
    LFormationen = [
        gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL"),
        gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM"),    # TECH_CLOSED_FORM
        gc.getInfoTypeForString("PROMOTION_FORM_PHALANX"),        # TECH_PHALANX
        gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2"),       # TECH_PHALANX2
        gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF"),         # TECH_PHALANX2
        gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL"),        # TECH_MANIPEL
        gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN"),        # TECH_TREFFEN
        gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE"),        # TECH_MARIAN_REFORM
        gc.getInfoTypeForString("PROMOTION_FORM_KEIL"),           # TECH_HUFEISEN
        gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF"),  # TECH_HORSEBACK_RIDING_2
        gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ"),  # TECH_TREFFEN
        gc.getInfoTypeForString("PROMOTION_FORM_GASSE"),          # TECH_GEOMETRIE2
        gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO"),        # TECH_MARIAN_REFORM
        gc.getInfoTypeForString("PROMOTION_FORM_PARTHER"),
        gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS"),
        gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE"),        # TECH_BRANDSCHATZEN
        gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL"),     # TECH_LOGIK
        gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE"),    # TECH_LOGIK
        gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS"),
        gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2"),
    ]
    LUnitsNoAIReservists = [
        gc.getInfoTypeForString("UNIT_TRIARII2"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN2"),
        gc.getInfoTypeForString("UNIT_CELERES"),
        gc.getInfoTypeForString("UNIT_ARCHER_LEGION"),
        gc.getInfoTypeForString("UNIT_ELITE_HOPLIT"),
        gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"),
        gc.getInfoTypeForString("UNIT_SPARTAN"),
        gc.getInfoTypeForString("UNIT_UNSTERBLICH_2"),
        gc.getInfoTypeForString("UNIT_ARGYRASPIDAI"),
        gc.getInfoTypeForString("UNIT_ARGYRASPIDAI2"),
        gc.getInfoTypeForString("UNIT_PHARAONENGARDE"),
        gc.getInfoTypeForString("UNIT_GAUFUERST"),
        gc.getInfoTypeForString("UNIT_NUBIAFUERST"),
        gc.getInfoTypeForString("UNIT_MACCABEE"),
        gc.getInfoTypeForString("UNIT_STAMMESFUERST"),
        gc.getInfoTypeForString("UNIT_FUERST_DAKER"),
        gc.getInfoTypeForString("UNIT_GERMAN_HARIER"),
        gc.getInfoTypeForString("UNIT_RADSCHA"),
        gc.getInfoTypeForString("UNIT_INDIAN_NAYAR"),
        gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"),
        gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"),
        gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER")
    ]
    LUnitAuxiliar = [
        gc.getInfoTypeForString("UNIT_AUXILIAR"),
        gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"),
        gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON"),
    ]
    LUnitNoSlaves = LUnitWarAnimals
    LCombatNoRuestung = [
        gc.getInfoTypeForString("UNITCOMBAT_NAVAL"),
        gc.getInfoTypeForString("UNITCOMBAT_SIEGE"),
        gc.getInfoTypeForString("UNITCOMBAT_RECON"),
        gc.getInfoTypeForString("UNITCOMBAT_HEALER"),
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),
        -1,  # UnitCombatTypes.NO_UNITCOMBAT,
        # gc.getInfoTypeForString("NONE"),  # also -1
    ]
    LUnitNoRuestung = [
        gc.getInfoTypeForString("UNIT_WARRIOR"),
        gc.getInfoTypeForString("UNIT_AXEWARRIOR"),
        gc.getInfoTypeForString("UNIT_HUNTER"),
        gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"),
        gc.getInfoTypeForString("UNIT_KURZSCHWERT"),
        gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"),
        gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"),
        gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"),
        gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT"),
        gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"),
        gc.getInfoTypeForString("UNIT_MERC_HORSEMAN"),
        gc.getInfoTypeForString("UNIT_HORSEMAN"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER"),
        gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"),
    ]
    LUnitNoRuestung.extend(LUnitWarAnimals)

    LUnitSkirmish = [
        gc.getInfoTypeForString("UNIT_BALEAREN"),
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"),
        gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"),
        gc.getInfoTypeForString("UNIT_THRAKIEN_PELTAST"),
    ]
    LClassSkirmish = [
        gc.getInfoTypeForString("UNITCLASS_PELTIST"),
        gc.getInfoTypeForString("UNITCLASS_SKIRMISHER"),
        gc.getInfoTypeForString("UNITCLASS_CHARIOT_ARCHER"),
        gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER"),
        gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER"),
    ]
    LFernangriffNoCosts = [
        gc.getInfoTypeForString("CIVILIZATION_BERBER"),
        gc.getInfoTypeForString("CIVILIZATION_HUNNEN"),
        gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"),
    ]
    # Individuelle Kosten fuer iAirRange-Units
    DFernangriffCosts = {
        gc.getInfoTypeForString("UNITCLASS_HUNTER"): 0,
        gc.getInfoTypeForString("UNITCLASS_LIGHT_ARCHER"): 0,
        gc.getInfoTypeForString("UNITCLASS_ARCHER"): 1,
        gc.getInfoTypeForString("UNITCLASS_COMPOSITE_ARCHER"): 2,
        gc.getInfoTypeForString("UNIT_ARCHER_KRETA"): 2,
        gc.getInfoTypeForString("UNITCLASS_REFLEX_ARCHER"): 2,
        gc.getInfoTypeForString("UNITCLASS_ARCHER_LEGION"): 2,
        gc.getInfoTypeForString("UNIT_INDIAN_LONGBOW"): 3,
        gc.getInfoTypeForString("UNIT_LIBYAN_AMAZON"): 3,
        gc.getInfoTypeForString("UNITCLASS_PELTIST"): 2,
        gc.getInfoTypeForString("UNIT_BALEAREN"): 2,
        gc.getInfoTypeForString("UNITCLASS_SKIRMISHER"): 2,
        gc.getInfoTypeForString("UNIT_THRAKIEN_PELTAST"): 2,
        gc.getInfoTypeForString("UNITCLASS_CHARIOT_ARCHER"): 2,
        gc.getInfoTypeForString("UNIT_HETHIT_WARCHARIOT"): 2,
        gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"): 2,
        gc.getInfoTypeForString("UNIT_BAKTRIEN"): 2,
        gc.getInfoTypeForString("UNITCLASS_HORSE_ARCHER"): 2,
        gc.getInfoTypeForString("UNITCLASS_CAMEL_ARCHER"): 2,
        gc.getInfoTypeForString("UNIT_BALLISTA"): 2,
        gc.getInfoTypeForString("UNITCOMBAT_SIEGE"): 3,
        gc.getInfoTypeForString("UNIT_ROME_DECAREME"): 4,
    }

    LSeewind = [
        gc.getInfoTypeForString("FEATURE_WIND_N"),
        gc.getInfoTypeForString("FEATURE_WIND_NE"),
        gc.getInfoTypeForString("FEATURE_WIND_E"),
        gc.getInfoTypeForString("FEATURE_WIND_SE"),
        gc.getInfoTypeForString("FEATURE_WIND_S"),
        gc.getInfoTypeForString("FEATURE_WIND_SW"),
        gc.getInfoTypeForString("FEATURE_WIND_W"),
        gc.getInfoTypeForString("FEATURE_WIND_NW"),
    ]

    # Für UNITAI-Vergabe in onBuild
    LBuildArchers = [
        gc.getInfoTypeForString("UNIT_LIGHT_ARCHER"),
        gc.getInfoTypeForString("UNIT_ARCHER"),
        gc.getInfoTypeForString("UNIT_COMPOSITE_ARCHER"),
    ]
    LBuildCatapults = [
        gc.getInfoTypeForString("UNIT_ONAGER"),
        gc.getInfoTypeForString("UNIT_CATAPULT"),
        gc.getInfoTypeForString("UNIT_FIRE_CATAPULT"),
    ]

    # PAE Waffenmanufakturen - adds a second unit (PAE V Patch 4)
    DManufakturen = {
        gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"): gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_SCHWERT"),
        gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"): gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_AXT"),
        gc.getInfoTypeForString("UNITCOMBAT_ARCHER"): gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_BOGEN"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_SPEER"),
        gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"): gc.getInfoTypeForString("BUILDING_WAFFENMANUFAKTUR_SPEER"),
    }

    DImprSupplyBonus = {
        gc.getInfoTypeForString("IMPROVEMENT_FARM"): 50,
        gc.getInfoTypeForString("IMPROVEMENT_PASTURE"): 50,
        gc.getInfoTypeForString("IMPROVEMENT_PLANTATION"): 30,
        gc.getInfoTypeForString("IMPROVEMENT_BRUNNEN"): 20,
        gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"): 10,
        gc.getInfoTypeForString("IMPROVEMENT_HAMLET"): 15,
        gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"): 20,
        gc.getInfoTypeForString("IMPROVEMENT_TOWN"): 25,
        gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"): 25,
        gc.getInfoTypeForString("IMPROVEMENT_FORT"): 30,
        gc.getInfoTypeForString("IMPROVEMENT_FORT2"): 40,
    }

    DBuildingPromo = {
        gc.getInfoTypeForString("BUILDING_PROMO_FOREST"): gc.getInfoTypeForString("PROMOTION_WOODSMAN1"),
        gc.getInfoTypeForString("BUILDING_PROMO_HILLS"): gc.getInfoTypeForString("PROMOTION_GUERILLA1"),
        gc.getInfoTypeForString("BUILDING_PROMO_JUNGLE"): gc.getInfoTypeForString("PROMOTION_JUNGLE1"),
        gc.getInfoTypeForString("BUILDING_PROMO_SWAMP"): gc.getInfoTypeForString("PROMOTION_SUMPF1"),
        gc.getInfoTypeForString("BUILDING_PROMO_DESERT"): gc.getInfoTypeForString("PROMOTION_DESERT1"),
        gc.getInfoTypeForString("BUILDING_PROMO_CITY_A"): gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"),
        gc.getInfoTypeForString("BUILDING_PROMO_CITY_D"): gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"),
        gc.getInfoTypeForString("BUILDING_PROMO_PILLAGE"): gc.getInfoTypeForString("PROMOTION_PILLAGE1"),
        gc.getInfoTypeForString("BUILDING_PROMO_NAVI"): gc.getInfoTypeForString("PROMOTION_NAVIGATION1")
    }
    DPromosForPromoBuilding = {
        gc.getInfoTypeForString("PROMOTION_WOODSMAN5"): gc.getInfoTypeForString("BUILDING_PROMO_FOREST"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA5"): gc.getInfoTypeForString("BUILDING_PROMO_HILLS"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE5"): gc.getInfoTypeForString("BUILDING_PROMO_JUNGLE"),
        gc.getInfoTypeForString("PROMOTION_SUMPF5"): gc.getInfoTypeForString("BUILDING_PROMO_SWAMP"),
        gc.getInfoTypeForString("PROMOTION_DESERT5"): gc.getInfoTypeForString("BUILDING_PROMO_DESERT"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"): gc.getInfoTypeForString("BUILDING_PROMO_CITY_A"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5"): gc.getInfoTypeForString("BUILDING_PROMO_CITY_D"),
        gc.getInfoTypeForString("PROMOTION_PILLAGE5"): gc.getInfoTypeForString("BUILDING_PROMO_PILLAGE"),
        gc.getInfoTypeForString("PROMOTION_NAVIGATION4"): gc.getInfoTypeForString("BUILDING_PROMO_NAVI")
    }
    LLatifundien = [
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"),
        # gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5"),
    ]
    LFarms = [
        gc.getInfoTypeForString("IMPROVEMENT_PASTURE"),
        gc.getInfoTypeForString("IMPROVEMENT_FARM"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"),
        gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5"),
    ]
    LMines = [
        gc.getInfoTypeForString("IMPROVEMENT_MINE"),
        gc.getInfoTypeForString("IMPROVEMENT_QUARRY"),
    ]
    LTemples = [
        gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_ROME_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE"),
        gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE"),
    ]

    LPromoPillage = [
        gc.getInfoTypeForString("PROMOTION_PILLAGE1"),
        gc.getInfoTypeForString("PROMOTION_PILLAGE2"),
        gc.getInfoTypeForString("PROMOTION_PILLAGE3"),
        gc.getInfoTypeForString("PROMOTION_PILLAGE4"),
        gc.getInfoTypeForString("PROMOTION_PILLAGE5"),
    ]
    LWoodRemovedByLumberCamp = [
        gc.getInfoTypeForString("BUILD_REMOVE_JUNGLE"),
        gc.getInfoTypeForString("BUILD_REMOVE_FOREST"),
        gc.getInfoTypeForString("BUILD_REMOVE_FOREST_BURNT"),
    ]
    LGuerilla = [
        gc.getInfoTypeForString("PROMOTION_GUERILLA1"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA2"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA3"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA4"),
        gc.getInfoTypeForString("PROMOTION_GUERILLA5")
    ]
    LWoodsman = [
        gc.getInfoTypeForString("PROMOTION_WOODSMAN1"),
        gc.getInfoTypeForString("PROMOTION_WOODSMAN2"),
        gc.getInfoTypeForString("PROMOTION_WOODSMAN3"),
        gc.getInfoTypeForString("PROMOTION_WOODSMAN4"),
        gc.getInfoTypeForString("PROMOTION_WOODSMAN5")
    ]
    LJungle = [
        gc.getInfoTypeForString("PROMOTION_JUNGLE1"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE2"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE3"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE4"),
        gc.getInfoTypeForString("PROMOTION_JUNGLE5")
    ]
    LSwamp = [
        gc.getInfoTypeForString("PROMOTION_SUMPF1"),
        gc.getInfoTypeForString("PROMOTION_SUMPF2"),
        gc.getInfoTypeForString("PROMOTION_SUMPF3"),
        gc.getInfoTypeForString("PROMOTION_SUMPF4"),
        gc.getInfoTypeForString("PROMOTION_SUMPF5")
    ]
    LDesert = [
        gc.getInfoTypeForString("PROMOTION_DESERT1"),
        gc.getInfoTypeForString("PROMOTION_DESERT2"),
        gc.getInfoTypeForString("PROMOTION_DESERT3"),
        gc.getInfoTypeForString("PROMOTION_DESERT4"),
        gc.getInfoTypeForString("PROMOTION_DESERT5")
    ]
    LCityGarrison = [
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON2"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON3"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON4"),
        gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")
    ]
    LVeteranForbiddenPromos1 = [
        gc.getInfoTypeForString("PROMOTION_SKIRMISH1"),
        gc.getInfoTypeForString("PROMOTION_SKIRMISH2"),
        gc.getInfoTypeForString("PROMOTION_SKIRMISH3"),
    ]
    LCityRaider = [
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER2"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER3"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER4"),
        gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"),
    ]
    LVeteranForbiddenPromos4 = [
        gc.getInfoTypeForString("PROMOTION_RANG_ROM_1"),
        gc.getInfoTypeForString("PROMOTION_RANG_ROM_2"),
        gc.getInfoTypeForString("PROMOTION_RANG_ROM_3"),
        gc.getInfoTypeForString("PROMOTION_RANG_ROM_4"),
        gc.getInfoTypeForString("PROMOTION_RANG_ROM_5"),
    ]

    # Kelten, Germanen, Gallier, etc.
    LCivGermanen = [
        gc.getInfoTypeForString("CIVILIZATION_GERMANEN"),
        gc.getInfoTypeForString("CIVILIZATION_CELT"),
        gc.getInfoTypeForString("CIVILIZATION_GALLIEN"),
        gc.getInfoTypeForString("CIVILIZATION_DAKER"),
        gc.getInfoTypeForString("CIVILIZATION_BRITEN"),
        gc.getInfoTypeForString("CIVILIZATION_VANDALS"),
    ]

    # [Unitkey] => { [Civkey] => [Unitkey], None -> [Default Unitkey]}
    DHorseDownMap = {
        gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"): {
            None: gc.getInfoTypeForString("UNIT_AUXILIAR"),
            gc.getInfoTypeForString("CIVILIZATION_ROME"): gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"),
            gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"): gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"),
            gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"): gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON"),
        },
        gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"): {
            None: gc.getInfoTypeForString("UNIT_FOEDERATI"),
        },
        # gc.getInfoTypeForString('UNIT_PRAETORIAN_RIDER'): {
        #     None: gc.getInfoTypeForString('UNIT_PRAETORIAN'),
        # },
        gc.getInfoTypeForString('UNIT_MOUNTED_SACRED_BAND_CARTHAGE'): {
            None: gc.getInfoTypeForString('UNIT_SACRED_BAND_CARTHAGE'),
        },
        gc.getInfoTypeForString('UNIT_MOUNTED_SCOUT'): {
            None: gc.getInfoTypeForString("UNIT_SCOUT"),
            gc.getInfoTypeForString("CIVILIZATION_ATHENS"): gc.getInfoTypeForString("UNIT_SCOUT_GREEK"),
            gc.getInfoTypeForString("CIVILIZATION_GREECE"): gc.getInfoTypeForString("UNIT_SCOUT_GREEK"),
        },
    }

    DHorseUpMap = {
        "auxiliar": gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"),
        gc.getInfoTypeForString("UNIT_FOEDERATI"): gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"),
        # gc.getInfoTypeForString("UNIT_PRAETORIAN"): gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"),
        gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"): gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"),
        gc.getInfoTypeForString("UNIT_SCOUT"): gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"),
        gc.getInfoTypeForString("UNIT_SCOUT_GREEK"): gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"),
    }

    LGGStandard = [
        "Adiantunnus", "Divico", "Albion",
        "Malorix", "Inguiomer", "Archelaos",
        "Dorimachos", "Helenos", "Kerkidas",
        "Mikythos", "Philopoimen", "Pnytagoras",
        "Sophainetos", "Theopomopos", "Gylippos",
        "Proxenos", "Theseus", "Balakros",
        "Bar Kochba", "Julian ben Sabar", "Justasas",
        "Patricius", "Schimon bar Giora", "Artaphernes",
        "Harpagos", "Atropates", "Bahram Chobin",
        "Datis", "Schahin", "Egnatius",
        "Curius Aentatus", "Antiochos II", "Spartacus",
        "Herodes I", "Calgacus", "Suebonius Paulinus",
        "Maxentus", "Sapor II", "Alatheus",
        "Saphrax", "Honorius", "Aetius",
        "Achilles", "Herodes", "Heros",
        "Odysseus", "Anytos"]

    DGGNames = {
        gc.getInfoTypeForString("CIVILIZATION_ROME"):
        ["Agilo", "Marellus", "Flavius Theodosius",
         "Flavius Merobaudes", "Flavius Bauto", "Flavius Saturnius",
         "Flavius Fravitta", "Sextus Pompeius", "Publius Canidius Crassus",
         "Marcus Claudius Marellus", "Marcus Cato Censorius", "Flavius Felix",
         "Flavius Aetius", "Gnaeus Pompeius Strabo", "Ricimer",
         "Flavius Ardaburius Aspar", "Publius Quinctilius Varus", "Marcus Vispanius Agrippa",
         "Marcus Antonius Primus", "Tiberius Gracchus", "Petillius Cerialis",
         "Gaius Suetonius Paulimius", "Titus Labienus", "Gnaeus Iulius Verus",
         "Aulus Allienus", "Marcellinus", "Flavius Castinus",
         "Lucius Fannius", "Aulus Didius Gallus", "Rufio",
         "Publius Servilius Rullus", "Papias"],
        gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
        ["Lars Tolumnius", "Lucius Tarquinius Priscus", "Arrunte Tarquinius",
         "Celio Vibenna", "Elbio Vulturreno", "Arrunte Porsena",
         "Tito Tarquinius", "Aulus Caecina Alienus", "Mezentius",
         "Aulus Caecina Severerus", "Sextus Tarquinius", "Velthur Spurinna"],
        gc.getInfoTypeForString("CIVILIZATION_CELT"):
        ["Ortiagon", "Adiatunnus", "Boduognatus",
         "Indutiomarus", "Catuvolcus", "Deiotaros",
         "Viridomarus", "Chiomara", "Voccio",
         "Kauaros", "Komontorios"],
        gc.getInfoTypeForString("CIVILIZATION_GALLIEN"):
        ["Vergobret", "Viridovix", "Acco",
         "Amandus", "Camulogenus", "Postumus",
         "Aelianus", "Capenus", "Tibatto",
         "Julias Classicus", "Diviciacus"],
        gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
        ["Valamir", "Athaulf ", "Eurich",
         "Sigerich", "Walia", "Julius Civilis",
         "Malorix", "Edekon", "Vestralp",
         "Chnodomar", "Agenarich", "Ardarich",
         "Verritus", "Thuidimir", "Gundioch",
         "Priarius", "Kniva", "Radagaisus",
         "Alaviv", "Athanarich", "Hunulf",
         "Hunimund", "Rechiar", "Rechila",
         "Cannabaudes", "Eriulf", "Adovacrius",
         "Gundomad", "Hariobaud", "Hortar",
         "Suomar", "Marcomer", "Gennobaudes",
         "Sunno", "Merogaisus", "Segimer",
         "Inguiomer", "Vadomar", "Ascaricus",
         "Ursicinus", "Arbogast"],
        gc.getInfoTypeForString("CIVILIZATION_DAKER"):
        ["Cotisone", "Oroles", "Duras",
         "Rubobostes", "Dromichaetes", "Rholes",
         "Zyraxes", "Dapys", "Fastida",
         "Zenon"],
        gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"):
        ["Bardylis", "Glaukias", "Monunios II",
         "Skerdilaidas", "Bato I", "Demetrios Pharos",
         "Pleuratos I", "Sirras", "Bato II",
         "Epulon", "Longarus", "Pinnes Pannonien",
         "Cleitus", "Bardylis II", "Genthios"],
        gc.getInfoTypeForString("CIVILIZATION_GREECE"):
        ["Adeimantos", "Xenokleides", "Timonides Leukas",
         "Pyrrhias", "Philopoimen", "Milon",
         "Leosthenes", "Kineas", "Dorimachos",
         "Daochos I", "Ameinias", "Herakleides",
         "Panares", "Lasthenes", "Onomarchus",
         "Menon Pharsalos", "Timoleon", "Hermokrates",
         "Archytas Tarent", "Keridas"],
        gc.getInfoTypeForString("CIVILIZATION_ATHENS"):
        ["Konon", "Miltiades", "Perikles",
         "Leon", "Menon", "Aristeides",
         "Autokles", "Chares", "Eukrates",
         "Hippokrates", "Kallistratos", "Thrasyllos",
         "Timomachos", "Xanthippos", "Xenophon",
         "Demosthenes", "Anytos"],
        gc.getInfoTypeForString("CIVILIZATION_THEBAI"):
        ["Kleomenes Boeotarich", "Pagondas", "Pelopidas",
         "Proxenos", "Coeratadas", "Gorgidas",
         "Peisis Thespiai", "Theagenes Boeotarich", "Apollokrates",
         "Polyxenos"],
        gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
        ["Brasidas", "Eurybiades", "Klearchos",
         "Xanthippos", "Mindaros", "Peisander",
         "Therimenes", "Thibron", "Agesilaos",
         "Gylippos", "Astyochos", "Aiantides Milet",
         "Antalkidas", "Archidamos II", "Aristodemos",
         "Chalkideus", "Derkylidas", "Euryanax",
         "Eurylochos", "Hippokrates Sparta", "Kallikratidas",
         "Phoibidas", "Cheirisophos"],
        gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
        ["Admetos", "Attalos", "Antipatros",
         "Antigonos", "Antigenes", "Demetrios Althaimenes",
         "Gorgias", "Herakon", "Karanos",
         "Kleitos", "Memnon", "Nikanor",
         "Parmenion", "Philippos", "Pleistarchos",
         "Meleagros", "Menidas", "Menandros",
         "Telesphoros", "Demetrios I Poliorketes", "Adaios Alektryon",
         "Alexandros", "Koinos", "Zopyrion"],
        gc.getInfoTypeForString("CIVILIZATION_HETHIT"):
        ["Pithana", "Anitta", "Labarna",
         "Mursili I", "Hantili I", "Arnuwanda II",
         "Muwattalli II", "Suppiluliuma II", "Kantuzzili",
         "Kurunta"],
        gc.getInfoTypeForString("CIVILIZATION_LYDIA"):
        ["Ardys II", "Sadyattes II", "Gyges",
         "Paktyes", "Mazares", "Myrsus",
         "Lydus", "Manes", "Agron",
         "Meles"],
        gc.getInfoTypeForString("CIVILIZATION_PHON"):
        ["Luli", "Abdi-Milkutti", "Straton I",
         "Tabnit", "Abd-Melqart", "Azemilkos",
         "Baal I", "Ithobaal III", "Elukaios",
         "Baal II", "Panam-muwa II", "Esmun-ezer"],
        gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"):
        ["Adherbal", "Bomilkar", "Hannibal Gisko",
         "Boodes", "Hamilkar", "Mago",
         "Maharbal", "Hanno", "Himilkon",
         "Gisco", "Hannibal Bomilkars", "Hasdrubal Cartagagena",
         "Hasdrubal Barkas", "Hasdrubal Hannos", "Hasdrubal Gisco",
         "Mago Barkas", "Malchus"],
        gc.getInfoTypeForString("CIVILIZATION_ISRAEL"):
        ["Bar Kochbar", "Jonathan", "Judas Makkabaeus",
         "Justasas", "Schimon bar Giora", "Simon Makkabaeus",
         "Johann Gischala", "Barak", "Patricius",
         "Abner", "Scheba", "Jaobs",
         "Benaja", "Omri", "Jeha",
         "Goliath"],
        gc.getInfoTypeForString("CIVILIZATION_SUMERIA"):
        ["Agga", "Ur-Nammu", "Gudea",
         "Eanatum", "Amar-Sin", "Sulgi",
         "Utuhengal", "Lugalbanda", "Enuk-duanna",
         "Rim-Anum", "Ibbi-Sin"],
        gc.getInfoTypeForString("CIVILIZATION_BABYLON"):
        ["Sumu-abum", "Sumulael", "Sabium",
         "Hammurapi", "Eriba-Marduk", "Burna-burias I",
         "Neriglissar", "Abi-esuh", "Nergalscharrussar",
         "Ulamburiasch", "Musezib-Marduk", "Bel-simanni",
         "Agum III", "Marduk-apla-iddina II", "Nabu-nasir",
         "Bel-ibni"],
        gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"):
        ["Dajan-Assur", "Samsi-ilu", "Sin-sumu-lisir",
         "Assur-bela-ka-in", "Bel-lu-Ballet", "Nergal-ilaya",
         "Nabu-da-inannil", "Inurta-ilaya", "Tustanu",
         "Schanabuschu", "Assur-dan I", "Assur-nirari V",
         "Eriba-Adad I", "Assur-dan II", "Sanherib",
         "Asarhaddon"],
        gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
        ["Artaphernes", "Artasyras", "Shahrbaraz",
         "Harpagos", "Mardonios", "Xenias Parrhasia",
         "Otanes Sisamnes", "Tissaphernes", "Hydarnes",
         "Pharnabazos II", "Tithraustes",
         "Smerdomenes", "Tritantaichmes", "Tiribazos",
         "Megabazos", "Megabates", "Artabozos I",
         "Pharnabazos III", "Pherendates", "Abrokomas",
         "Atropates", "Datis", "Satibarzanes",
         "Oxyathres", "Struthas"],
        gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
        ["Ahmose", "Djehuti", "Ahmose Pennechbet",
         "Antef", "Seti", "Psammetich I",
         "Sib-e", "Ramses III", "Psammetich III",
         "Merenptah", "Haremhab", "Amasis",
         "Amenemhab", "Re-e", "Djefaihap",
         "Kanefer"],
        gc.getInfoTypeForString("CIVILIZATION_NUBIA"):
        ["Kaschta", "Pije", "Schabaka",
         "Schabataka", "Tanotamun", "Aspelta",
         "Pekartror", "Harsijotef", "Charamadoye",
         "Cheperkare"],
        gc.getInfoTypeForString("CIVILIZATION_IBERER"):
        ["Mandonio", "Caro Segeda", "Megara",
         "Olindico", "Culcas", "Gauson",
         "Hilerno", "Istolacio", "Luxinio",
         "Punico", "Besadino", "Budar",
         "Edecon", "Indortes"],
        gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"):
        ["Gauda", "Gulussa", "Matho",
         "Tacfarinas", "Syphax", "Hiempsal I",
         "Micipsa", "Arabion", "Suburra",
         "Mastanabal"],
        gc.getInfoTypeForString("CIVILIZATION_BERBER"):
        ["Masties", "Lusius Quietus", "Firmus",
         "Gildon", "Quintus Lollius Urbicus", "Sabalus",
         "Bagas", "Bogud", "Bocchus II",
         "Lucius Balbus Minor"],
        gc.getInfoTypeForString("CIVILIZATION_LIBYA"):
        ["Osorkon II", "Namilt I", "Iupet",
         "Osochor", "Paschedbastet", "Namilt II",
         "Takelot II", "Petubastis I", "Osorkon III",
         "Bakenntah"],
        gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"):
        ["Idanthyrsos", "Maues", "Satrakes",
         "Skilurus", "Scopasis", "Palacus",
         "Madius", "Eunones", "Octamasadas",
         "Azes I"],
        gc.getInfoTypeForString("CIVILIZATION_HUNNEN"):
        ["Balamir", "Dengizich", "Ellac",
         "Oktar", "Rua", "Uldin",
         "Kursisch""Hormidac", "Ernak", "Charaton"],
        gc.getInfoTypeForString("CIVILIZATION_INDIA"):
        ["Pushyamitra Shunga", "Kujula Kadphises", "Chandragupta II",
         "Samudragupta", "Kharavela", "Skandagupta",
         "Dhana Nanda", "Vidudabha", "Vishvamitra",
         "Bimbisara", "Ajatashatru", "Bindusara",
         "Kanishka", "Vima Kadphises", "Soter Megas"],
        gc.getInfoTypeForString("CIVILIZATION_BRITEN"):
        ["Cassivelanaunus", "Cingetorix", "Carvillius",
         "Taximagulus", "Segovax", "Ambrosius Aurelius",
         "Hengest", "Horsa", "Vortigern",
         "Riothamus", "Venutius", "Togodumnus",
         "Allectus", "Nennius", "Calgacus"],
        gc.getInfoTypeForString("CIVILIZATION_PARTHER"):
        ["Surena", "Artabanus V", "Vologase I",
         "Vologase IV", "Phraates IV", "Osreos I",
         "Phraates II", "Pakoros I", "Artabanus IV",
         "Barzapharnes", "Pharnapates"],
        gc.getInfoTypeForString("CIVILIZATION_VANDALS"):
        ["Godigisel", "Gunderich", "Gunthamund",
         "Gento", "Thrasamund", "Hoamer",
         "Wisimar", "Flavius Stilicho",
         "Andevoto", "Hilderich"]
    }

    # # Religionen
    # LRelis = [
    #     gc.getInfoTypeForString("RELIGION_HINDUISM"),
    #     gc.getInfoTypeForString("RELIGION_BUDDHISM"),
    #     gc.getInfoTypeForString("RELIGION_JUDAISM"),
    #     gc.getInfoTypeForString("RELIGION_CHRISTIANITY"),
    #     gc.getInfoTypeForString("RELIGION_JAINISMUS"),
    # ]

    LGreeks = [
        gc.getInfoTypeForString("CIVILIZATION_GREECE"),
        gc.getInfoTypeForString("CIVILIZATION_ATHENS"),
        gc.getInfoTypeForString("CIVILIZATION_THEBAI"),
        gc.getInfoTypeForString("CIVILIZATION_SPARTA")
    ]
    LNearEast = [
        gc.getInfoTypeForString("CIVILIZATION_PHON"),
        gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"),
        gc.getInfoTypeForString("CIVILIZATION_BABYLON"),
        gc.getInfoTypeForString("CIVILIZATION_ISRAEL"),
        gc.getInfoTypeForString("CIVILIZATION_SUMERIA")
    ]
    LNorthern = [
        gc.getInfoTypeForString("CIVILIZATION_CELT"),
        gc.getInfoTypeForString("CIVILIZATION_GALLIEN"),
        gc.getInfoTypeForString("CIVILIZATION_BRITEN"),
        gc.getInfoTypeForString("CIVILIZATION_GERMANEN")
    ]
    LegioNames = [
        "Legio I Adiutrix", "Legio I Germanica", "Legio I Italica",
        "Legio I Macriana Liberatrix", "Legio I Minervia", "Legio I Parthica",
        "Legio II Adiutrix", "Legio II Augusta", "Legio II Italica",
        "Legio II Parthica", "Legio II Traiana Fortis", "Legio III Augusta",
        "Legio III Cyrenaica", "Legio III Gallica", "Legio III Italica",
        "Legio III Parthica", "Legio III Macedonica", "Legio IV Flavia Felix",
        "Legio IV Scythica", "Legio V Alaudae", "Legio V Macedonica",
        "Legio VI Ferrata", "Legio VI Victrix", "Legio VII Claudia",
        "Legio VII Gemina", "Legio VIII Augusta", "Legio IX Hispana",
        "Legio X Fretensis", "Legio X Equestris", "Legio XI Claudia",
        "Legio XII Fulminata", "Legio XIII Gemina", "Legio XIV Gemina",
        "Legio XV Apollinaris", "Legio XV Primigenia", "Legio XVI Gallica",
        "Legio XVI Flavia Firma", "Legio XVII", "Legio XVIII",
        "Legio XIX", "Legio XX Valeria Victrix", "Legio XXI Rapax",
        "Legio XXII Deiotariana", "Legio XXII Primigenia", "Legio X"+"XX Ulpia Victrix",
        "Legio I Iulia Alpina", "Legio I Armeniaca", "Legio I Flavia Constantia",
        "Legio I Flavia Gallicana", "Legio I Flavia Martis", "Legio I Flavia Pacis",
        "Legio I Illyricorum", "Legio I Iovia", "Legio I Isaura Sagitaria",
        "Legio I Martia", "Legio I Maximiana", "Legio I Noricorum",
        "Legio I Pontica", "Legio II Iulia Alpina", "Legio II Armeniaca",
        "Legio II Brittannica", "Legio II Flavia Virtutis", "Legio II Herculia",
        "Legio II Isaura", "Legio III Iulia Alpina", "Legio III Diocletiana",
        "Legio III Flavia Salutis", "Legio III Herculia", "Legio III Isaura",
        "Legio IV Italica", "Legio IV Martia", "Legio IV Parthica",
        "Legio V Iovia", "Legio V Parthica", "Legio VI Gallicana",
        "Legio VI Herculia", "Legio VI Hispana", "Legio VI Parthica",
        "Legio XII Victrix", "Legio Thebaica",
    ]

    # BonusClass indices
    eGrain = gc.getInfoTypeForString("BONUSCLASS_GRAIN") # WHEAT, GERSTE, HAFER, ROGGEN, HIRSE, RICE
    eLivestock = gc.getInfoTypeForString("BONUSCLASS_LIVESTOCK") # COW, PIG, SHEEP
    ePlantation = gc.getInfoTypeForString("BONUSCLASS_PLANTATION") # GRAPES, OLIVES, DATTELN
    eGeneral = gc.getInfoTypeForString("BONUSCLASS_GENERAL") # COAL (Blei), ZINN, ZINK, ZEDERNHOLZ, COPPER, BRONZE, IRON, MESSING, HORSE, CAMEL, HUNDE, PAPYRUS_PAPER
    eLuxury = gc.getInfoTypeForString("BONUSCLASS_LUXURY") # GOLD, SILVER, PEARL, LION, SALT, DYE, FUR, INCENSE, MYRRHE, IVORY, SPICES, WINE, MUSIC
    eRarity = gc.getInfoTypeForString("BONUSCLASS_RARITY") # MAGNETIT, OBSIDIAN, OREICHALKOS, GLAS, BERNSTEIN, ELEKTRON, WALRUS, GEMS, SILK, SILPHIUM, TERRACOTTA
    eWonder = gc.getInfoTypeForString("BONUSCLASS_WONDER") # MARBLE, STONE
    # eMisc =  gc.getInfoTypeForString("BONUSCLASS_MISC") # BANANA, CRAB, DEER, FISH, CLAM, PAPYRUS
    # eMerc =  gc.getInfoTypeForString("BONUSCLASS_MERCENARY") # BALEAREN, TEUTONEN, BAKTRIEN, KRETA, KILIKIEN, MARS, THRAKIEN

    iNumBonuses = gc.getNumBonusInfos()
    LBonusCorn = []
    LBonusLivestock = []
    LBonusPlantation = []
    LBonusLuxury = []
    LBonusRarity = []
    LBonusUntradeable = []
    for eBonus in range(iNumBonuses):
        pBonusInfo = gc.getBonusInfo(eBonus)
        iClass = pBonusInfo.getBonusClassType()
        if iClass == eGrain:
            LBonusCorn.append(eBonus)
        elif iClass == eLivestock:
            LBonusLivestock.append(eBonus)
        elif iClass == ePlantation:
            LBonusPlantation.append(eBonus)
        elif iClass == eLuxury:
            LBonusLuxury.append(eBonus)
        elif iClass == eRarity:
            LBonusRarity.append(eBonus)
        # eg BONUSCLASS_MISC
        elif iClass != eWonder and iClass != eGeneral:
            LBonusUntradeable.append(eBonus)
        # BonusClass wonder and general are not stored separately (bc. unnecessary)

    LBonusCultivatable = LBonusCorn + LBonusLivestock + LBonusPlantation + [gc.getInfoTypeForString("BONUS_HORSE")]

    # Tranfer local defined variables into module ones.
    lnames = [l for l in locals().keys() if l[0] != "_" and l != "gc"]
    for l in lnames:
        globals()[l] = locals()[l]
