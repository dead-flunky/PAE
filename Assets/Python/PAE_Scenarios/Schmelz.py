# Scenario SchmelzEuro/SchmelzWelt

# Imports
from CvPythonExtensions import *
# import CvEventInterface
import CvUtil
# import PyHelpers

# Defines
gc = CyGlobalContext()


IceSnow = []
IceCoast = []
IceTundra = []
IceTundra2 = []
IceEis = []
IceDesertEbene = []
IceDesertCoast = []


def onLoadGame(sScenarioName):
    global IceSnow
    global IceCoast
    global IceTundra
    global IceTundra2
    global IceEis
    global IceDesertEbene
    global IceDesertCoast

    eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
    eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
    #eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
    eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
    eEis = gc.getInfoTypeForString("FEATURE_ICE")
    eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
    #eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
    eDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")
    # ---------------- Schmelzen 2/4 (BoggyB) --------
    # Beim Neuladen (Felder aus 3/4 bleiben nicht gespeichert)
    for x in xrange(CyMap().getGridWidth()):
        for y in xrange(CyMap().getGridHeight()):
            pPlot = CyMap().plot(x, y)
            if pPlot.getTerrainType() == eDarkIce:
                continue
            elif pPlot.getTerrainType() == eSnow:
                IceSnow.append(pPlot)
            elif pPlot.getTerrainType() == eTundra:
                # Extra Tundra-Bereich, wos langsamer gehn soll
                if sScenarioName == "SchmelzEuro" and x >= 42 and y >= 49:
                    IceTundra2.append(pPlot)
                else:
                    IceTundra.append(pPlot)
            elif pPlot.getFeatureType() == eEis:
                IceEis.append(pPlot)
            # Ueberflutung
            if pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isHills() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1:
                if sScenarioName == "SchmelzEuro":
                    if y >= 28:
                        IceCoast.append(pPlot)
                else:
                    IceCoast.append(pPlot)
            # Desertifizierung
            if sScenarioName == "SchmelzEuro" and y <= 8:
                if pPlot.getTerrainType() == eEbene and not pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isRiver():
                    IceDesertEbene.append(pPlot)
                elif pPlot.getTerrainType() == eCoast and y <= 6 and x >= 2 and x <= 60:
                    IceDesertCoast.append(pPlot)


