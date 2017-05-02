# Disasters features and events

### Imports
from CvPythonExtensions import *
import random

import PAE_City
import PAE_Unit

### Defines
gc = CyGlobalContext()

def myRandom (num):
      if num <= 1: return 0
      else: return random.randint(0, num-1)

### Entrypoint
def doGenerateDisaster(iGameTurn):

    if iGameTurn == 0: return

    iTurnDisastersModulo = 80
    bApocalypse = False
    if gc.getPlayer(gc.getGame().getActivePlayer()).getName() == "Apocalypto":
        iTurnDisastersModulo = 20
        bApocalypse = True

    if gc.getGame().getGameTurnYear() > -600 and iGameTurn % 25 == 0: doNebel()

    # Teiler
    if gc.getGame().getGameTurnYear() > -400: iTeiler = 2
    else: iTeiler = 1

    # entweder Erdbeben, Comet, Meteore oder Vulkan

    # Katas erzeugen
    if iGameTurn % (iTurnDisastersModulo / iTeiler) == 0:
        iRand = myRandom(5)
        if iRand == 0: doErdbeben(0,0)
        elif iRand == 1: doVulkan(0,0,0)
        elif iRand == 2: doComet()
        else: doMeteorites()

    # Warnung aussenden
    elif (iGameTurn + 1) % (iTurnDisastersModulo / iTeiler) == 0:
        iBuilding1 = gc.getInfoTypeForString("BUILDINGCLASS_ORACLE")
        iBuilding2 = gc.getInfoTypeForString("BUILDINGCLASS_ORACLE2")
        iRange = gc.getMAX_PLAYERS()
        i=0
        for i in range (iRange):
            loopPlayer = gc.getPlayer(i)
            if loopPlayer.isHuman():
                iChance = 0
                if loopPlayer.getBuildingClassCount(iBuilding1) > 0: iChance = 100
                elif loopPlayer.getBuildingClassCount(iBuilding2) > 0: iChance = 50
                if iChance > 0 and iChance > myRandom(100):
                    # Player gets warning message
                    CyInterface().addMessage(i, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_ORACLE_WARNING",("",)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    if bApocalypse:
        if iGameTurn % (85 / iTeiler) == 0: doSeesturm()
        if iGameTurn % (90 / iTeiler) == 0: doGrasshopper()
        if iGameTurn % (60 / iTeiler) == 0: doTornado()
    elif iGameTurn % (70 / iTeiler) == 0:
        iRand = myRandom(2)
        if iRand == 0: doSeesturm()
        elif iRand == 1: doGrasshopper()
        else: doTornado()

    if iGameTurn % (90 / iTeiler) == 0: doSandsturm()

    if iGameTurn % ((iTurnDisastersModulo / iTeiler) + 20) == 0: undoVulkan()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++ Naturkatastrophen / Disasters +++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def doSandsturm():

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_desertstorm = gc.getInfoTypeForString('FEATURE_FALLOUT')

      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
      terr_coast = gc.getInfoTypeForString('TERRAIN_COAST')

      improv1 = gc.getInfoTypeForString('IMPROVEMENT_FORT')
      improv2 = gc.getInfoTypeForString('IMPROVEMENT_FORT2')
      improv3 = gc.getInfoTypeForString('IMPROVEMENT_TURM2')

      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      elif iMapSize < 5: iMax = 3
      else: iMax = 5

      # 20 Versuche max. iMax Sandstuerme zu kreieren
      for i in range (20):

        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_oasis and pPlot.getFeatureType() != feat_flood_plains and pPlot.getTerrainType() == terr_desert and not pPlot.isPeak():
            OwnerArray = []
            iMaxEffect += 1
            for i in range(3):
              for j in range(5):
                # An den aeusseren Sturmgrenzen etwas auflockern
                if j == 0 or j == 4: iSetStorm = myRandom(2)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if (not (loopPlot.isWater() or loopPlot.isPeak()) and loopPlot.getTerrainType() == terr_desert and loopPlot.getFeatureType() != feat_oasis and loopPlot.getFeatureType() != feat_flood_plains) or loopPlot.getTerrainType() == terr_coast:
                      if loopPlot.getImprovementType() != improv1 and loopPlot.getImprovementType() != improv2 and loopPlot.getImprovementType() != improv3:
                        if loopPlot.getRouteType() == 0 and not loopPlot.isCity(): loopPlot.setRouteType(-1)
                        if loopPlot.getImprovementType() != gc.getInfoTypeForString('IMPROVEMENT_MINE'): loopPlot.setImprovementType(-1)
                      loopPlot.setFeatureType(feat_desertstorm,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_DESERTSTORM",("",)),None,2,gc.getFeatureInfo(feat_desertstorm).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

        # Maximal iMax Stuerme
        if iMaxEffect == iMax: break

def doGrasshopper():

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_grasshopper = gc.getInfoTypeForString('FEATURE_GRASSHOPPER')

      lFeatures = []
      lFeatures.append(gc.getInfoTypeForString('FEATURE_JUNGLE'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_SAVANNA'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FOREST'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_DICHTERWALD'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FOREST_BURNT'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_OASIS'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS'))
      lFeatures.append(gc.getInfoTypeForString('FEATURE_SEUCHE'))

      terr_desert = gc.getInfoTypeForString('TERRAIN_DESERT')
      terr_plains = gc.getInfoTypeForString('TERRAIN_PLAINS')

      improv1 = gc.getInfoTypeForString('IMPROVEMENT_FORT')
      improv2 = gc.getInfoTypeForString('IMPROVEMENT_FORT2')
      improv3 = gc.getInfoTypeForString('IMPROVEMENT_TURM2')

      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      elif iMapSize < 5: iMax = 2
      else: iMax = 4

      # 10 Versuche max. 4 Heuschreckenplagen zu kreieren
      for i in range (10):

        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() not in lFeatures and not pPlot.isPeak() \
          and (pPlot.getTerrainType() == terr_desert or pPlot.getTerrainType() == terr_plains):
            OwnerArray = []
            iMaxEffect += 1
            for i in range(3):
              for j in range(5):
                # An den aeusseren Grenzen etwas auflockern
                if j == 0 or j == 4: iSetStorm = myRandom(2)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if not (loopPlot.isWater() or loopPlot.isPeak()) and loopPlot.getFeatureType() not in lFeatures \
                    and (loopPlot.getTerrainType() == terr_desert or loopPlot.getTerrainType() == terr_plains):
                      if loopPlot.getImprovementType() != improv1 and loopPlot.getImprovementType() != improv2 and loopPlot.getImprovementType() != improv3:
                        if loopPlot.getImprovementType() != gc.getInfoTypeForString("IMPROVEMENT_MINE") and loopPlot.getImprovementType() != gc.getInfoTypeForString("IMPROVEMENT_QUARRY"):
                          loopPlot.setImprovementType(-1)
                      loopPlot.setFeatureType(feat_grasshopper,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_GRASSHOPPERS",("",)),None,2,gc.getFeatureInfo(feat_grasshopper).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

        # Maximal iMax Heuschreckenplagen
        if iMaxEffect == iMax: break

def doNebel():

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_nebel = gc.getInfoTypeForString('FEATURE_NEBEL')
      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')

      terr_ocean = gc.getInfoTypeForString('TERRAIN_OCEAN')
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize < 3: iMax = 1
      else: iMax = 3

      # 10 Versuche max. iMax Nebel zu kreieren
      for i in range (10):

        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_ice and pPlot.getTerrainType() == terr_ocean:
            OwnerArray = []
            iMaxEffect += 1
            for i in range(10):
              for j in range(7):
                # An den aeusseren Grenzen etwas auflockern
                if i == 0 or i == 9 or j == 0 or j == 6: iSetStorm = myRandom(3)
                elif i == 1 or i == 8 or j == 1 or j == 5: iSetStorm = myRandom(2)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_ocean:
                      loopPlot.setFeatureType(feat_nebel,0)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_NEBEL",("",)),None,2,gc.getFeatureInfo(feat_nebel).getButton(),ColorTypes(14),iRandX,iRandY,True,True)

        # Maximal 3 Nebeldecken
        if iMaxEffect == iMax: break

def doSeesturm():

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      feat_seesturm = gc.getInfoTypeForString('FEATURE_SEESTURM')
      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')

      terr_coast = gc.getInfoTypeForString('TERRAIN_COAST')
      terr_ocean = gc.getInfoTypeForString('TERRAIN_OCEAN')
      iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
      iMaxEffect = 0
      iMapSize = gc.getMap().getWorldSize()
      if iMapSize == 0: iMax = 1
      elif iMapSize == 1: iMax = 2
      elif iMapSize == 2: iMax = 2
      elif iMapSize == 3: iMax = 3
      elif iMapSize == 4: iMax = 3
      elif iMapSize == 5: iMax = 4
      else: iMax = 5

      # 20 Versuche max. iMax Seestuerme zu kreieren
      for i in range (20):

        # Maximal 5 Seestuerme
        if iMaxEffect == iMax: break

        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)

        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

          if pPlot.getFeatureType() == iDarkIce: continue
          if pPlot.getFeatureType() != feat_ice and pPlot.getTerrainType() == terr_coast or pPlot.getTerrainType() == terr_ocean:
            OwnerArray = []
            iMaxEffect += 1
            for i in range(8):
              for j in range(5):
                # An den aeusseren Grenzen etwas auflockern
                if i == 0 or i == 7 or j == 0 or j == 4: iSetStorm = myRandom(2)
                else: iSetStorm = 1
                # Sturm setzen
                if iSetStorm == 1:
                  loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 2)
                  if None != loopPlot and not loopPlot.isNone():
                    if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() == terr_coast or loopPlot.getTerrainType() == terr_ocean:
                      if loopPlot.getImprovementType() > -1:
                        loopPlot.setImprovementType(-1)
                        if loopPlot.getOwner() > -1:
                          if gc.getPlayer(loopPlot.getOwner()).isHuman():
                            CyInterface().addMessage(gc.getPlayer(loopPlot.getOwner()).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_SEESTURM_FISCHERBOOT",("",)),None,2,gc.getFeatureInfo(feat_seesturm).getButton(),ColorTypes(7),loopPlot.getX(),loopPlot.getY(),True,True)
                      loopPlot.setFeatureType(feat_seesturm,0)
                      doKillUnits(pPlot, 10)
                  # Besitzer herausfinden
                  if loopPlot.getOwner() != -1 and loopPlot.getOwner() not in OwnerArray:
                    OwnerArray.append(loopPlot.getOwner())

            # Sturmmeldung an die Plot-Besitzer
            iRange = len(OwnerArray)
            for i in range (iRange):
              if gc.getPlayer(OwnerArray[i]).isHuman():
                CyInterface().addMessage(gc.getPlayer(OwnerArray[i]).getID(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_SEESTURM",("",)),None,2,gc.getFeatureInfo(feat_seesturm).getButton(),ColorTypes(7),iRandX,iRandY,True,True)


def doTornado():
    iMaxEffect = 0

    feat_tornado = gc.getInfoTypeForString('FEATURE_TORNADO')
    feat_sturm = gc.getInfoTypeForString('FEATURE_STURM')
    feat_seesturm = gc.getInfoTypeForString('FEATURE_SEESTURM')

    feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
    iMapSize = gc.getMap().getWorldSize()
    if iMapSize == 0: iMax = 1
    elif iMapSize == 1: iMax = 2
    elif iMapSize == 2: iMax = 3
    elif iMapSize == 3: iMax = 4
    elif iMapSize == 4: iMax = 5
    elif iMapSize == 5: iMax = 6
    else: iMax = 7

    # 10 Versuche fuer max. iMax Tornados
    for i in range (10):

        # Maximal iMax Effekte
        if iMaxEffect == iMax: break

        iMapW = gc.getMap().getGridWidth()
        iMapH = gc.getMap().getGridHeight()

        iRandX = myRandom(iMapW)
        iRandY = myRandom(iMapH)
        pPlot = gc.getMap().plot(iRandX, iRandY)
        if None != pPlot and not pPlot.isNone():

         if pPlot.getFeatureType() == iDarkIce: continue
         if not pPlot.isPeak():
          if pPlot.getFeatureType() != feat_flood_plains and pPlot.getFeatureType() != feat_oasis:
            iMaxEffect += 1
            if not pPlot.isCity(): pPlot.setRouteType(-1)
            pPlot.setImprovementType(-1)
            pPlot.setFeatureType(feat_tornado,0)

            iPlayer = pPlot.getOwner()
            pOwner = gc.getPlayer(iPlayer)

            if iPlayer != -1:

              if pPlot.isVisibleToWatchingHuman(): CyCamera().JustLookAtPlot(pPlot)

              if gc.getPlayer(iPlayer).isHuman():
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_TORNADO",("", )))
                popupInfo.addPopup(iPlayer)
                CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO",("",)),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

            if pPlot.isCity():
              pCity = pPlot.getPlotCity()
              iPop_alt = pCity.getPopulation()
              iPop_neu = int(pCity.getPopulation() / 2)
              if iPop_neu < 1: iPop_neu = 1
              pCity.setPopulation(iPop_neu)
              if iPlayer != -1:
                if gc.getPlayer(iPlayer).isHuman() and pPlot.isVisibleToWatchingHuman():
                  if gc.getPlayer(iPlayer).isHuman():
                    CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
                  else:
                    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_TORNADO_CITY_OTHER",(pOwner.getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_tornado).getButton(),ColorTypes(2),iRandX,iRandY,True,True)
              # City, Wahrscheinlichkeit in %
              doDestroyCityBuildings(pCity,25)
              doKillUnits(pPlot, 10)
              PAE_City.doCheckCityState(pCity)

            # rundherum Sturm kreieren
            for i in range(3):
              for j in range(3):
                loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
                if None != loopPlot and not loopPlot.isNone():
                  if loopPlot.getFeatureType() == iDarkIce: continue
                  if loopPlot.getFeatureType() == -1 and not loopPlot.isPeak():
                    if loopPlot.isWater(): loopPlot.setFeatureType(feat_seesturm,0)
                    else: loopPlot.setFeatureType(feat_sturm,0)


def doErdbeben(iX, iY):
    # Effekt
    earthquakeEffect = gc.getInfoTypeForString("EFFECT_RES_BOMB")
    bonusPlotArray = []

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    # Effekt beim Vulkanausbruch
    if iX > 0 and iY > 0:
      CyEngine().triggerEffect( earthquakeEffect, gc.getMap().plot(iX, iY).getPoint() )

    else:

      feat_erdbeben = gc.getInfoTypeForString('FEATURE_ERDBEBEN')
      feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

      feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
      feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
      feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
      feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

      feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
      terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')

      # Staerkegrad des Erdbebens 6 - 9
      # 6 - Radius 1: Modernisierungen 60%, Stadt: Gebaeude 15%, Units 10%
      # 7 - Radius 1: Modernisierungen 70%, Stadt: Gebaeude 30%, Units 30%, -2 Pop, Land: Units 10%
      # 8 - Radius 2: Modernisierungen 80%
      #               Epi + 1:  Stadt: Gebaeude 50%, Units 50%, Pop / 2,   Land: Units 20%
      #               Radius 2: Stadt: Gebaeude 30%, Units 30%, Pop - 1/3, Land: Units 10%
      # 9 - Radius 3: Modernisierungen 90%
      #               Epi + 1: Pop < 6: Stadt und Units 100%,
      #                        Pop > 5: 3/4 Pop weg, Gebaeude 80%, Wunder 50%, Units 80%
      #                        Land: Units 40%
      #               Radius 2: Pop / 2, Stadt:   Gebaeude 60%, Units 60%, Land: Units 30%
      #               Radius 3: Pop - 1/3, Stadt: Gebaeude 40%, Units 40%, Land: Units 20%
      iSkala = 6 + myRandom(4)

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      # Plot soll nicht ganz am Rand sein (Flunky: alle 4 Raender ausnehmen)
      iRandX = 3 + myRandom(iMapW - 6)
      iRandY = 3 + myRandom(iMapH - 6)
      pPlot = gc.getMap().plot(iRandX, iRandY)
      iPlayer = pPlot.getOwner()

      if None != pPlot and not pPlot.isNone():
       if not pPlot.isWater() and pPlot.getFeatureType() != iDarkIce:
        if pPlot.isVisibleToWatchingHuman(): CyCamera().JustLookAtPlot(pPlot)
        # ERDBEBEN 6, 7
        if iSkala < 8:
          if iPlayer != -1:
            if gc.getPlayer(iPlayer).isHuman():
              # Message: Ein gewaltiges Erdbeben der Staerke %d erschuettert Euer Land!
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_6_OR_7",(iSkala,0)))
              popupInfo.addPopup(iPlayer)
              CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_6_OR_7",(iSkala,0)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  pCity.setFood(0)
                  if iSkala == 6:
                    doDestroyCityBuildings(pCity, 15)
                    doKillUnits(loopPlot, 10)
                  else:
                    doDestroyCityBuildings(pCity, 30)
                    doKillUnits(loopPlot, 30)
                    iPopAlt = pCity.getPopulation()
                    iPopNeu = 0
                    if iPopAlt > 4: iPopNeu = iPopAlt - 2
                    elif iPopAlt > 2: iPopNeu = iPopAlt - 1
                    else: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)

                    if iPopNeu and iPlayer != -1:
                      if gc.getPlayer(iPlayer).isHuman():
                        # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                        CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  PAE_City.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = myRandom(10)
                  if iSkala == 6:
                    iLimit = 6
                  else:
                    iLimit = 7
                    doKillUnits(loopPlot, 10)
                  if iRand < iLimit:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                      if myRandom(3) == 1: loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)

        # ERDBEBEN 8
        elif iSkala == 8:

          if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
            if pPlot.isVisibleToWatchingHuman():
              CyCamera().JustLookAtPlot(pPlot)
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte das Land.
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8",("",)))
              popupInfo.addPopup(gc.getGame().getActivePlayer())
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            else:
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte ein fernes Land.
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_8_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(5):
            for j in range(5):
              loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPopAlt = pCity.getPopulation()
                  if iBetrag < 2:
                    doDestroyCityBuildings(pCity, 50)
                    doKillUnits(loopPlot, 50)
                    iPopNeu = int(iPopAlt / 2)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    doDestroyCityBuildings(pCity, 30)
                    doKillUnits(loopPlot, 30)
                    iPopNeu = iPopAlt - int(iPopAlt / 3)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  PAE_City.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = myRandom(10)
                  if iRand < 8:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                      if myRandom(2) == 1: loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: doKillUnits(loopPlot, 20)
                  else: doKillUnits(loopPlot, 10)

        # ERDBEBEN 9
        elif iSkala > 8:

          if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
            if pPlot.isVisibleToWatchingHuman():
              CyCamera().JustLookAtPlot(pPlot)
              # Message: Ein katastrophales Erdbeben der Staerke 9 erschuetterte das Land.
              popupInfo = CyPopupInfo()
              popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
              popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9",("",)))
              popupInfo.addPopup(gc.getGame().getActivePlayer())
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
            else:
              # Message: Ein verheerendes Erdbeben der Staerke 8 erschuetterte ein fernes Land.
              CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_9_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

          for i in range(7):
            for j in range(7):
              loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater(): CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Plot fuer Bonus Resource checken
                # Vergabe unten
                if not loopPlot.isWater() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and not loopPlot.isPeak() and loopPlot.isHills():
                   bonusPlotArray.append(loopPlot)

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPopAlt = pCity.getPopulation()
                  if iBetrag < 2:
                    if iPopAlt < 6:
                      doDestroyCityWonders(pCity, 100, feat_erdbeben)
                      doKillUnits(loopPlot, 100)
                      pCity.kill()
                      if gc.getPlayer(iPlayer).isHuman():
                        # Message: Die Stadt %s und dessen Bevoelkerung wurde in ihren Truemmern begraben....
                        CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_EARTHQUAKE_CITY_DESTROYED",(pCity.getName(),)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)
                    else:
                      doDestroyCityWonders(pCity, 50, feat_erdbeben)
                      doDestroyCityBuildings(pCity, 80)
                      doKillUnits(loopPlot, 80)
                      iPopNeu = int(iPopAlt / 4)
                      pCity.setPopulation(iPopNeu)
                  elif iBetrag < 3:
                    doDestroyCityBuildings(pCity, 60)
                    doKillUnits(loopPlot, 60)
                    iPopNeu = int(iPopAlt / 2)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    doDestroyCityBuildings(pCity, 40)
                    doKillUnits(loopPlot, 40)
                    iPopNeu = iPopAlt - int(iPopAlt / 3)
                    if iPopNeu < 2: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)


                  if not pCity.isNone() and iPlayer != -1:
                    pCity.setFood(0)
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_erdbeben).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  if pCity: PAE_City.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                elif not loopPlot.isWater():
                  iRand = myRandom(100)
                  if iRand < 90:
                    loopPlot.setRouteType(-1)
                    loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: doKillUnits(loopPlot, 40)
                  elif iBetrag < 3: doKillUnits(loopPlot, 30)
                  else: doKillUnits(loopPlot, 20)


        # Vergabe einer Bonus Resource 20%
        if len(bonusPlotArray) > 0:
          if 2 > myRandom(10):
            lBonus = []
            lBonus.append(gc.getInfoTypeForString("BONUS_GEMS"))
            lBonus.append(gc.getInfoTypeForString("BONUS_COPPER"))
            lBonus.append(gc.getInfoTypeForString("BONUS_IRON"))
            lBonus.append(gc.getInfoTypeForString("BONUS_MARBLE"))
            lBonus.append(gc.getInfoTypeForString("BONUS_STONE"))
            lBonus.append(gc.getInfoTypeForString("BONUS_OBSIDIAN"))
            lBonus.append(gc.getInfoTypeForString("BONUS_MAGNETIT"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ZINK"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ZINN"))
            lBonus.append(gc.getInfoTypeForString("BONUS_COAL"))
            lBonus.append(gc.getInfoTypeForString("BONUS_ELEKTRON"))
            lBonus.append(gc.getInfoTypeForString("BONUS_GOLD"))
            lBonus.append(gc.getInfoTypeForString("BONUS_SILVER"))
            lBonus.append(gc.getInfoTypeForString("BONUS_SALT"))
            iRand = myRandom(len(lBonus))
            iBonus = lBonus[iRand]

            iRandPlot = myRandom(len(bonusPlotArray))
            bonusPlotArray[iRandPlot].setBonusType(iBonus)
            if bonusPlotArray[iRandPlot].getOwner() > -1:
              if gc.getPlayer(bonusPlotArray[iRandPlot].getOwner()).isHuman():
                CyInterface().addMessage(bonusPlotArray[iRandPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iBonus).getDescription(),)), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(14), bonusPlotArray[iRandPlot].getX(), bonusPlotArray[iRandPlot].getY(), True, True)


        # Zusaetzliche Gefahren durch das Erdbeben

        # Vulkan
        if pPlot.isPeak() and iSkala > 7:
          doVulkan(iRandX, iRandY, iSkala)

       # Unterwassererdbeben
       elif iSkala > 8:

         # Testen ob es ein Ozean ist
         iNumWaterTiles = 0
         for i in range(5):
           for j in range(5):
             loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
             if None != loopPlot and not loopPlot.isNone():
               if loopPlot.getFeatureType() == iDarkIce: continue
               if loopPlot.isWater(): iNumWaterTiles += 1
         # Statt dem Erbeben wird ein Tsunami zum Leben erweckt
         if iNumWaterTiles > 9:
           doTsunami(iRandX, iRandY)


def doVulkan(iX, iY, iSkala):

    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    # iX, iY und iSkala vom Feature Erbeben: iSkala 8 oder 9
    # Wenn das nicht gegeben ist, einen eigenen Vulkanausbruch erzeugen
    if iSkala == 0:
      iSkala = 8 + myRandom(2)

      iMapW = gc.getMap().getGridWidth()
      iMapH = gc.getMap().getGridHeight()

      # 10 Versuche einen Berg ausfindig zu machen
      for i in range (10):
        # Plot soll nicht ganz am Rand sein (Flunky: alle 4 Raender ausnehmen)
        iRandX = 3 + myRandom(iMapW - 6)
        iRandY = 3 + myRandom(iMapH - 6)
        if gc.getMap().plot(iRandX, iRandY).isPeak():
          iX = iRandX
          iY = iRandY
          break

    if iX > 0 and iY > 0:
      pPlot = gc.getMap().plot(iX, iY)

      terr_peak   = gc.getInfoTypeForString("TERRAIN_PEAK")
      terr_tundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
      terr_coast  = gc.getInfoTypeForString("TERRAIN_COAST")
      feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")
      feat_brand  = gc.getInfoTypeForString("FEATURE_SMOKE")
      feat_saurer_regen = gc.getInfoTypeForString("FEATURE_SAURER_REGEN")

      feat_flood_plains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
      feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

      feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
      feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
      feat_jungle = gc.getInfoTypeForString('FEATURE_JUNGLE')
      feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

      bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
      bonus_obsidian = gc.getInfoTypeForString("BONUS_OBSIDIAN")
      bonusPlotArray = []

      if pPlot.isPeak():
        pPlot.setPlotType (PlotTypes.PLOT_LAND,True,True)
        pPlot.setTerrainType(terr_tundra,1,1)

      pPlot.setFeatureType(feat_vulkan,0)

      # Meldungen -----
      # Staerke 1
      if iSkala == 8:
        if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
          if pPlot.isVisibleToWatchingHuman():
            CyCamera().JustLookAtPlot(pPlot)
            # Message: Ein verheerender Vulkanausbruch legt das Land in Schutt und Asche.
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_1",("",)))
            popupInfo.addPopup(gc.getGame().getActivePlayer())
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_1",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

      # Staerke 2
      else:
        if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
          if pPlot.isVisibleToWatchingHuman():
            CyCamera().JustLookAtPlot(pPlot)
            # Message: Ein katastrophaler Vulkanausbruch legt das Land in Schutt und Asche.
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2",("",)))
            popupInfo.addPopup(gc.getGame().getActivePlayer())
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2",("",)), "AS2D_EARTHQUAKE", 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)
          else:
            # Message: Ein katastrophaler Vulkanausbruch legt ein fernes Land in Schutt und Asche.
            CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_2_FAR_AWAY",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(12), pPlot.getX(), pPlot.getY(), True, True)

      # Staerke 1 (iSkala 8): 1 Plot Radius
      #   Stadt: Pop / 2, Gebaeude 50%, Units 50%
      #   Land:  Units 25%
      #   Feature: Sauerer Regen: Umkreis von 5 Plots

      # Staerke 2 (iSkala 9): 2 Plots Radius
      #   Radius 1:
      #     Stadt: Pop = 1/4, Gebaeude 75%, Units 75%
      #     Land:  Units 50%
      #   Radius 2:
      #     Stadt: Pop / 2, Gebaeude 50%, Units 50%
      #     Land:  Units 25%
      #   Feature: Sauerer Regen: Umkreis von 1 Plot, Ellipse nach Osten oder Westen: 15 Plots

      iRandX = iX
      iRandY = iY

      # Effekt
      earthquakeEffect = gc.getInfoTypeForString("EFFECT_RES_BOMB")
      volcanoEffect = gc.getInfoTypeForString("EFFECT_OMEN_HORSEMAN")
      CyEngine().triggerEffect( volcanoEffect, pPlot.getPoint() )

      PlayerPopUpFood = []

      # Staerke 1
      if iSkala == 8:

          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater() and i != 1 and j != 1: CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Entfernung zum Epizentrum berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPlayer = pCity.getOwner()
                  iPopAlt = pCity.getPopulation()

                  doDestroyCityBuildings(pCity, 50)
                  doKillUnits(loopPlot, 50)
                  iPopNeu = int(iPopAlt / 2)
                  if iPopNeu < 2: iPopNeu = 1
                  pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  PAE_City.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                else:
                  loopPlot.setRouteType(-1)
                  loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isWater() and not loopPlot.isPeak():
                   if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_vulkan and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else: loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  doKillUnits(loopPlot, 25)

                # Plot fuer Bonus checken
                # Vergabe ganz unten
                if not loopPlot.isWater() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1 and loopPlot.isHills():
                  bonusPlotArray.append(loopPlot)

                # Dem Plot +1 Nahrung geben (25%)
                if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and not (i==1 and j==1):
                 if loopPlot.getFeatureType != feat_vulkan and loopPlot.getTerrainType() != terr_tundra:
                  if myRandom(4) == 1:
                    gc.getGame().setPlotExtraYield(iRandX - 2 + i, iRandY - 2 + j, 0, 1) # x,y,YieldType,iChange
                    iOwner = loopPlot.getOwner()
                    if iOwner != -1:
                     if gc.getPlayer(iOwner).isHuman():
                      CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)
                      # fuer spaeteres popup
                      if gc.getPlayer(iOwner).getID() not in PlayerPopUpFood: PlayerPopUpFood.append(gc.getPlayer(iOwner).getID())

                # Verbreitbare Resi vernichten
                if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                  doEraseBonusFromDisaster(loopPlot)

          # Sauerer Regen
          for i in range(7):
            for j in range(7):
              loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                #loopPlot.setRouteType(-1)
                if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                and loopPlot.getFeatureType() != feat_brand and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak():
                  if loopPlot.getFeatureType() != feat_forest_burnt:
                    loopPlot.setFeatureType(feat_saurer_regen,0)


      # Staerke 2
      else:

          for i in range(5):
            for j in range(5):
              loopPlot = gc.getMap().plot(iRandX - 2 + i, iRandY - 2 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if not loopPlot.isWater() and i != 2 and j != 2: CyEngine().triggerEffect( earthquakeEffect, loopPlot.getPoint() )

                # Entfernung zum Vulkan berechnen
                iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())

                # Stadt
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  iPlayer = pCity.getOwner()
                  iPopAlt = pCity.getPopulation()

                  if iBetrag < 2:
                    doDestroyCityBuildings(pCity, 75)
                    doKillUnits(loopPlot, 75)
                    iPopNeu = int(iPopAlt / 4)
                    if iPopNeu < 1: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  else:
                    doDestroyCityBuildings(pCity, 50)
                    doKillUnits(loopPlot, 50)
                    iPopNeu = iPopAlt - int(iPopAlt / 2)
                    if iPopNeu < 1: iPopNeu = 1
                    pCity.setPopulation(iPopNeu)
                  pCity.setFood(0)

                  if iPlayer != -1:
                    if gc.getPlayer(iPlayer).isHuman():
                      # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

                  PAE_City.doCheckCityState(pCity)

                # Modernisierungen zerstoeren
                else:
                  loopPlot.setRouteType(-1)
                  loopPlot.setImprovementType(-1)
                  # Brand setzen
                  if not loopPlot.isWater() and loopPlot.getFeatureType() != feat_flood_plains \
                  and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak() and loopPlot.getFeatureType() != feat_oasis:
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else: loopPlot.setFeatureType(feat_brand,0)
                  # Units killen
                  if iBetrag < 2: doKillUnits(loopPlot, 50)
                  else: doKillUnits(loopPlot, 25)

                # Plot fuer Bonus checken
                # Nur 1 Plot rund um den Vulkan
                # Vergabe ganz unten
                if i > 0 and i < 4 and j > 0 and j < 4:
                  if not loopPlot.isWater() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1 and loopPlot.isHills():
                    bonusPlotArray.append(loopPlot)

                # Dem Plot +1 Nahrung geben (25%)
                if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and not (i==2 and j==2):
                 if loopPlot.getFeatureType != feat_vulkan and loopPlot.getTerrainType() != terr_tundra:
                  if myRandom(4) == 1:
                    gc.getGame().setPlotExtraYield(iRandX - 2 + i, iRandY - 2 + j, 0, 1) # x,y,YieldType,iChange
                    iOwner = loopPlot.getOwner()
                    if iOwner != -1:
                     if gc.getPlayer(iOwner).isHuman():
                      CyInterface().addMessage(iOwner, True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD",("",)), None, 2, gc.getFeatureInfo(feat_vulkan).getButton(), ColorTypes(8), loopPlot.getX(), loopPlot.getY(), True, True)
                      # fuer spaeteres popup
                      if gc.getPlayer(iOwner).getID() not in PlayerPopUpFood: PlayerPopUpFood.append(gc.getPlayer(iOwner).getID())

                # Verbreitbare Resi vernichten
                if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                  doEraseBonusFromDisaster(loopPlot)

          # Sauerer Regen
          # Ellipse nach Osten oder Westen: 15 Plots
          iRand_W_O = myRandom(2)
          for i in range(20):
            for j in range(11):

              if iRand_W_O == 1:
                loopPlot = gc.getMap().plot(iRandX + i, iRandY - 5 + j)
              else:
                loopPlot = gc.getMap().plot(iRandX - i, iRandY - 5 + j)

              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                and loopPlot.getFeatureType() != feat_vulkan and not loopPlot.isPeak():
                  bDraw = False
                  if   (i == 0 or i == 19) and j > 3 and j < 8: bDraw = True
                  elif (i == 1 or i == 18) and j > 2 and j < 8: bDraw = True
                  elif (i == 2 or i == 17) and j > 1 and j < 9: bDraw = True
                  elif (i == 3 or i == 4 or i == 15 or i == 16) and j > 0 and j < 10: bDraw = True
                  elif (i > 4 and i < 15): bDraw = True
                  if bDraw:
                    #loopPlot.setRouteType(-1)
                    bSetRegen = False
                    if loopPlot.getFeatureType() == -1: bSetRegen = True
                    elif loopPlot.getFeatureType() != feat_forest_burnt:
                      if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2 or loopPlot.getFeatureType() == feat_jungle:
                        if myRandom(2) == 1: bSetRegen = True

                    if bSetRegen:
                      loopPlot.setFeatureType(feat_saurer_regen,0)



          # Vulkan wird zu Wasser, wenn auf einer (Halb)Insel
          # Sprengt sich weg (somit keine Vulkan-Feature-Grafik notwendig)
          iNumWaterTiles = 0
          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
              if None != loopPlot and not loopPlot.isNone():
                if loopPlot.getFeatureType() == iDarkIce: continue
                if loopPlot.isWater(): iNumWaterTiles += 1
          # Statt dem Erbeben wird ein Tsunami zum Leben erweckt
          if iNumWaterTiles > 3:
            pPlot.setFeatureType(-1,0)
            pPlot.setTerrainType(terr_coast,1,1)
            pPlot.setPlotType(PlotTypes.PLOT_OCEAN,True,True)
            doTsunami(iRandX,iRandY)


      # Message: PopUp wegen +1 Food
      iRange = len(PlayerPopUpFood)
      if iRange > 0:
        for i in range (iRange):
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_VOLCANO_FOOD_POPUP",("",)))
          popupInfo.addPopup(PlayerPopUpFood[i])

      # Chance einer Magnetit und Obsidian Bonus Resource jeweils 50%
      iRange = len(bonusPlotArray)
      if iRange > 0:
        iRand = myRandom(3)
        iBonus = -1
        if iRand == 1: iBonus = bonus_magnetit
        elif iRand == 2: iBonus = bonus_obsidian

        if iBonus != -1:
          for iLoopPlot in range(iRange):
            iRand = myRandom(100)
            if iRand < 100 / (iLoopPlot+1):
              bonusPlotArray[iLoopPlot].setBonusType(iBonus)
              if bonusPlotArray[iLoopPlot].getOwner() > -1:
                if gc.getPlayer(bonusPlotArray[iLoopPlot].getOwner()).isHuman():
                  CyInterface().addMessage(bonusPlotArray[iLoopPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iBonus).getDescription(),)), None, 2, gc.getBonusInfo(iBonus).getButton(), ColorTypes(14), bonusPlotArray[iLoopPlot].getX(), bonusPlotArray[iLoopPlot].getY(), True, True)