def onEndGameTurn(iGameTurn, sScenarioName):
    global IceSnow
    global IceCoast
    global IceTundra
    global IceTundra2
    global IceEis
    global IceDesertEbene
    global IceDesertCoast

    eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
    eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
    #eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
    eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
    eEis = gc.getInfoTypeForString("FEATURE_ICE")
    eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
    #eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
    eDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    if iGameTurn == 1:
        for x in xrange(CyMap().getGridWidth()):
            for y in xrange(CyMap().getGridHeight()):
                pPlot = CyMap().plot(x, y)
                if pPlot.getTerrainType() == eDarkIce:
                    continue
                if pPlot.getTerrainType() == eSnow:
                    IceSnow.append(pPlot)
                elif pPlot.getTerrainType() == eTundra:
                    # Extra Tundra-Bereich, wos langsamer gehn soll
                    if sScenarioName == "SchmelzEuro" and x >= 42 and y >= 49:
                        IceTundra2.append(pPlot)
                    else:
                        IceTundra.append(pPlot)
                elif pPlot.getFeatureType() == eEis:
                    IceEis.append(pPlot)
                # Ueberflutung
                if pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isHills() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1:
                    if sScenarioName == "SchmelzEuro":
                        if y >= 28:
                            IceCoast.append(pPlot)
                    else:
                        IceCoast.append(pPlot)
                # Desertifizierung
                if sScenarioName == "SchmelzEuro" and y <= 8:
                    if pPlot.getTerrainType() == eEbene and not pPlot.isCoastalLand() and not pPlot.isCity() and not pPlot.isRiver():
                        IceDesertEbene.append(pPlot)
                    elif pPlot.getTerrainType() == eCoast and y <= 6 and x >= 2 and x <= 60:
                        IceDesertCoast.append(pPlot)

    # ---------------- Schmelzen 4/4 (BoggyB)--------
    elif iGameTurn > 1:
        # Normal alle 40 Runden (insg. 940 Runden)
        # Schnell alle 32 Runden (insg. 770 Runden)
        # Episch alle 45 Runden (insg. 1095 Runden)
        # Marathon alle 52 Runden (insg. 1220 Runden)
        iTurnSchmelzIntervall = 40
        iTurnLimit = 800
        iGameSpeed = gc.getGame().getGameSpeedType()
        if iGameSpeed == gc.getInfoTypeForString("GAMESPEED_QUICK"):
            iTurnSchmelzIntervall = 32
            iTurnLimit = 600
        elif iGameSpeed == gc.getInfoTypeForString("GAMESPEED_EPIC"):
            iTurnSchmelzIntervall = 45
            iTurnLimit = 900
        elif iGameSpeed == gc.getInfoTypeForString("GAMESPEED_MARATHON"):
            iTurnSchmelzIntervall = 52
            iTurnLimit = 1000

        # ***TEST***
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Summe Eis",len(IceSnow))), None, 2, None, ColorTypes(10), 0, 0, False, False)

        if iGameTurn % iTurnSchmelzIntervall == 0 and iGameTurn <= iTurnLimit:
            iWahrscheinlichkeit = 8
            # if sScenarioName == "SchmelzWelt":
            #  iWahrscheinlichkeit = 8

            eTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
            eSnow = gc.getInfoTypeForString("TERRAIN_SNOW")
            eGras = gc.getInfoTypeForString("TERRAIN_GRASS")
            eEbene = gc.getInfoTypeForString("TERRAIN_PLAINS")
            eEis = gc.getInfoTypeForString("FEATURE_ICE")
            eCoast = gc.getInfoTypeForString("TERRAIN_COAST")
            eDesert = gc.getInfoTypeForString("TERRAIN_DESERT")

            # Schnee -> Tundra
            if IceSnow:
                for pPlot in IceSnow:
                    iRand = CvUtil.myRandom(iWahrscheinlichkeit, "IceSnow")
                    if iRand == 1:
                        pPlot.setTerrainType(eTundra, 1, 1)
                        IceSnow.remove(pPlot)
                        # Tundra Liste updaten
                        if sScenarioName == "SchmelzEuro" and pPlot.getX() >= 42 and pPlot.getY() >= 49:
                            IceTundra2.append(pPlot)
                        else:
                            IceTundra.append(pPlot)

            # Tundra -> Gras (25%) oder Ebene (75%)
            if IceTundra:
                for pPlot in IceTundra:
                    iRand = CvUtil.myRandom(iWahrscheinlichkeit, "IceTundra")
                    if iRand == 1:
                        iRand = CvUtil.myRandom(4, "IceTundraB")
                        if iRand == 1:
                            pPlot.setTerrainType(eGras, 1, 1)
                        else:
                            pPlot.setTerrainType(eEbene, 1, 1)
                        IceTundra.remove(pPlot)
            if IceTundra2:
                for pPlot in IceTundra2:
                    iRand = CvUtil.myRandom(iWahrscheinlichkeit*3, "IceTundra2")
                    if iRand == 1:
                        iRand = CvUtil.myRandom(4, "IceTundra2B")
                        if iRand == 1:
                            pPlot.setTerrainType(eGras, 1, 1)
                        else:
                            pPlot.setTerrainType(eEbene, 1, 1)
                        IceTundra2.remove(pPlot)

            # Eis schmilzt
            if IceEis:
                for pPlot in IceEis:
                    iRand = CvUtil.myRandom(iWahrscheinlichkeit, "IceEis")
                    if iRand == 1:
                        pPlot.setFeatureType(-1, 0)
                        IceEis.remove(pPlot)

            # Ueberflutung
            if IceCoast:
                for pPlot in IceCoast:
                    iRand = CvUtil.myRandom(50, "IceCoast")
                    if iRand == 1:
                        pPlot.setTerrainType(eCoast, 1, 1)
                        IceCoast.remove(pPlot)

            # Desertifizierung
            if sScenarioName == "SchmelzEuro":
                if IceDesertEbene:
                    for pPlot in IceDesertEbene:
                        iRand = CvUtil.myRandom(iWahrscheinlichkeit, "IceDesertEbene")
                        if iRand == 1:
                            pPlot.setTerrainType(eDesert, 1, 1)
                            pPlot.setImprovementType(-1)
                            IceDesertEbene.remove(pPlot)
                elif IceDesertCoast:
                    for pPlot in IceDesertCoast:
                        iRand = CvUtil.myRandom(iWahrscheinlichkeit, "IceDesertCoast")
                        if iRand == 1:
                            pPlot.setTerrainType(eEbene, 1, 1)
                            IceDesertCoast.remove(pPlot)
                            # Desert Liste updaten
                            IceDesertEbene.append(pPlot)