def undoVulkan():
  terr_peak = gc.getInfoTypeForString("TERRAIN_PEAK")
  feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")

  iMapW = gc.getMap().getGridWidth()
  iMapH = gc.getMap().getGridHeight()

  for i in range (iMapW):
    for j in range (iMapH):
      pPlot = CyMap().plot(i, j)

      if pPlot.getFeatureType() == feat_vulkan:
        #iYield = pPlot.getYield(0)
        #if iYield > 0: gc.getGame().setPlotExtraYield(i, j, 0, -iYield) # x,y,YieldType,iChange
        # Reihenfolge einhalten! wichtig!!!
        pPlot.setFeatureType(-1,0)
        pPlot.setTerrainType(terr_peak,1,1)
        pPlot.setPlotType(PlotTypes.PLOT_PEAK,True,True)

  # --------- Ende Vulkan / Volcano ------------

def doTsunami(iX, iY):
  feat_seuche = gc.getInfoTypeForString("FEATURE_SEUCHE")
  feat_saurer_regen = gc.getInfoTypeForString("FEATURE_SAURER_REGEN")

  feat_flood_plains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
  feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')
  feat_vulkan = gc.getInfoTypeForString("FEATURE_VOLCANO")
  feat_tsunami = gc.getInfoTypeForString("FEATURE_TSUNAMI")

  iBuildingPalisade = gc.getInfoTypeForString('BUILDING_PALISADE')
  iBuildingWalls = gc.getInfoTypeForString('BUILDING_WALLS')
  iBuildingHW1 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS')
  iBuildingHW2 = gc.getInfoTypeForString('BUILDING_CELTIC_DUN')
  iBuildingHW3 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS_GRECO')

  iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

  iMapW = gc.getMap().getGridWidth()
  iMapH = gc.getMap().getGridHeight()

  # Der Tsunamieffekt muss im 2ten Wasserfeld vor der Kueste (Land) gestartet werden
  # Der Schaden soll bis einschliesslich 4 Landplots reingehen
  # Der Einschlag/Das Epizentrum darf maximal 3 Felder ausserhalb der Kueste (Land) sein, sonst unwirksam
  # Huegel und Berge stoppen den Schaden an weiteren Feldern
  # Plot 1: Stadt: Pop - 1/2, Units 15%, Gebaeude 10%, Mods + Streets
  # Plot 2: Stadt: Pop - 1/3, Units 10%, Gebaeude  5%, Mods + Streets
  #         Ausgenommen: Stadt auf Huegel mit Stadtmauer: Pop - 1/4, Units und Gebaeude 0%
  # Plot 3: Stadt: Pop - 1/4, Units  5%, Mods + Streets
  #         Ausgenommen: Stadt auf Huegel mit Stadtmauer: Sicher
  # Plot 4: Nur Modernisierungen
  # Stadtmauer 50%, Palisade 100% und Hohe Mauer 20% weg

  for iHimmelsrichtung in range(4):
      iDamageMaxPlots = 4
      bEffectDone = False
      bDoTsunami = False

      # 3 Plots dicke Flutkatastrophe
      for d in range(3):
       # Checken ob innerhalb von 4 Feldern Land ist
       for i in range(4):
         if iHimmelsrichtung == 0:   loopPlot = CyMap().plot(iX - 1 + d, iY + i) # Norden
         elif iHimmelsrichtung == 1: loopPlot = CyMap().plot(iX - 1 - d, iY - i) # Sueden
         elif iHimmelsrichtung == 2: loopPlot = CyMap().plot(iX + i, iY - 1 + d) # Osten
         elif iHimmelsrichtung == 3: loopPlot = CyMap().plot(iX - i, iY - 1 + d) # Westen
         if None != loopPlot and not loopPlot.isNone():
           if loopPlot.getFeatureType() == iDarkIce: continue
           if not loopPlot.isWater(): bDoTsunami = True

      if bDoTsunami == True:

       for d in range(3):
         iDamagePlots = 0

         if iHimmelsrichtung == 0:   iRange = iMapH - iY
         elif iHimmelsrichtung == 1: iRange = iY
         elif iHimmelsrichtung == 2: iRange = iMapW - iX
         elif iHimmelsrichtung == 3: iRange = iX

         for i in range(iRange):

          if iHimmelsrichtung == 0:   loopPlot = CyMap().plot(iX - 1 + d, iY + i)
          elif iHimmelsrichtung == 1: loopPlot = CyMap().plot(iX - 1 + d, iY - i)
          elif iHimmelsrichtung == 2: loopPlot = CyMap().plot(iX + i, iY - 1 + d)
          elif iHimmelsrichtung == 3: loopPlot = CyMap().plot(iX - i, iY - 1 + d)

          # 0: Einschlag/Epizentrum
          # Ende bei Max Plots
          if iDamagePlots >= iDamageMaxPlots: break
          # Ende bei DarkIce
          if loopPlot.getFeatureType() == iDarkIce: break
          # Ende bei Berg oder aktivem Vulkan
          if loopPlot.isPeak() or loopPlot.getFeatureType() == feat_vulkan: break
          # Ende wenn es ein Landstrich ist
          if iDamagePlots > 0 and loopPlot.isWater(): break

          # Land
          if i > 0 and not loopPlot.isWater():
           iDamagePlots += 1

           # Effekt
           if not bEffectDone and d == 1:
             if iHimmelsrichtung == 0:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_N")
               pEffectPlot = CyMap().plot(iX, iY + i - 2)
             elif iHimmelsrichtung == 1:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_S")
               pEffectPlot = CyMap().plot(iX, iY - i + 2)
             elif iHimmelsrichtung == 2:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_E")
               pEffectPlot = CyMap().plot(iX + i - 2, iY)
             elif iHimmelsrichtung == 3:
               iEffect = gc.getInfoTypeForString("EFFECT_TSUNAMI_W")
               pEffectPlot = CyMap().plot(iX - i + 2, iY)
             CyEngine().triggerEffect( iEffect, pEffectPlot.getPoint() )
             bEffectDone = True

             if gc.getPlayer(gc.getGame().getActivePlayer()).isHuman():
               if pEffectPlot.isVisibleToWatchingHuman():
                 CyCamera().JustLookAtPlot(pEffectPlot)
                 # Message: Eine gigantische Flutwelle trifft die Kueste und versetzt das Land in aergste Not!
                 popupInfo = CyPopupInfo()
                 popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                 popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_TSUNAMI",("",)))
                 popupInfo.addPopup(gc.getGame().getActivePlayer())
                 CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_TSUNAMI",("",)), "AS2D_TSUNAMI", 2, gc.getFeatureInfo(feat_tsunami).getButton(), ColorTypes(7), pEffectPlot.getX(), pEffectPlot.getY(), True, True)


           # Stadt
           if loopPlot.isCity():
             pCity = loopPlot.getPlotCity()
             iPlayer = pCity.getOwner()
             iPopAlt = pCity.getPopulation()
             iPopNeu = iPopAlt

             if iDamagePlots == 0:
               doDestroyCityBuildings(pCity, 10)
               doKillUnits(loopPlot, 15)
               iPopNeu = iPopAlt - int(iPopAlt / 2)
               if iPopNeu < 1: iPopNeu = 1
               pCity.setPopulation(iPopNeu)
             elif iDamagePlots == 1:
               # Stadt mit Stadtmauern und Huegel
               if loopPlot.isHills() and (pCity.isHasBuilding(iBuildingWalls) or pCity.isHasBuilding(iBuildingHW1) or pCity.isHasBuilding(iBuildingHW2) or pCity.isHasBuilding(iBuildingHW3) ):
                 iPopNeu = iPopAlt - int(iPopAlt / 4)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
               else:
                 doDestroyCityBuildings(pCity, 5)
                 doKillUnits(loopPlot, 10)
                 iPopNeu = iPopAlt - int(iPopAlt / 3)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
             elif iDamagePlots == 2:
               # Stadt mit Stadtmauern und Huegel
               if loopPlot.isHills() and (pCity.isHasBuilding(iBuildingWalls) or pCity.isHasBuilding(iBuildingHW1) or pCity.isHasBuilding(iBuildingHW2) or pCity.isHasBuilding(iBuildingHW3) ):
                 break
               else:
                 doKillUnits(loopPlot, 5)
                 iPopNeu = iPopAlt - int(iPopAlt / 4)
                 if iPopNeu < 1: iPopNeu = 1
                 pCity.setPopulation(iPopNeu)
             pCity.setFood(0)

             # Stadtmauern zerstoeren
             doDestroyWalls(pCity)

             if iPlayer != -1 and iPopNeu != iPopAlt:
               if gc.getPlayer(iPlayer).isHuman():
                 # Message: Die Bevoelkerung der Stadt %s sank von %alt auf %neu!
                 CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_CITY_SHRINKS_TO",(pCity.getName(),iPopAlt,iPopNeu)), None, 2, gc.getFeatureInfo(feat_tsunami).getButton(), ColorTypes(7), loopPlot.getX(), loopPlot.getY(), True, True)

             PAE_City.doCheckCityState(pCity)

           # Land
           else:
             if iDamagePlots + 1 < iDamageMaxPlots: loopPlot.setRouteType(-1)
             loopPlot.setImprovementType(-1)
             if loopPlot.getFeatureType() != feat_flood_plains \
             and loopPlot.getFeatureType() != feat_saurer_regen and loopPlot.getFeatureType() != feat_oasis:
               loopPlot.setFeatureType(feat_seuche,0)
             doKillUnits(loopPlot, 30)

           # Bei Huegel Tsunami stoppen
           if loopPlot.isHills(): iDamagePlots = iDamageMaxPlots

# ----------- Ende Tsunami ------------

def doMeteorites():
  feat_meteor = gc.getInfoTypeForString('FEATURE_METEORS')
  feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

  feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
  feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

  feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
  feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
  feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

  feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
  terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')

  iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

  iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")

  bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
  bonus_oreichalkos = gc.getInfoTypeForString("BONUS_OREICHALKOS")
  bonusPlotArray = []

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
  iMaxEffect = 0
  iMapSize = gc.getMap().getWorldSize()
  if iMapSize == 0: iMax = 1
  elif iMapSize == 1: iMax = 2
  elif iMapSize == 2: iMax = 4
  elif iMapSize == 3: iMax = 6
  elif iMapSize == 4: iMax = 8
  elif iMapSize == 5: iMax = 10
  else: iMax = 12

  # 20 Chancen fuer max. iMax Meteorstrikes
  for i in range (20):
    # Maximal iMax Effekte
    if iMaxEffect == iMax: break

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    iRandX = myRandom(iMapW)
    iRandY = myRandom(iMapH)
    pPlot = gc.getMap().plot(iRandX, iRandY)
    if None != pPlot and not pPlot.isNone():
        if pPlot.getFeatureType() == iDarkIce: continue
        iMaxEffect += 1
        # Modernisierung und Strasse entfernen
        if not pPlot.isCity():
           pPlot.setRouteType(-1)
           pPlot.setImprovementType(-1)

        iPlayer = pPlot.getOwner()
        if pPlot.isVisibleToWatchingHuman():
          CyCamera().JustLookAtPlot(pPlot)
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
          popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_METEORITES",("",)))
          popupInfo.addPopup(gc.getGame().getActivePlayer())
          CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES",("",)),"AS2D_METEORSTRIKE",2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(7),iRandX,iRandY,True,True)

        # Effekt
        iEffect = gc.getInfoTypeForString("EFFECT_METEORS")
        CyEngine().triggerEffect( iEffect, pPlot.getPoint() )

        # Stadt
        if pPlot.isCity():
          pCity = pPlot.getPlotCity()
          iPop_alt = pCity.getPopulation()
          iPop_neu = int(pCity.getPopulation() / 2)
          if iPop_neu < 2: iPop_neu = 1
          pCity.setPopulation(iPop_neu)
          pCity.setFood(0)
          if iPlayer != -1:
            if pPlot.isVisibleToWatchingHuman():
              if iPlayer == gc.getGame().getActivePlayer():
                CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
              else:
                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_METEORITES_CITY_OTHER",(gc.getPlayer(pCity.getOwner()).getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_meteor).getButton(),ColorTypes(2),iRandX,iRandY,True,True)

          # City, Wahrscheinlichkeit in %
          doKillUnits(pPlot,10)
          doDestroyCityBuildings(pCity,33)
          # Stadtmauern zerstoeren
          doDestroyWalls(pCity)
          PAE_City.doCheckCityState(pCity)

        # rundherum Brand generieren und dabei 50:50 Modernis und Strassen entfernen
        for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(iRandX - 1 + i, iRandY - 1 + j)
            if None != loopPlot and not loopPlot.isNone():
              if loopPlot.getFeatureType() != feat_flood_plains and not loopPlot.isPeak() \
              and not loopPlot.isWater() and loopPlot.getFeatureType() != feat_oasis:
                if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                  loopPlot.setFeatureType(feat_forest_burnt,0)
                else:
                  if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                    loopPlot.setFeatureType(feat_brand,0)
                if loopPlot.getImprovementType() == iImpType1: loopPlot.setImprovementType(-1)

              if myRandom(2) == 1:
                if not loopPlot.isCity():
                  loopPlot.setRouteType(-1)
                  loopPlot.setImprovementType(-1)
              doKillUnits(loopPlot,20)

            # Plot fuer Magnetit/Oreichalkos Bonus checken
            if not loopPlot.isWater() and not loopPlot.isCity() and not loopPlot.isPeak() and loopPlot.getBonusType(loopPlot.getOwner()) == -1 and loopPlot.getBonusType(-1) == -1:
              bonusPlotArray.append(loopPlot)

            # Verbreitbare Resi vernichten
            if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
              doEraseBonusFromDisaster(loopPlot)


    # Chance einer neuen Bonus Resource, 25% - danach 50:50 - Magnetit:Oreichalkos
  if len(bonusPlotArray) > 0:
    iRand = myRandom(8)
    if iRand < 2:
      if iRand == 0: iNewBonus = bonus_magnetit
      else: iNewBonus = bonus_oreichalkos
      iRandPlot = myRandom(len(bonusPlotArray))
      bonusPlotArray[iRandPlot].setBonusType(iNewBonus)
      if bonusPlotArray[iRandPlot].getOwner() > -1:
        if gc.getPlayer(bonusPlotArray[iRandPlot].getOwner()).isHuman():
          CyInterface().addMessage(bonusPlotArray[iRandPlot].getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iNewBonus).getDescription(),)), None, 2, gc.getBonusInfo(iNewBonus).getButton(), ColorTypes(14), bonusPlotArray[iRandPlot].getX(), bonusPlotArray[iRandPlot].getY(), True, True)


def doComet():
    feat_comet = gc.getInfoTypeForString('FEATURE_COMET')
    feat_brand = gc.getInfoTypeForString('FEATURE_SMOKE')

    feat_flood_plains = gc.getInfoTypeForString('FEATURE_FLOOD_PLAINS')
    feat_oasis = gc.getInfoTypeForString('FEATURE_OASIS')

    feat_forest = gc.getInfoTypeForString('FEATURE_FOREST')
    feat_forest2 = gc.getInfoTypeForString('FEATURE_DICHTERWALD')
    feat_forest_burnt = gc.getInfoTypeForString('FEATURE_FOREST_BURNT')

    feat_ice = gc.getInfoTypeForString('FEATURE_ICE')
    terr_snow = gc.getInfoTypeForString('TERRAIN_SNOW')
    iDarkIce = gc.getInfoTypeForString("FEATURE_DARK_ICE")

    iImpType1 = gc.getInfoTypeForString("IMPROVEMENT_LUMBER_CAMP")
    lVillages = []
    lVillages.append(gc.getInfoTypeForString("IMPROVEMENT_HAMLET"))
    lVillages.append(gc.getInfoTypeForString("IMPROVEMENT_VILLAGE"))
    lVillages.append(gc.getInfoTypeForString("IMPROVEMENT_TOWN"))

    bonus_magnetit = gc.getInfoTypeForString("BONUS_MAGNETIT")
    bonus_oreichalkos = gc.getInfoTypeForString("BONUS_OREICHALKOS")

    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()

    iRangeMaxPlayers = gc.getMAX_PLAYERS()

#  0 = WORLDSIZE_DUEL
#  1 = WORLDSIZE_TINY
#  2 = WORLDSIZE_SMALL
#  3 = WORLDSIZE_STANDARD
#  4 = WORLDSIZE_LARGE
#  5 = WORLDSIZE_HUGE
    iMaxEffect = 0
    iMapSize = gc.getMap().getWorldSize()
    if iMapSize < 3: iMax = 1
    elif iMapSize < 5: iMax = 2
    else: iMax = 3

    # iMax Kometen
    for i in range (iMax):

     # Soll nicht ganz am Rand sein (Flunky: alle 4 Raender ausnehmen)
     iRandX = 3 + myRandom(iMapW - 6)
     iRandY = 3 + myRandom(iMapH - 6)
     pPlot = gc.getMap().plot(iRandX, iRandY)
     if None != pPlot and not pPlot.isNone():

      if pPlot.getFeatureType() == iDarkIce: continue

      # Modernisierung und Strasse entfernen
      if not pPlot.isCity():
        pPlot.setRouteType(-1)
        pPlot.setImprovementType(-1)

      iPlayer = pPlot.getOwner()

      if pPlot.isVisibleToWatchingHuman():
        CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET",("",)),"AS2D_BOMBARD",2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
        CyCamera().JustLookAtPlot(pPlot)

      # Effekt
      if pPlot.isWater():
        CyEngine().triggerEffect( gc.getInfoTypeForString("EFFECT_COMET_WATER"), pPlot.getPoint() )
        # Loest Tsunami aus
        doTsunami(iRandX,iRandY)
      else:
        CyEngine().triggerEffect( gc.getInfoTypeForString("EFFECT_COMET"), pPlot.getPoint() )

        # Stadt
        if pPlot.isCity():
              pCity = pPlot.getPlotCity()
              iPop_alt = pCity.getPopulation()
              iPop_neu = int(pCity.getPopulation() / 6)
              if iPop_neu < 2: iPop_neu = 1
              pCity.setPopulation(iPop_neu)
              pCity.setFood(0)

              # Messages
              for iPlayer2 in range(iRangeMaxPlayers):
                pSecondPlayer = gc.getPlayer(iPlayer2)
                iSecondPlayer = pSecondPlayer.getID()
                if pSecondPlayer.isHuman():
                  iSecTeam = pSecondPlayer.getTeam()
                  if pPlot.isVisible(iSecTeam, 0) and pSecondPlayer.isHuman():
                    if iPlayer == iSecondPlayer:
                      popupInfo = CyPopupInfo()
                      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                      popupInfo.setText(CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY",(pCity.getName(),iPop_neu,iPop_alt)))
                      popupInfo.addPopup(iPlayer)
                      CyInterface().addMessage(iPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY",(pCity.getName(),iPop_neu,iPop_alt)),None,2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(7),iRandX,iRandY,True,True)
                    else:
                      # Message an alle
                      CyInterface().addMessage(iSecondPlayer, True, 12, CyTranslator().getText("TXT_KEY_DISASTER_COMET_CITY_OTHER",(pOwner.getCivilizationAdjective(2),pCity.getName())),None,2,gc.getFeatureInfo(feat_comet).getButton(),ColorTypes(2),iRandX,iRandY,True,True)

              # City, Wahrscheinlichkeit in %
              doKillUnits(pPlot,100)
              doDestroyCityBuildings(pCity,80)
              doDestroyCityWonders(pCity,25,feat_comet)
              PAE_City.doCheckCityState(pCity)

        # rundherum Brand generieren und dabei 50:50 Modernis und Strassen entfernen
        for i in range(7):
          for j in range(7):
                loopPlot = gc.getMap().plot(iRandX - 3 + i, iRandY - 3 + j)
                if None != loopPlot and not loopPlot.isNone():
                  if loopPlot.getFeatureType() == iDarkIce: continue
                  if loopPlot.getFeatureType() != feat_flood_plains and loopPlot.getFeatureType() != feat_oasis \
                  and not loopPlot.isPeak() and not loopPlot.isWater():
                    if loopPlot.getFeatureType() == feat_forest or loopPlot.getFeatureType() == feat_forest2:
                       loopPlot.setFeatureType(feat_forest_burnt,0)
                    else:
                      if loopPlot.getFeatureType() != feat_ice and loopPlot.getTerrainType() != terr_snow:
                         loopPlot.setFeatureType(feat_brand,0)
                    if loopPlot.getImprovementType() == iImpType1: loopPlot.setImprovementType(-1)

                  if myRandom(2) == 1:
                    if not loopPlot.isCity():
                      loopPlot.setRouteType(-1)
                      loopPlot.setImprovementType(-1)
                  # Gemeinden und Doerfer -> Huetten/Cottages
                  elif loopPlot.getImprovementType() in lVillages: loopPlot.setImprovementType(gc.getInfoTypeForString("IMPROVEMENT_COTTAGE"))


                  # Entfernung zum Einschlag berechnen
                  iBetrag = (iRandX - loopPlot.getX()) * (iRandX - loopPlot.getX()) + (iRandY - loopPlot.getY()) * (iRandY - loopPlot.getY())
                  if iBetrag == 1:
                    doKillUnits(loopPlot,50)
                    if loopPlot.isCity(): doDestroyCityBuildings(loopPlot.getPlotCity(),50)
                  elif iBetrag == 2:
                    doKillUnits(loopPlot,25)
                    if loopPlot.isCity(): doDestroyCityBuildings(loopPlot.getPlotCity(),25)
                  elif iBetrag == 3:
                    doKillUnits(loopPlot,10)
                    if loopPlot.isCity(): doDestroyCityBuildings(loopPlot.getPlotCity(),10)

                # Stadtmauern zerstoeren
                if loopPlot.isCity(): doDestroyWalls(loopPlot.getPlotCity())

                # Verbreitbare Resi vernichten (nur Radius 2)
                if i>0 and i<6 and j>1 and j<6:
                  if loopPlot.getBonusType(loopPlot.getOwner()) > -1 or loopPlot.getBonusType(-1) > -1:
                    doEraseBonusFromDisaster(loopPlot)

        # Chance einer neuen Bonus Resource fix auf pPlot
        # Chance 50% - danach 50:50 - Magnetit:Oreichalkos
        if not pPlot.isWater() and not pPlot.isPeak() and pPlot.getBonusType(pPlot.getOwner()) == -1 and pPlot.getBonusType(-1) == -1:
          iRand = myRandom(4)
          if iRand < 2:
            if iRand == 0: iNewBonus = bonus_magnetit
            else: iNewBonus = bonus_oreichalkos
            pPlot.setBonusType(iNewBonus)
            if pPlot.getOwner() > -1:
              if gc.getPlayer(pPlot.getOwner()).isHuman():
                CyInterface().addMessage(pPlot.getOwner(), True, 10, CyTranslator().getText("TXT_KEY_NEW_BONUS",(gc.getBonusInfo(iNewBonus).getDescription(),)), None, 2, gc.getBonusInfo(iNewBonus).getButton(), ColorTypes(14), pPlot.getX(), pPlot.getY(), True, True)



  # ------------------- Anfang Gebaeude, Wunder und Einheiten Damage  -----------------


  # iChance = Wahrscheinlichkeit, dass ein Gebaeude zerstoert wird
def doDestroyCityBuildings(pCity, iChance):
    iOwner = pCity.getOwner()
    iRange = gc.getNumBuildingInfos()
    for iBuilding in range(iRange):
        if pCity.getNumRealBuilding(iBuilding):
            pBuilding = gc.getBuildingInfo(iBuilding)
            if not isWorldWonderClass(pBuilding.getBuildingClassType()):
                if myRandom(100) < iChance:
                    pCity.setNumRealBuilding(iBuilding,0)
                    pOwner = gc.getPlayer(iOwner)
                    if pOwner.isHuman():
                        CyInterface().addMessage(pOwner.getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
    PAE_City.doCheckCityState(pCity)
    PAE_City.doCheckTraitBuildings(pCity)
    PAE_City.doCheckGlobalTraitBuildings(iOwner)


  # iChance = Wahrscheinlichkeit, dass ein Wunder zerstoert wird
  # iFeatureType = Art der Katastrophe
def doDestroyCityWonders(pCity, iChance, iFeatureType):
  iOwner = pCity.getOwner()
  iFeature_Erdbeben = gc.getInfoTypeForString("FEATURE_ERDBEBEN")
  iFeature_Komet = gc.getInfoTypeForString("FEATURE_COMET")

  iRangeMaxPlayers = gc.getMAX_PLAYERS()

  if pCity.getNumBuildings() > 0:
    iRange = gc.getNumBuildingInfos()
    for iBuilding in range(iRange):
      pBuilding = gc.getBuildingInfo(iBuilding)
      if pCity.getNumBuilding(iBuilding):
        if isWorldWonderClass(gc.getBuildingInfo(iBuilding).getBuildingClassType()):
          iRand = myRandom(100)
          if iRand < iChance:
            pCity.setNumRealBuilding(iBuilding,0)
            # Messages
            pOwner = gc.getPlayer(iOwner)
            iOwnerTeam = pOwner.getTeam()
            for iAllPlayer in range (iRangeMaxPlayers):
              ThisPlayer = gc.getPlayer(iAllPlayer)
              iThisPlayer = ThisPlayer.getID()
              iThisTeam = ThisPlayer.getTeam()
              ThisTeam = gc.getTeam(iThisTeam)
              if ThisTeam.isHasMet(iOwnerTeam) and ThisPlayer.isHuman():
                if iFeatureType == iFeature_Erdbeben:
                  CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER_ERDBEBEN",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_EARTHQUAKE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
                elif iFeatureType == iFeature_Komet:
                  CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER_KOMET",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_PLAGUE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)
                else:
                  CyInterface().addMessage(iThisPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_WONDER",(pOwner.getCivilizationAdjective(1),pCity.getName(),pBuilding.getDescription())),"AS2D_PLAGUE",2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


  # iChance = Wahrscheinlichkeit, dass eine Unit gekillt wird
def doKillUnits(pPlot, iChance):
  iRange = pPlot.getNumUnits()
  for iUnit in range (iRange):
    pUnit = pPlot.getUnit(iUnit)
    if pUnit != None:
      iRand = myRandom(100)
      if iRand < iChance:

        # Wenn ein General draufgeht hat das Auswirkungen
        if pUnit.getLeaderUnitType() > -1:
          PAE_Unit.doDyingGeneral(pUnit)

        if pUnit.getOwner() > -1:
          if gc.getPlayer(pUnit.getOwner()).isHuman():
            # Message: Eure Einheit %s hat diese schreckliche Naturgewalt nicht ueberlebt!
            CyInterface().addMessage( pUnit.getOwner(), True, 8, CyTranslator().getText("TXT_KEY_MESSAGE_DISASTER_UNIT_KILLED",(pPlot.getUnit(iUnit).getName(),0)), "AS2D_PLAGUE", 2, pPlot.getUnit(iUnit).getButton(), ColorTypes(7), pPlot.getX(), pPlot.getY(), True, True)

        pUnit.kill(1,pUnit.getOwner())

      else:
        pPlot.getUnit(iUnit).setDamage(60, -1)
        pPlot.getUnit(iUnit).setImmobileTimer(1)


def doDestroyWalls(pCity):
  iPlayer = pCity.getOwner()
  iBuildingPalisade = gc.getInfoTypeForString('BUILDING_PALISADE')
  iBuildingWalls = gc.getInfoTypeForString('BUILDING_WALLS')
  iBuildingHW1 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS')
  iBuildingHW2 = gc.getInfoTypeForString('BUILDING_CELTIC_DUN')
  iBuildingHW3 = gc.getInfoTypeForString('BUILDING_HIGH_WALLS_GRECO')

  # Stadtmauern zerstoeren
  if pCity.isHasBuilding(iBuildingPalisade):
    pBuilding = gc.getBuildingInfo(iBuildingPalisade)
    pCity.setNumRealBuilding(iBuildingPalisade,0)
    if iPlayer != -1:
      if gc.getPlayer(iPlayer).isHuman():
        CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

  if pCity.isHasBuilding(iBuildingWalls):
    if myRandom(100) < 50:
     pBuilding = gc.getBuildingInfo(iBuildingWalls)
     pCity.setNumRealBuilding(iBuildingWalls,0)
     if iPlayer != -1:
      if gc.getPlayer(iPlayer).isHuman():
       CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

  if pCity.isHasBuilding(iBuildingHW1):
    if myRandom(100) < 20:
     pBuilding = gc.getBuildingInfo(iBuildingHW1)
     pCity.setNumRealBuilding(iBuildingHW1,0)
     if iPlayer != -1:
      if gc.getPlayer(iPlayer).isHuman():
       CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

  if pCity.isHasBuilding(iBuildingHW2):
    if myRandom(100) < 20:
     pBuilding = gc.getBuildingInfo(iBuildingHW2)
     pCity.setNumRealBuilding(iBuildingHW2,0)
     if iPlayer != -1:
      if gc.getPlayer(iPlayer).isHuman():
       CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)

  if pCity.isHasBuilding(iBuildingHW3):
    if myRandom(100) < 20:
     pBuilding = gc.getBuildingInfo(iBuildingHW3)
     pCity.setNumRealBuilding(iBuildingHW3,0)
     if iPlayer != -1:
      if gc.getPlayer(iPlayer).isHuman():
       CyInterface().addMessage(gc.getPlayer(iPlayer).getID(), True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BUILDING",(pCity.getName(),pBuilding.getDescription())),None,2,pBuilding.getButton(),ColorTypes(7),pCity.getX(),pCity.getY(),True,True)


# Naturkatastrophen vernichten verbreitbare Bonusresourcen
# Nur bei Vulkan, Meteoriten und Kometen
def doEraseBonusFromDisaster(pPlot):
  # Inits (von doBonusCityGetPlot)
  lGetreide = []
  lGetreide.append(gc.getInfoTypeForString("BONUS_WHEAT"))
  lGetreide.append(gc.getInfoTypeForString("BONUS_GERSTE"))
  lGetreide.append(gc.getInfoTypeForString("BONUS_HAFER"))
  lGetreide.append(gc.getInfoTypeForString("BONUS_ROGGEN"))
  lGetreide.append(gc.getInfoTypeForString("BONUS_HIRSE"))
  lGetreide.append(gc.getInfoTypeForString("BONUS_RICE"))
  lVieh1 = []
  lVieh1.append(gc.getInfoTypeForString("BONUS_COW"))
  lVieh1.append(gc.getInfoTypeForString("BONUS_PIG"))
  lVieh1.append(gc.getInfoTypeForString("BONUS_SHEEP"))
  lSpice = []
  lSpice.append(gc.getInfoTypeForString("BONUS_OLIVES"))
  lSpice.append(gc.getInfoTypeForString("BONUS_DATTELN"))
  lTier1 = []
  lTier1.append(gc.getInfoTypeForString("BONUS_CAMEL"))

  # known bonus or unknown bonus(?)
  iPlayer = pPlot.getOwner()
  iBonus = pPlot.getBonusType(iPlayer)
  if iBonus == -1: iBonus = pPlot.getBonusType(-1)

  if iBonus > -1:
    if iBonus in lGetreide or iBonus in lVieh1 or iBonus in lSpice or iBonus in lTier1:
      pPlot.setBonusType(-1)
      if iPlayer > -1:
        if gc.getPlayer(iPlayer).isHuman():
          if iBonus in lGetreide:
            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS1",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
          elif iBonus in lVieh1 or iBonus in lTier1:
            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS2",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)
          elif iBonus in lSpice:
            CyInterface().addMessage(iPlayer, True, 8, CyTranslator().getText("TXT_KEY_DISASTER_DESTROYED_BONUS3",(gc.getBonusInfo(iBonus).getDescription(),)),None,2,gc.getBonusInfo(iBonus).getButton(),ColorTypes(7),pPlot.getX(),pPlot.getY(),True,True)


# ++++++++++++++++++ ENDE Naturkatastrophen / Disasters +++++++++++++++++++++++++++++