## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Edited by pierre@voak.at (pie), Austria
## Implementaion of miscellaneous game functions
# Lots of functions are only available when changed in Assets/PythonCallbackDefines.xml  (but not all!)

import CvUtil
from CvPythonExtensions import *
import CvEventInterface
import Popup as PyPopup
import PyHelpers
import re
import time # Seed! MP-OOS
import random # Seed! MP-OOS

# globals
gc = CyGlobalContext()
PyPlayer = PyHelpers.PyPlayer
PyInfo = PyHelpers.PyInfo
PyCity = PyHelpers.PyCity
PyGame = PyHelpers.PyGame

# PAE Random Seed
seed = int(time.strftime("%d%m%Y"))
random.seed(seed)
CyRandom().init(seed)

class CvGameUtils:
  "Miscellaneous game functions"
  def __init__(self):

    # PAE Veterans to Reservists feature
    self.lUnitsNoAIReservists = []
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_TRIARII2"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_PRAETORIAN"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_CELERES"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_ARCHER_LEGION"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_ELITE_HOPLIT"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_SPARTAN"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_UNSTERBLICH_2"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_ARGYRASPIDAI"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_ARGYRASPIDAI2"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_PHARAONENGARDE"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_GAUFUERST"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_NUBIAFUERST"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_MACCABEE"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_STAMMESFUERST"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_FUERST_DAKER"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_GERMAN_HARIER"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_RADSCHA"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_INDIAN_NAYAR"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"))
    self.lUnitsNoAIReservists.append(gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"))

    # PAE Foot soldier => Rider
    self.lUnitAuxiliar = []
    self.lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR"))
    self.lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"))
    self.lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON"))

    # PAE - vars for AI feature checks
    self.PAE_AI_ID = -1
    self.PAE_AI_Cities_Horses = []
    self.PAE_AI_Cities_Slaves = []
    self.PAE_AI_Cities_Slavemarket = []

    pass

#################### RANDOM ######################
  def myRandom (self, num, txt):
    #return gc.getGame().getMapRandNum(num, None)
    if num <= 1: return 0
    else: return random.randint(0, num-1)

  def isVictoryTest(self):
    if ( gc.getGame().getElapsedGameTurns() > 10 ):
      return True
    else:
      return False

  def isVictory(self, argsList):
    eVictory = argsList[0]
    return True

  def isPlayerResearch(self, argsList):
    ePlayer = argsList[0]
    return True

  def getExtraCost(self, argsList):
    ePlayer = argsList[0]
    return 0

  def createBarbarianCities(self):
    return False

  def createBarbarianUnits(self):
    return False

  def skipResearchPopup(self,argsList):
    ePlayer = argsList[0]
    return False

  def showTechChooserButton(self,argsList):
    ePlayer = argsList[0]
    return True

  def getFirstRecommendedTech(self,argsList):
    ePlayer = argsList[0]
    return TechTypes.NO_TECH

  def getSecondRecommendedTech(self,argsList):
    ePlayer = argsList[0]
    eFirstTech = argsList[1]
    return TechTypes.NO_TECH

  def canRazeCity(self,argsList):
    iRazingPlayer, pCity = argsList
#    if pCity.getPopulation() >= 4:
#      return False
    return True

  def canDeclareWar(self,argsList):
    iAttackingTeam, iDefendingTeam = argsList
    return True

  def skipProductionPopup(self,argsList):
    pCity = argsList[0]
    return False

  def showExamineCityButton(self,argsList):
    pCity = argsList[0]
    return True

  def getRecommendedUnit(self,argsList):
    pCity = argsList[0]
    return UnitTypes.NO_UNIT

  def getRecommendedBuilding(self,argsList):
    pCity = argsList[0]
    return BuildingTypes.NO_BUILDING

  def updateColoredPlots(self):
    return False

  def isActionRecommended(self,argsList):
    pUnit = argsList[0]
    iAction = argsList[1]
    return False

  def unitCannotMoveInto(self,argsList):
    ePlayer = argsList[0]
    iUnitId = argsList[1]
    iPlotX = argsList[2]
    iPlotY = argsList[3]
###########################################
# Max Units on a Plot
# Only available when changed in Assets/PythonCallbackDefines.xml
    pPlot = CyMap().plot(iPlotX, iPlotY)
    iNum = pPlot.getNumUnits()
#    CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_CITY_GROWTH",("X",iNum)), None, 2, None, ColorTypes(12), 0, 0, False, False)
    if (not pPlot.isWater() and not pPlot.isCity() and iNum >= 14):
      return True
# --------- end ---------------------------
    return False

  def cannotHandleAction(self,argsList):
    pPlot = argsList[0]
    iAction = argsList[1]
    bTestVisible = argsList[2]
    return False

  # Ist derzeit bei PythonCallbackDefines.xml wieder deaktiviert
  def canBuild(self,argsList):
    iX, iY, iBuild, iPlayer = argsList
    # Aussenhandelsposten nicht im eigenen Land
    if iBuild == gc.getInfoTypeForString("BUILD_HANDELSPOSTEN"):
      if CyMap().plot(iX, iY).getOwner() != -1: return 0
    return -1  # Returning -1 means ignore; 0 means Build cannot be performed; 1 or greater means it can

  def cannotFoundCity(self,argsList):
    iPlayer, iPlotX, iPlotY = argsList
    return False

  def cannotSelectionListMove(self,argsList):
    pPlot = argsList[0]
    bAlt = argsList[1]
    bShift = argsList[2]
    bCtrl = argsList[3]
    return False

  def cannotSelectionListGameNetMessage(self,argsList):
    eMessage = argsList[0]
    iData2 = argsList[1]
    iData3 = argsList[2]
    iData4 = argsList[3]
    iFlags = argsList[4]
    bAlt = argsList[5]
    bShift = argsList[6]
    return False

  def cannotDoControl(self,argsList):
    eControl = argsList[0]
    return False

  def canResearch(self,argsList):
    ePlayer = argsList[0]
    eTech = argsList[1]
    bTrade = argsList[2]
    return False

  def cannotResearch(self,argsList):
    ePlayer = argsList[0]
    eTech = argsList[1]
    bTrade = argsList[2]
    return False

  def canDoCivic(self,argsList):
    ePlayer = argsList[0]
    eCivic = argsList[1]
    # Trait Imperialist: Herrscherkult von Anfang an / ruler cult right from the beginning
    if ePlayer != -1:
        pPlayer = gc.getPlayer(ePlayer)
        if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_IMPERIALIST")) and eCivic == gc.getInfoTypeForString("CIVIC_HERRSCHERKULT"): return True
    #--
    return False

  def cannotDoCivic(self,argsList):
    ePlayer = argsList[0]
    eCivic = argsList[1]
    # Civic Hohepriester darf ohne Staatsreligion nicht genutzt werden
    if eCivic == gc.getInfoTypeForString("CIVIC_HOHEPRIESTER") and gc.getPlayer(ePlayer).getStateReligion() == -1: return True
    sScenarioScriptData = CyMap().plot(0, 0).getScriptData()
    iRound = gc.getGame().getGameTurn() - gc.getGame().getStartTurn()
    if sScenarioScriptData == "PeloponnesianWarKeinpferd" or sScenarioScriptData == "FirstPunicWar" or sScenarioScriptData == "WarOfDiadochi":
        if not gc.getPlayer(ePlayer).isHuman() and iRound <= 50: return True
    if sScenarioScriptData == "480BC" or sScenarioScriptData == "LimesGermanicus":
        if not gc.getPlayer(ePlayer).isHuman() and iRound <= 20: return True
    return False

  def canTrain(self,argsList):
    pCity = argsList[0]
    eUnit = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    bIgnoreCost = argsList[4]
    bIgnoreUpgrades = argsList[5]
    return False

  def cannotTrain(self,argsList):
    pCity = argsList[0]
    eUnit = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    bIgnoreCost = argsList[4]
    bIgnoreUpgrades = argsList[5]

    #pUnit = gc.getUnitInfo(eUnit)

    return False

  def canConstruct(self,argsList):
    pCity = argsList[0]
    eBuilding = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    bIgnoreCost = argsList[4]
    return False

  def cannotConstruct(self,argsList):
    pCity = argsList[0]
    eBuilding = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    bIgnoreCost = argsList[4]
    return False

  def canCreate(self,argsList):
    pCity = argsList[0]
    eProject = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    return False

  def cannotCreate(self,argsList):
    pCity = argsList[0]
    eProject = argsList[1]
    bContinue = argsList[2]
    bTestVisible = argsList[3]
    return False

  def canMaintain(self,argsList):
    pCity = argsList[0]
    eProcess = argsList[1]
    bContinue = argsList[2]
    return False

  def cannotMaintain(self,argsList):
    pCity = argsList[0]
    eProcess = argsList[1]
    bContinue = argsList[2]
    return False

  def AI_chooseTech(self,argsList):
    ePlayer = argsList[0]
    bFree = argsList[1]
    pPlayer = gc.getPlayer(ePlayer)
    iCiv = pPlayer.getCivilizationType()
    eTeam = gc.getTeam(pPlayer.getTeam())
    iTech = -1
    iBronze = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_BRONZE')
    iHorse = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_HORSE')
    iEles = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_IVORY')
    iCamel = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_CAMEL')
    iStone = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_STONE')
    iMarble = CvUtil.findInfoTypeNum(gc.getBonusInfo,gc.getNumBonusInfos(),'BONUS_MARBLE')

    # Generell nur 1 Hauptabfrage, um nicht immer soviel zu haben:

    # vor Fuehrerschaft
    if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_LEADERSHIP')):
      # 1. Mystik
      iTech = gc.getInfoTypeForString('TECH_MYSTICISM')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 2. Jagd
      iTech = gc.getInfoTypeForString('TECH_HUNTING')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 3. Schamanismus
      iTech = gc.getInfoTypeForString('TECH_SCHAMANISMUS')
      if not eTeam.isHasTech(iTech):
        return iTech

      # Hindu
      iTech = gc.getInfoTypeForString('TECH_RELIGION_HINDU')
      if pPlayer.canResearch(iTech, False):
        return iTech

      # 3. Polytheismus
      iTech = gc.getInfoTypeForString('TECH_POLYTHEISM')
      if not eTeam.isHasTech(iTech):
        return iTech

      # Egypt und Sumer
      if iCiv == gc.getInfoTypeForString('CIVILIZATION_EGYPT'):
        iTech = gc.getInfoTypeForString('TECH_RELIGION_EGYPT')
        if pPlayer.canResearch(iTech, False):
          return iTech

      if iCiv == gc.getInfoTypeForString('CIVILIZATION_SUMERIA'):
        iTech = gc.getInfoTypeForString('TECH_RELIGION_SUMER')
        if pPlayer.canResearch(iTech, False):
          return iTech

      # 4. Fuehrerschaft beeline
      return gc.getInfoTypeForString('TECH_LEADERSHIP')

    # vor Binnenkolonisierung
    if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_COLONIZATION')):
      # Those Civs shall get their neighbour religion at least after leadership
      if iCiv == gc.getInfoTypeForString('CIVILIZATION_NUBIA'):
        iTech = gc.getInfoTypeForString('TECH_RELIGION_EGYPT')
        if not eTeam.isHasTech(iTech):
          return iTech

      elif iCiv == gc.getInfoTypeForString('CIVILIZATION_BABYLON'):
        iTech = gc.getInfoTypeForString('TECH_RELIGION_SUMER')
        if not eTeam.isHasTech(iTech):
          return iTech

      # 6. Landwirtschaft
      iTech = gc.getInfoTypeForString('TECH_AGRICULTURE')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 7. Viehzucht
      iTech = gc.getInfoTypeForString('TECH_ANIMAL_HUSBANDRY')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 8. Bootsbau beeline falls Kuestenstadt
      iTech = gc.getInfoTypeForString('TECH_BOOTSBAU')
      if pPlayer.countNumCoastalCities() > 0:
        if not eTeam.isHasTech(iTech):
          return iTech

      # 9. Pflug
      iTech = gc.getInfoTypeForString('TECH_PFLUG')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 10. Bogenschiessen
      iTech = gc.getInfoTypeForString('TECH_ARCHERY')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 11. Bergbau beeline
      iTech = gc.getInfoTypeForString('TECH_MINING')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 12. Staatenbildung beeline
      iTech = gc.getInfoTypeForString('TECH_STAATENBILDUNG')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 12. Binnenkolonisierung beeline
      return gc.getInfoTypeForString('TECH_COLONIZATION')

    # vor der EISENZEIT
    if not eTeam.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING')):
      # Restliche Grundtechs und andere Basics nach Binnenkolonisierung:
      # 1. Rad
      iTech = gc.getInfoTypeForString('TECH_THE_WHEEL')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 2. Kriegsaxt
      iTech = gc.getInfoTypeForString('TECH_BEWAFFNUNG')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 3. Gesteinsabbau
      iTech = gc.getInfoTypeForString('TECH_STEINABBAU')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 4. Astronomie
      iTech = gc.getInfoTypeForString('TECH_ASTRONOMIE')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 5. Zeremonielles Begraebnis
      iTech = gc.getInfoTypeForString('TECH_CEREMONIAL')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 6. Zahlensysteme fuer Spezialisten
      iTech = gc.getInfoTypeForString('TECH_ZAHLENSYSTEME')
      if not eTeam.isHasTech(iTech):
        # Zahlensysteme
        if pPlayer.canResearch(iTech, false): return iTech
        # 6a. Hieroglyphen
        iTech = gc.getInfoTypeForString('TECH_WRITING2')
        if not eTeam.isHasTech(iTech):
          if pPlayer.canResearch(iTech, false): return iTech
        # 6b. Keilschrift
        iTech = gc.getInfoTypeForString('TECH_WRITING')
        if not eTeam.isHasTech(iTech):
          if pPlayer.canResearch(iTech, false): return iTech

      # 7. Steinmetzkunst nur fuer Spezialisten
      iTech = gc.getInfoTypeForString('TECH_MASONRY')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ZAHLENSYSTEME')):
          return iTech

      # 8. Geometrie fuer Spezialisten
      iTech = gc.getInfoTypeForString('TECH_GEOMETRIE')
      if pPlayer.canResearch(iTech, False):
        return iTech

      # 9. Fruchtbarkeitskult beeline ueber Sonnen- / Mondkalender
      iTech = gc.getInfoTypeForString('TECH_FRUCHTBARKEIT')
      if not eTeam.isHasTech(iTech):
        return iTech

      # Fuer Abu Simbel beim Nubier
      if iCiv == gc.getInfoTypeForString('CIVILIZATION_NUBIA'):
        iTech = gc.getInfoTypeForString('TECH_TEMPELWIRTSCHAFT')
        if not eTeam.isHasTech(iTech):
          return iTech
      # 10. Kurzbogen beeline ueber Speerspitzen
      iTech = gc.getInfoTypeForString('TECH_ARCHERY2')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 11. Streitaxt mit Bronze
      iTech = gc.getInfoTypeForString('TECH_BEWAFFNUNG2')
      if not eTeam.isHasTech(iTech):
        if pPlayer.getNumAvailableBonuses(iBronze) > 0:
          return iTech

      # 12. Wein, wenn Trauben vorhanden
      iTech = gc.getInfoTypeForString('TECH_WEINBAU')
      if not eTeam.isHasTech(iTech):
        if pPlayer.countOwnedBonuses(gc.getInfoTypeForString('BONUS_GRAPES')) > 0:
          return iTech

      # 13. Kultivierung
      iTech = gc.getInfoTypeForString('TECH_KULTIVIERUNG')
      if not eTeam.isHasTech(iTech):
        return iTech

      # 14. Arithmetik beeline nach Seidenstrasse
      iTech = gc.getInfoTypeForString('TECH_ARITHMETIK')
      if not eTeam.isHasTech(iTech):
        if CyGame().getProjectCreatedCount(gc.getInfoTypeForString('PROJECT_SILKROAD')) > 0:
          return iTech

      # 15.Codex / Indra
      # bis Versklavung freies Techen
      iTech = gc.getInfoTypeForString('TECH_CODEX')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
           return iTech

    # --- Eisenzeit ---
    # Camels / Kamele
    iTech = gc.getInfoTypeForString('TECH_KAMELZUCHT')
    if not eTeam.isHasTech(iTech):
      if pPlayer.getNumAvailableBonuses(iCamel) > 0:
        return iTech

    # Eledome
    iTech = gc.getInfoTypeForString('TECH_ELEFANTENZUCHT')
    if not eTeam.isHasTech(iTech):
      if pPlayer.getNumAvailableBonuses(iEles) > 0:
        if pPlayer.canResearch(iTech, False):
          return iTech

    iTech = gc.getInfoTypeForString('TECH_THE_WHEEL3')
    if not eTeam.isHasTech(iTech):
      if pPlayer.getNumAvailableBonuses(iHorse) > 0:
        if pPlayer.canResearch(iTech, False):
          return iTech

    iTech = gc.getInfoTypeForString('TECH_SCHIFFSBAU')
    if not eTeam.isHasTech(iTech):
      if pPlayer.countNumCoastalCities() > 0:
        if pPlayer.canResearch(iTech, False):
          return iTech


    iTech = gc.getInfoTypeForString('TECH_KUESTE')
    if not eTeam.isHasTech(iTech):
      if pPlayer.countNumCoastalCities() > 3:
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_KARTEN')):
          if pPlayer.canResearch(iTech, False):
            return iTech

    # Heroen
    iTech = gc.getInfoTypeForString('TECH_GLADIATOR')
    if not eTeam.isHasTech(iTech):
      if pPlayer.canResearch(iTech, False):
        return iTech

    # Kriegstechs
    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_IRON_WORKING')):
      iTech = gc.getInfoTypeForString('TECH_BELAGERUNG')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          if eTeam.getAtWarCount(True) >= 1:
            return iTech

    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_MECHANIK')):
      iTech = gc.getInfoTypeForString('TECH_CATAPULT')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          if eTeam.getAtWarCount(True) >= 1:
            return iTech

    # Wissen
    iTech = gc.getInfoTypeForString('TECH_LIBRARY')
    if not eTeam.isHasTech(iTech):
     if pPlayer.canResearch(iTech, False):
      if iCiv == gc.getInfoTypeForString('CIVILIZATION_ROME') or iCiv == gc.getInfoTypeForString('CIVILIZATION_ETRUSCANS') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_GREECE') or iCiv == gc.getInfoTypeForString('CIVILIZATION_ATHENS') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_THEBAI') or iCiv == gc.getInfoTypeForString('CIVILIZATION_SPARTA') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_MACEDONIA') or iCiv == gc.getInfoTypeForString('CIVILIZATION_HETHIT') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_LYDIA') or iCiv == gc.getInfoTypeForString('CIVILIZATION_PHON') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_PERSIA') or iCiv == gc.getInfoTypeForString('CIVILIZATION_BABYLON') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_SUMERIA') or iCiv == gc.getInfoTypeForString('CIVILIZATION_ASSYRIA') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_CARTHAGE') or iCiv == gc.getInfoTypeForString('CIVILIZATION_EGYPT') \
      or iCiv == gc.getInfoTypeForString('CIVILIZATION_IBERER'):
        return iTech

    # Wunder
    # Mauern von Babylon
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_BABYLON'):
      iTech = gc.getInfoTypeForString('TECH_CONSTRUCTION')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_LIBRARY')):
          return iTech

    # Artemistempel
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_LYDIA'):
      iTech = gc.getInfoTypeForString('TECH_BAUKUNST')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_LIBRARY')):
          return iTech

    # Ninive
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_ASSYRIA'):
      iTech = gc.getInfoTypeForString('TECH_PHILOSOPHY')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_CONSTRUCTION')):
          return iTech

    # 1000 Saeulen
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_PERSIA'):
      iTech = gc.getInfoTypeForString('TECH_MOSAIK')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_KUNST')):
          return iTech

    # CIV - Trennung: zB Religionen
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_CELT') or iCiv == gc.getInfoTypeForString('CIVILIZATION_GALLIEN'):
      iTech = gc.getInfoTypeForString('TECH_RELIGION_CELTIC')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ENSLAVEMENT')):
          return iTech

    if iCiv == gc.getInfoTypeForString('CIVILIZATION_GERMANEN'):
      iTech = gc.getInfoTypeForString('TECH_RELIGION_NORDIC')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ENSLAVEMENT')):
          return iTech

    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_GREEK')):
      iTech = gc.getInfoTypeForString('TECH_RELIGION_GREEK')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ENSLAVEMENT')):
          return iTech

    if iCiv == gc.getInfoTypeForString('CIVILIZATION_PHON'):
      iTech = gc.getInfoTypeForString('TECH_RELIGION_PHOEN')
      if not eTeam.isHasTech(iTech):
        return iTech

    if iCiv == gc.getInfoTypeForString('CIVILIZATION_PERSIA') or iCiv == gc.getInfoTypeForString('CIVILIZATION_ASSYRIA'):
      iTech = gc.getInfoTypeForString('TECH_DUALISMUS')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ENSLAVEMENT')):
          return iTech

    if iCiv == gc.getInfoTypeForString('CIVILIZATION_INDIA'):
      iTech = gc.getInfoTypeForString('TECH_MEDITATION')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_CODE_OF_LAWS')):
          return iTech
      iTech = gc.getInfoTypeForString('TECH_ASKESE')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

    if iCiv == gc.getInfoTypeForString('CIVILIZATION_ROME'):
      iTech = gc.getInfoTypeForString('TECH_RELIGION_ROME')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ALPHABET')):
          return iTech

    # Judentum
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_ISRAEL'):
      iTech = gc.getInfoTypeForString('TECH_MONOTHEISM')
      if not eTeam.isHasTech(iTech):
        if eTeam.isHasTech(gc.getInfoTypeForString('TECH_COLONIZATION2')):
          return iTech

    # Voelkerspezifisches Wissen
    # Perser
    if iCiv == gc.getInfoTypeForString('CIVILIZATION_PERSIA'):
      iTech = gc.getInfoTypeForString('TECH_PERSIAN_ROAD')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

    # Griechen
    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_GREEK')):
      iTech = gc.getInfoTypeForString('TECH_MANTIK')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech
    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_GREEK')):
      iTech = gc.getInfoTypeForString('TECH_PHALANX')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

    # Roemer
    if eTeam.isHasTech(gc.getInfoTypeForString('TECH_ROMAN')):
      iTech = gc.getInfoTypeForString('TECH_CORVUS')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_MANIPEL')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_PILUM')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_MARIAN_REFORM')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_CALENDAR2')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_ROMAN_ROADS')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_FEUERWEHR')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

      iTech = gc.getInfoTypeForString('TECH_LORICA_SEGMENTATA')
      if not eTeam.isHasTech(iTech):
        if pPlayer.canResearch(iTech, False):
          return iTech

    return TechTypes.NO_TECH

  def AI_chooseProduction(self,argsList):
    pCity = argsList[0]
    iOwner = pCity.getOwner()
    pPlayer = gc.getPlayer(iOwner)

    # Barbs ausgeschlossen
    if iOwner == gc.getBARBARIAN_PLAYER(): return False

    # AI soll sofort Palast bauen, wenn baubar
    if pPlayer.getCapitalCity().getID() == -1:
      iBuilding = gc.getInfoTypeForString("BUILDING_PALACE")
      if pCity.canConstruct (iBuilding,0,0,0):
        bDoIt = True
        # Stadtproduktionen durchgehen
        lCities = PyPlayer(iOwner).getCityList()
        for lCity in lCities:
          pCityX = pPlayer.getCity( lCity.getID() )
          if pCityX.getBuildingProduction (iBuilding):
            bDoIt = False
            break

        if bDoIt:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_CONSTRUCT, iBuilding, -1, False, False, False, True)
          return True

    # Projects
    iProject = -1

    # Seidenstrasse: wenn Zugang zu Seide
    iProjectX = gc.getInfoTypeForString("PROJECT_SILKROAD")
    if pCity.canCreate (iProjectX,0,0) and not pCity.isProductionProject():
      iBonus = gc.getInfoTypeForString("BONUS_SILK")
      if pCity.hasBonus(iBonus): iProject = iProjectX
      elif gc.getTeam(pPlayer.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_DEFENCES")): iProject = iProjectX

    # Bibel: wenn mehr als die Haelfte der Staedte das Christentum haben
    iProjectX = gc.getInfoTypeForString("PROJECT_BIBEL")
    if pCity.canCreate (iProjectX,0,0) and not pCity.isProductionProject():
        iNumCitiesWithChristianity = 0
        iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
        lCities = PyPlayer(iOwner).getCityList()
        iRange = len(lCities)
        for iCity in range(iRange):
          pCityX = pPlayer.getCity( lCities[iCity].getID() )
          if pCityX.isHasReligion(iReligion): iNumCitiesWithChristianity += 1

        if iNumCitiesWithChristianity > len(lCities) / 2: iProject = iProjectX

    # Antonius Kloster: wenn die Staatsreligion das Christentum ist
    iProjectX = gc.getInfoTypeForString("PROJECT_ANTONIUS_KLOSTER")
    if pCity.canCreate (iProjectX,0,0) and not pCity.isProductionProject():
      iReligion = gc.getInfoTypeForString("RELIGION_CHRISTIANITY")
      if pPlayer.getStateReligion() == iReligion: iProject = iProjectX

    # Akasha Chronik
    iProjectX = gc.getInfoTypeForString("PROJECT_AKASHA_CHRONIK")
    if pCity.canCreate (iProjectX,0,0) and not pCity.isProductionProject():
      iReligion = gc.getInfoTypeForString("RELIGION_HINDUISM")
      if pPlayer.getStateReligion() == iReligion: iProject = iProjectX

    # Projekt in Auftrag geben
    if iProject != -1:
        bDoIt = True
        # Stadtproduktionen durchgehen
        lCities = PyPlayer(iOwner).getCityList()
        iRange = len(lCities)
        for iCity in range(iRange):
          pCityX = pPlayer.getCity( lCities[iCity].getID() )
          if pCityX.isProductionProject():
            bDoIt = False
            break

        if bDoIt:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_CREATE, iProject, -1, False, False, True, False)
          return True
    # ---------------

    # Einheitenproduktion -----------
    # Aber erst ab Pop 5
    if pCity.getPopulation() > 4:

     # Bei Goldknappheit, Haendler in Auftrag geben (50%)
     if pCity.getPopulation() > 5:
       if pPlayer.getGold() < 500:
         if pPlayer.calculateGoldRate() < 5:
           if 1 == self.myRandom(2, None):
             iUnit = gc.getInfoTypeForString("UNIT_TRADE_MERCHANTMAN")
             if pCity.canTrain(iUnit,0,0):
               gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, iUnit, -1, False, False, True, False)
               return True
             iUnit = gc.getInfoTypeForString("UNIT_TRADE_MERCHANT")
             if pCity.canTrain(iUnit,0,0):
               pArea = pCity.area()
               if pArea.getNumCities() > 1:
                 if pArea.getNumTiles() > pArea.getNumOwnedTiles() * 2:
                   gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, iUnit, -1, False, False, True, False)
                   return True

     # Sonstige spezielle Einheiten
     iRand = self.myRandom(10, None)
     # Chance of 20%
     if iRand < 2:
      # Inquisitor
      Unit1 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_INQUISITOR" )
      # Haendler zu Land
      Unit2 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_TRADE_MERCHANT" )
      # Haendler zu Meer
      Unit3 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_TRADE_MERCHANTMAN" )
      # Versorgungswagen
      Unit4 = gc.getCivilizationInfo(pPlayer.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_SUPPLY_WAGON"))
      # Handelskarawane
      Unit5 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_CARAVAN" )
      # Pferd
      Unit6 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_HORSE" )
      # Getreidekarren
      Unit7 = CvUtil.findInfoTypeNum(gc.getUnitInfo,gc.getNumUnitInfos(), "UNIT_SUPPLY_FOOD" )

      # Unit already exists
      bUnit1 = False
      bUnit2 = False
      bUnit3 = False
      bUnit4 = False
      bUnit5 = False
      bUnit6 = False
      bUnit7 = False

      if pCity.canTrain(Unit1,0,0) or pCity.canTrain(Unit2,0,0) or pCity.canTrain(Unit3,0,0) or pCity.canTrain(Unit4,0,0) or pCity.canTrain(Unit5,0,0) \
      or pCity.canTrain(Unit6,0,0) or pCity.canTrain(Unit7,0,0):

        # Inselstadt soll nur Handelsschiffe bauen
        i=j=Plots=0
        for i in range(3):
          for j in range(3):
            loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
            if loopPlot != None and not loopPlot.isNone():
              if not loopPlot.isWater(): Plots = Plots + 1
        if Plots < 7:
          bUnit1 = True
          bUnit2 = True
          bUnit4 = True
          bUnit5 = True
          bUnit6 = True
          bUnit7 = True


        # if there is a Unit, don't Build one
        lUnits = PyPlayer(iOwner).getUnitList()
        lUnitTypes = []
        iRange = len(lUnits)
        for iUnit in range(iRange):
          lUnitTypes.append( pPlayer.getUnit(lUnits[iUnit].getID()).getUnitType() )

        if Unit1 in lUnitTypes: bUnit1 = True
        if Unit2 in lUnitTypes: bUnit2 = True
        if Unit3 in lUnitTypes: bUnit3 = True
        if Unit4 in lUnitTypes: bUnit4 = True
        if Unit5 in lUnitTypes: bUnit5 = True
        if Unit6 in lUnitTypes: bUnit6 = True
        if Unit7 in lUnitTypes: bUnit7 = True

        # Stadtproduktion durchgehen
        lCities = PyPlayer(iOwner).getCityList()
        iRange = len(lCities)
        for iCity in range(iRange):
          pCityX = gc.getPlayer(iOwner).getCity( lCities[iCity].getID() )
          if pCityX.isProductionUnit():
            if not bUnit1:
              if pCityX.getUnitProduction(Unit1): bUnit1 = True
            if not bUnit2:
              if pCityX.getUnitProduction(Unit2): bUnit2 = True
            if not bUnit3:
              if pCityX.getUnitProduction(Unit3): bUnit3 = True
            if not bUnit4:
              if pCityX.getUnitProduction(Unit4): bUnit4 = True
            if not bUnit5:
              if pCityX.getUnitProduction(Unit5): bUnit5 = True
            if not bUnit6:
              if pCityX.getUnitProduction(Unit6): bUnit6 = True
            if not bUnit7:
              if pCityX.getUnitProduction(Unit7): bUnit7 = True

        # Auf zur Produktion
        if pCity.canTrain(Unit1,0,0) and not bUnit1 and pPlayer.isStateReligion():
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit1, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit2,0,0) and not bUnit2:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit2, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit3,0,0) and not bUnit3:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit3, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit4,0,0) and not bUnit4:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit4, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit5,0,0) and not bUnit5:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit5, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit6,0,0) and not bUnit6 and pCity.getPopulation() > 5:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit6, -1, False, False, True, False)
          return True
        if pCity.canTrain(Unit7,0,0) and not bUnit7:
          gc.getMap().plot(pCity.getX(), pCity.getY()).getPlotCity().pushOrder(OrderTypes.ORDER_TRAIN, Unit7, -1, False, False, True, False)
          return True

    return False

  # global
  def AI_unitUpdate(self,argsList):
    pUnit = argsList[0]
    iOwner = pUnit.getOwner()
    pOwner = gc.getPlayer(iOwner)
    pTeam = gc.getTeam(pOwner.getTeam())

    if not pOwner.isHuman():
      pUnitOwner = gc.getPlayer(iOwner)
      iUnitType = pUnit.getUnitType()
      pPlayer = pUnitOwner
      lCities = PyPlayer(iOwner).getCityList()

      # PAE AI Unit Instances (better turn time)
      if self.PAE_AI_ID != iOwner:
         self.PAE_AI_ID = iOwner
         self.PAE_AI_Cities_Horses = []
         self.PAE_AI_Cities_Slaves = []
         self.PAE_AI_Cities_Slavemarket = []


      # Inquisitor
      if iUnitType == gc.getInfoTypeForString("UNIT_INQUISITOR") and iOwner != gc.getBARBARIAN_PLAYER():
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Inquisitor",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        if self.doInquisitorCore_AI(pUnit):
          return True

      # Freed slaves
      if iUnitType == gc.getInfoTypeForString("UNIT_FREED_SLAVE"):
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Freed Slave",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        if self.doSettleFreedSlaves_AI(pUnit):
          return True

      # Elefant (Zucht/Elefantenstall)
      if iUnitType == gc.getInfoTypeForString("UNIT_ELEFANT"):
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Elefant",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_ELEFANTENZUCHT")):
          if self.doElefant_AI(pUnit):
            return True

      # Bonusverbreitung
      if iUnitType == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD") and iOwner != gc.getBARBARIAN_PLAYER():
        #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Supply Food",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)
        if self.doBonusverbreitung_AI(pUnit):
          return True

      # Trade merchant (aber nicht Great Merchant)
      if pUnit.getUnitAIType() == gc.getInfoTypeForString("UNITAI_MERCHANT") and iUnitType != gc.getInfoTypeForString("UNIT_MERCHANT") and iOwner != gc.getBARBARIAN_PLAYER():
        # AI vergibt UNITAITyp beim Bau
        # or iUnitType == gc.getInfoTypeForString("UNIT_GAULOS") or iUnitType == gc.getInfoTypeForString("UNIT_CARVEL_TRADE"):
        if CvEventInterface.getEventManager().doAutomateMerchant(pUnit):
          return True

# Veteran -> Eliteunit (netMessage 705)
# und weiter unten aendern!

      # Ab Kampferfahren Status (nur Streitwagen)
      if iUnitType == gc.getInfoTypeForString("UNIT_CHARIOT"):
        if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
          self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_WAR_CHARIOT"))
          return True

      # Ab Veteran Status
      if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")):

        # ROME
        if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME") \
        or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
          # Principes oder Hastati -> Triarii
          if iUnitType == gc.getInfoTypeForString("UNIT_PRINCIPES2") \
          or iUnitType == gc.getInfoTypeForString("UNIT_HASTATI2") :
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_TRIARII2"))
              return True
          # Triari, Legion or Legion 2 -> Praetorians or Cohortes Praetoriae
          elif iUnitType == gc.getInfoTypeForString("UNIT_TRIARII2") \
          or iUnitType == gc.getInfoTypeForString("UNIT_LEGION") \
          or iUnitType == gc.getInfoTypeForString("UNIT_LEGION2") :
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BERUFSSOLDATEN")):
              iRand = 0
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LORICA_SEGMENTATA")):
                iRand = self.myRandom(2, None)
              if iRand == 1:
                self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
                return True
              else:
                self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_PRAETORIAN"))
                return True
          # Praetorian -> Praetorian Garde
          elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN") or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2") :
            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LORICA_SEGMENTATA")):
                self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_PRAETORIAN3"))
                return True
          # Hasta Warrior -> Celeres
          elif iUnitType == gc.getInfoTypeForString("UNIT_HASTATI1") :
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_CELERES"))
              return True
          # Archer -> Reflex
          elif iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_ROME") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ARCHER_LEGION"))
            return True

        # GREEKS
        elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") \
        or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
        or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") \
        or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
          # Hoplit -> Elite Hoplit
          if iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ELITE_HOPLIT"))
            return True
          # Archer -> Reflex
          elif iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"))
            return True

        # SPARTA
        if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
          # Sparta Hoplit -> Elite Hoplit
          if iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT_SPARTA") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_SPARTAN"))
            return True

        # PERSIA
        elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
          # Unsterblich -> Garde
          if iUnitType == gc.getInfoTypeForString("UNIT_UNSTERBLICH") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_UNSTERBLICH_2"))
            return True

        # MACEDONIA
        elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
          #  Hypaspist oder Pezhetairoi -> Argyraspidai
          if iUnitType == gc.getInfoTypeForString("UNIT_HYPASPIST") \
          or iUnitType == gc.getInfoTypeForString("UNIT_SARISSA_MACEDON") :
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ARGYRASPIDAI"))
              return True
          #  Argyraspidai -> Argyraspidai 2 (Silberschild)
          elif iUnitType == gc.getInfoTypeForString("UNIT_ARGYRASPIDAI") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ARGYRASPIDAI2"))
            return True
          # Archer -> Reflex
          elif iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"))
            return True

        # EGYPT
        elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
          # Gaufuerst -> Pharaonengarde
          if iUnitType == gc.getInfoTypeForString("UNIT_GAUFUERST") :
            self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_PHARAONENGARDE"))
            return True

        # Schildtraeger
        if iUnitType == gc.getInfoTypeForString("UNIT_SCHILDTRAEGER") :

          if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_GAUFUERST"))
              return True

          elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_NUBIA") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_NUBIAFUERST"))
              return True

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_MACCABEE"))
              return True

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GALLIEN") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BRITEN") :
                self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_STAMMESFUERST"))
                return True
            elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_DAKER") :
                self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_FUERST_DAKER"))
                return True

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ASSYRIA") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL") \
            or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SUMERIA") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_SYRIAN_GARDE"))
              return True

        # Axeman
        elif iUnitType == gc.getInfoTypeForString("UNIT_AXEMAN2") :

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"))
              return True

        # Spearman
        elif iUnitType == gc.getInfoTypeForString("UNIT_SPEARMAN") :

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_ARMOR")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"))
              return True
            elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_RADSCHA"))
              return True

          if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
            if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_GERMAN_HARIER"))
              return True

        # Swordsman
        elif iUnitType == gc.getInfoTypeForString("UNIT_SWORDSMAN") :

          if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA") :
              self.doUpgradeVeteran_AI(pUnit, gc.getInfoTypeForString("UNIT_INDIAN_NAYAR"))
              return True

        # Allgemein Veteran -> Reservist
        elif 1 == self.myRandom(20, None):
          if self.doReservist_AI(pUnit):
            return True

      # ---- ENDE Veteran -------

# Terrain Promos - Ausbildner / Trainer (in City)
      if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN5")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA5")) \
      or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE5")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF5")) \
      or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT5")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5")) \
      or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE5")) \
      or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION4")):
        self.doAISettleTrainer(pUnit)

      # wenn die Einheit per AISettleTrainer gekillt wurde, dann raus hier
      if pUnit.isNone(): return True


# BEGIN Unit -> Horse UPGRADE
      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_2")):
        pPlot = pUnit.plot()

        # self.lUnitAuxiliar: globale Variable
        if iUnitType in self.lUnitAuxiliar \
        or iUnitType == gc.getInfoTypeForString("UNIT_SCHILDTRAEGER") \
        or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN") \
        or iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE") :

          bSearchPlot = False

          if iUnitType in self.lUnitAuxiliar and pTeam.isHasTech(gc.getInfoTypeForString("TECH_HUFEISEN")):
              iNewUnitType = gc.getInfoTypeForString('UNIT_AUXILIAR_HORSE')
              bSearchPlot = True
          elif iUnitType == gc.getInfoTypeForString("UNIT_SCHILDTRAEGER"):
            if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CAVALRY")):
              iNewUnitType = gc.getInfoTypeForString('UNIT_HEAVY_HORSEMAN')
              bSearchPlot = True
          else:
            TechHorse3 = gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_3")
            if pTeam.isHasTech(TechHorse3):
              if iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN"):
                iNewUnitType = gc.getInfoTypeForString('UNIT_PRAETORIAN_RIDER')
              if iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"):
                iNewUnitType = gc.getInfoTypeForString('UNIT_MOUNTED_SACRED_BAND_CARTHAGE')
              bSearchPlot = True

          # Pferd suchen
          if bSearchPlot:
            bUpgrade = False
            UnitHorse = gc.getInfoTypeForString('UNIT_HORSE')
            iRange = pPlot.getNumUnits()
            for iUnit in range (iRange):
              if pPlot.getUnit(iUnit).getUnitType() == UnitHorse and pPlot.getUnit(iUnit).getOwner() == pUnit.getOwner():
                bUpgrade = True
                #pPlot.getUnit(iUnit).doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                pPlot.getUnit(iUnit).kill(1,pPlot.getUnit(iUnit).getOwner())
                break

            if bUpgrade:
              iX = pUnit.getX()
              iY = pUnit.getY()
              # Create a new unit
              NewUnit = gc.getPlayer(pUnit.getOwner()).initUnit(iNewUnitType, iX, iY, UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)
              NewUnit.setExperience(pUnit.getExperience(), -1)
              NewUnit.setLevel(pUnit.getLevel())
              NewUnit.changeMoves(90)
              NewUnit.setDamage(pUnit.getDamage(), False)
              if pUnit.getName() != gc.getUnitInfo(iUnitType).getText():
                UnitName = pUnit.getName()
                UnitName = re.sub(" \(.*?\)","",UnitName)
                NewUnit.setName(UnitName)
              # Check its promotions
              iRange = gc.getNumPromotionInfos()
              for iPromotion in range(iRange):
                # init all promotions the unit had
                if (pUnit.isHasPromotion(iPromotion)):
                  NewUnit.setHasPromotion(iPromotion, True)
              #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
              pUnit.kill(1,pUnit.getOwner())
              return True
# END Unit -> Horse UPGRADE

# Slaves settle into city
      if iUnitType == gc.getInfoTypeForString("UNIT_SLAVE") and iOwner != gc.getBARBARIAN_PLAYER():
        pPlot = pUnit.plot()
        if pPlot.isCity() and pPlot.getOwner() == iOwner:

          pCity = pPlot.getPlotCity()
          if not pCity.isNone() and pCity.getID() not in self.PAE_AI_Cities_Slaves:

              iCityPop = pCity.getPopulation()
              iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 15
              iCitySlaves = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE = 16
              iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE = 17
              iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE = 18

              # Zuerst Sklavenmarkt bauen
              bSlaveMarket = False
              iBuilding1 = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
              iBuilding2 = gc.getInfoTypeForString("BUILDING_STADT")
              if not pCity.isHasBuilding(iBuilding1):
                if pCity.isHasBuilding(iBuilding2):
                  pCity.setNumRealBuilding(iBuilding1,1)
                  pUnit.kill(1,pUnit.getOwner())
                  return True
              else: bSlaveMarket = True

              # Weitere Cities auf Sklavenmarkt checken und Sklaven zuerst dort hinschicken
              if iOwner != gc.getBARBARIAN_PLAYER() and lCities > len(self.PAE_AI_Cities_Slavemarket):
               if self.myRandom(10, None) < 2:
                for lCity in lCities:
                  xCity = pOwner.getCity( lCity.getID() )

                  if xCity.getID() not in self.PAE_AI_Cities_Slavemarket:

                    # PAE AI City Instance
                    self.PAE_AI_Cities_Slavemarket.append(xCity.getID())

                    if not xCity.isHasBuilding(iBuilding1):
                      if xCity.isHasBuilding(iBuilding2):
                        pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, xCity.getX(), xCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pPlot, pUnit)
                        return True


              # Sklaven bringen Unzufriedenheit und werden beruecksichtigt
              iHappiness = pCity.happyLevel() - pCity.unhappyLevel(0)

              iCitySlavesAll = iCitySlaves + iCitySlavesFood + iCitySlavesProd

              # Civics that prevent or increase revolt - not necessary: 5% penalty makes no difference
#              if pUnitOwner.isCivic(11): iCalc = -1
#              elif pUnitOwner.isCivic(13) or pUnitOwner.isCivic(14): iCalc = 1
#              else: iCalc = 0

              ## TEST ##
              #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("AI Slave",iCitySlavesAll)), None, 2, None, ColorTypes(10), 0, 0, False, False)


              bHasGladTech = False
              iNumGlads = 0
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GLADIATOR")):
                bHasGladTech = True
                # Gladidatorenplatz reservieren fuer Glads aber nur ab Pop 6
                if iCityPop > 5: iNumGlads = 3

              # settle as slaves
              if pCity.happyLevel() > iCitySlavesAll:
                if iCitySlavesAll + iCityGlads + iNumGlads <= iCityPop:
                  if iCitySlavesFood == 0: pCity.changeFreeSpecialistCount(17, 1)
                  elif iCitySlavesProd == 0: pCity.changeFreeSpecialistCount(18, 1)
                  elif iCitySlavesFood < iCitySlavesProd or iCitySlavesFood < iCitySlaves: pCity.changeFreeSpecialistCount(17, 1)
                  elif iCitySlavesProd < iCitySlavesFood or iCitySlavesProd < iCitySlaves: pCity.changeFreeSpecialistCount(18, 1)
                  else: pCity.changeFreeSpecialistCount(16, 1)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

                # settle as gladiators
                if bHasGladTech:
                  if iCitySlavesAll + iCityGlads <= iCityPop:
                    pCity.changeFreeSpecialistCount(15, 1) # Gladiator = 15
                    pUnit.kill(1,pUnit.getOwner())
                    return True

              # Priority 1 - Schule

              # assign to school
              # BUILDING_GYMNASION hat bereits +5 Forschung
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KUNST")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
              if pCity.isHasBuilding(iBuilding1):
                iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_RESEARCH, iBuilding1)
                if iCulture < 5:
                  iNewCulture = iCulture + 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iNewCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # assign to library
              # BUILDING_LIBRARY hat bereits +5 Forschung
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KUNST")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
              if pCity.isHasBuilding(iBuilding1):
                iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_RESEARCH, iBuilding1)
                if iCulture < 5:
                  iNewCulture = iCulture + 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_RESEARCH, iNewCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 2 - Theater

              # assign to the theatre
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_DRAMA")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_THEATER')
              if pCity.isHasBuilding(iBuilding1):
                iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
                if iCulture < 3:
                  iNewCulture = iCulture + 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iNewCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 3 - Manufaktur

              # assign to manufactory
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANUFAKTUREN")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
              if pCity.isHasBuilding(iBuilding1):
                iFood = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0)
                iProd = pCity.getBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1)
                if iProd <= iFood and iProd < 5:
                  iProd += 1
                  pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1, iProd)
                  pUnit.kill(1,pUnit.getOwner())
                  return True
                elif iFood < 5:
                  iFood += 1
                  pCity.setBuildingYieldChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0, iFood)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 4 - Bordell

              # assign to the house of pleasure (bordell/freudenhaus)
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_SYNKRETISMUS")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
              if pCity.isHasBuilding(iBuilding1):
                iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
                if iCulture < 5:
                  iNewCulture = iCulture + 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iNewCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 5 - Palace

              # assign to the Palace  10%
              iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
              if pCity.isHasBuilding(iBuilding1):
                if 1 == self.myRandom(10, None):
                  iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
                  iNewCulture = iCulture + 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iNewCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 6 - Temples

              # assign to a temple 10%
              if 1 == self.myRandom(10, None):
                iBuilding1 = gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE")
                iBuilding2 = gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE")
                iBuilding3 = gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE")
                iBuilding4 = gc.getInfoTypeForString("BUILDING_ROME_TEMPLE")
                iBuilding5 = gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE")
                iBuilding6 = gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE")
                iBuilding7 = gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE")
                iBuilding8 = gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
                TempleArray = []
                if pCity.isHasBuilding(iBuilding1): TempleArray.append(iBuilding1)
                if pCity.isHasBuilding(iBuilding2): TempleArray.append(iBuilding2)
                if pCity.isHasBuilding(iBuilding3): TempleArray.append(iBuilding3)
                if pCity.isHasBuilding(iBuilding4): TempleArray.append(iBuilding4)
                if pCity.isHasBuilding(iBuilding5): TempleArray.append(iBuilding5)
                if pCity.isHasBuilding(iBuilding6): TempleArray.append(iBuilding6)
                if pCity.isHasBuilding(iBuilding7): TempleArray.append(iBuilding7)
                if pCity.isHasBuilding(iBuilding8): TempleArray.append(iBuilding8)

                if len(TempleArray) > 0:
                  iBuilding = self.myRandom(len(TempleArray), None)
                  iCulture = pCity.getBuildingCommerceByBuilding(2, TempleArray[iBuilding])
                  iCulture += 1
                  pCity.setBuildingCommerceChange(gc.getBuildingInfo(TempleArray[iBuilding]).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, iCulture)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 7 - Feuerwehr

              # assign to the fire station 10%
              #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_FEUERWEHR")):
              iBuilding1 = gc.getInfoTypeForString('BUILDING_FEUERWEHR')
              if pCity.isHasBuilding(iBuilding1):
                iHappyiness = pCity.getBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType())
                if iHappyiness < 3:
                  iHappyiness += 1
                  pCity.setBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType(), iHappyiness)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

              # Priority 8 - Sell slave 25%
              if bSlaveMarket:
                if self.myRandom(4, None) == 1:
                  pUnit.getGroup().pushMission(MissionTypes.MISSION_TRADE, 0, 0, 0, False, False, MissionAITypes.NO_MISSIONAI, pPlot, pUnit)
                  return True

              # PAE AI City Instance
              self.PAE_AI_Cities_Slaves.append(pCity.getID())


# Horses - create stables
      if iUnitType == gc.getInfoTypeForString("UNIT_HORSE"):
       if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PFERDEZUCHT")):

         pPlot = pUnit.plot()
         if pPlot.isCity() and pPlot.getOwner() == iOwner:

          if lCities > len(self.PAE_AI_Cities_Horses):
           pCity = pPlot.getPlotCity()
           if not pCity.isNone() and pCity.getID() not in self.PAE_AI_Cities_Horses:

            # Zuerst hier Pferdestall bauen
            iBuilding1 = gc.getInfoTypeForString("BUILDING_STABLE")
            iBuilding2 = gc.getInfoTypeForString("BUILDING_KOLONIE")
            if not pCity.isHasBuilding(iBuilding1):
              if pCity.isHasBuilding(iBuilding2):
                pCity.setNumRealBuilding(iBuilding1,1)
                pUnit.kill(1,pUnit.getOwner())
                return True

            # PAE AI City Horse Instance
            self.PAE_AI_Cities_Horses.append(pCity.getID())


            # Weitere Cities auf Stallungen checken und Pferd dort hinschicken
            if iOwner != gc.getBARBARIAN_PLAYER():
             for lCity in lCities:
              xCity = pOwner.getCity( lCity.getID() )
              if xCity.getID() not in self.PAE_AI_Cities_Horses:

                # PAE AI City Horse Instance
                self.PAE_AI_Cities_Horses.append(xCity.getID())

                if not xCity.isHasBuilding(iBuilding1):
                  if xCity.isHasBuilding(iBuilding2):
                    pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, xCity.getX(), xCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pPlot, pUnit)
                    return True


# Auswanderer / Emigrant -> zu schwachen Staedten
      if iUnitType == gc.getInfoTypeForString("UNIT_EMIGRANT") and iOwner != gc.getBARBARIAN_PLAYER():

        pPlot = pUnit.plot()
        if pPlot.isCity() and pPlot.getOwner() == iOwner:

          iCityX = -1
          iCityPop = 0
          iRange = len(lCities)
          for i in range(iRange):
            iPop = pOwner.getCity(lCities[i].getID()).getPopulation()
            if iCityX == -1 or iPop < iCityPop:
              iCityPop = iPop
              iCityX = i

          if iCityX > -1:
            pCity = pOwner.getCity(lCities[iCityX].getID())
            if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
              pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
            else:
              pCity.changePopulation(1)
              pUnit.kill(1,pUnit.getOwner())
            return True

# Beutegold / Treasure / Goldkarren -> zur Hauptstadt
      if iUnitType == gc.getInfoTypeForString("UNIT_GOLDKARREN") and iOwner != gc.getBARBARIAN_PLAYER():
        pCapital = pOwner.getCapitalCity()
        lCities = PyPlayer(iOwner).getCityList()
        if pCapital.getID() == -1: pCity = pOwner.getCity(lCities[0].getID())
        else: pCity = pCapital
        if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
          pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
          return True
        else:
          if pCapital.getID() == pCity.getID():
            iGold = 80 + self.myRandom(71, None)
            pOwner.changeGold(iGold)
            pUnit.kill(1,pUnit.getOwner())
            #iBuilding = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_PALACE')
            #pCity.setBuildingCommerceChange(gc.getBuildingInfo(iBuilding).getBuildingClassType(), CommerceTypes.COMMERCE_CULTURE, 1)
          else:
            pUnit.finishMoves()
          return True

# Trojanisches Pferd
      if iUnitType == gc.getInfoTypeForString("UNIT_TROJAN_HORSE") and iOwner != gc.getBARBARIAN_PLAYER():
        # 1: wenn das pferd in der naehe einer feindlichen stadt ist und diese ueber 100% defense hat -> anwenden

        iX = pUnit.getX()
        iY = pUnit.getY()

        for x in range(3):
            for y in range(3):
              loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
              if loopPlot != None and not loopPlot.isNone():
                if loopPlot.isCity():
                  pCity = loopPlot.getPlotCity()
                  if pCity.getOwner() != pUnit.getOwner():
                    if gc.getTeam(pUnit.getOwner()).isAtWar(gc.getPlayer(pCity.getOwner()).getTeam()):
                      iDamage = pCity.getDefenseModifier(0)
                      if iDamage > 100:
                        pCity.changeDefenseDamage(iDamage)
                        #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                        pUnit.kill(1,pUnit.getOwner())
                        return True
      # -----------------

# Legend can become a Great General
      if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT6")) and iOwner != gc.getBARBARIAN_PLAYER():
          if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_LEADER")):
            pPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
            if pPlot.getOwner() == iOwner:

                 pPlayer.initUnit(gc.getInfoTypeForString("UNIT_GREAT_GENERAL"), pUnit.getX(), pUnit.getY(), UnitAITypes.NO_UNITAI, DirectionTypes.DIRECTION_SOUTH)

                 iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT4")
                 if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)
                 iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT5")
                 if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)
                 iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT6")
                 if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)
                 iPromo = gc.getInfoTypeForString("PROMOTION_HERO")
                 if pUnit.isHasPromotion(iPromo): pUnit.setHasPromotion(iPromo, False)

                 # Reduce XP
                 pUnit.setExperience(pUnit.getExperience() / 2, -1)

                 #if pUnit.getLevel() > 3:
                 #  pUnit.setLevel(pUnit.getLevel() - 3)
                 #else:
                 #  pUnit.setLevel(1)

      # -----------------

# Kaufbare Promotions ------------------

      # Kauf einer edlen Ruestung (Promotion)
      pPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
      if pPlot.isCity():
        if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_ARMOR")):
          iPromo = gc.getInfoTypeForString("PROMOTION_EDLE_RUESTUNG")
          iPromoPrereq = gc.getInfoTypeForString("PROMOTION_COMBAT5")
          if not pUnit.isHasPromotion(iPromo) and pUnit.isHasPromotion(iPromoPrereq):
            iCombatArray = []
            iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_NAVAL"))
            iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SIEGE"))
            iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_RECON"))
            iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_HEALER"))
            iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_ARCHER"))
            iCombatArray.append(gc.getInfoTypeForString("NONE"))
            if pUnit.getUnitCombatType() not in iCombatArray and pUnit.getUnitCombatType() != None:
              iUnitArray = []
              iUnitArray.append(gc.getInfoTypeForString("UNIT_WARRIOR"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_HUNTER"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_KURZSCHWERT"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_MERC_HORSEMAN"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_HORSEMAN"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_CARTHAGE_NUMIDIAN_CAVALRY"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_GALLIER_GILDE"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
              iUnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
              if pUnit.getUnitType() not in iUnitArray:
                pCity = pPlot.getPlotCity()
                iBuilding = gc.getInfoTypeForString("BUILDING_FORGE")
                bonus1 = gc.getInfoTypeForString("BONUS_OREICHALKOS")
                bonus2 = gc.getInfoTypeForString("BONUS_MESSING")
                if pCity.isHasBuilding(iBuilding) and (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2)):
                  pOwner = gc.getPlayer(iOwner)
                  iCost = gc.getUnitInfo(pUnit.getUnitType()).getCombat() * 12
                  if iCost <= 0: iCost = 180
                  if pOwner.getGold() > iCost*3:
                    # AI soll zu 25% die Ruestung kaufen
                    if self.myRandom(4, None) == 1:
                      pOwner.changeGold(-iCost)
                      pUnit.setHasPromotion(iPromo, True)
                      pUnit.finishMoves()
                      return True

# Kauf eines Wellen-Oils (Promotion)
      pPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
      if pPlot.isCity():
       if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_KUESTE")):
        if pUnit.getUnitCombatType() == gc.getInfoTypeForString('UNITCOMBAT_NAVAL'):
         pCity = pPlot.getPlotCity()
         bonus1 = gc.getInfoTypeForString("BONUS_OLIVES")
         iPromo = gc.getInfoTypeForString("PROMOTION_OIL_ON_WATER")
         iPromo2 = gc.getInfoTypeForString("PROMOTION_COMBAT2")

         if not pUnit.isHasPromotion(iPromo) and pUnit.isHasPromotion(iPromo2) and pCity.hasBonus(bonus1):
            pOwner = gc.getPlayer(iOwner)
            iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost()
            if iCost <= 0: iCost = 180
            if pOwner.getGold() > iCost:
              # AI soll zu 25% das Oil kaufen
                pOwner.changeGold(-iCost)
                pUnit.setHasPromotion(iPromo, True)
                pUnit.finishMoves()
                return True

      # -------------------

    return False

  def AI_doWar(self,argsList):
    eTeam = argsList[0]
    return False

  def AI_doDiplo(self,argsList):
    ePlayer = argsList[0]
    return False

  def calculateScore(self,argsList):
    ePlayer = argsList[0]
    bFinal = argsList[1]
    bVictory = argsList[2]

    iPopulationScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getPopScore(), gc.getGame().getInitPopulation(), gc.getGame().getMaxPopulation(), gc.getDefineINT("SCORE_POPULATION_FACTOR"), True, bFinal, bVictory)
    iLandScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getLandScore(), gc.getGame().getInitLand(), gc.getGame().getMaxLand(), gc.getDefineINT("SCORE_LAND_FACTOR"), True, bFinal, bVictory)
    iTechScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getTechScore(), gc.getGame().getInitTech(), gc.getGame().getMaxTech(), gc.getDefineINT("SCORE_TECH_FACTOR"), True, bFinal, bVictory)
    iWondersScore = CvUtil.getScoreComponent(gc.getPlayer(ePlayer).getWondersScore(), gc.getGame().getInitWonders(), gc.getGame().getMaxWonders(), gc.getDefineINT("SCORE_WONDER_FACTOR"), False, bFinal, bVictory)
    return int(iPopulationScore + iLandScore + iWondersScore + iTechScore)

  def doHolyCity(self):
    # Reli-Gruendungsfehler rausfiltern
    iTech = gc.getInfoTypeForString("TECH_LIBERALISM")
    bTech = False
    iRange = gc.getMAX_PLAYERS()
    for i in range (iRange):
      pTeam = gc.getTeam(gc.getPlayer(i).getTeam())
      if pTeam.isHasTech(iTech):
        bTech = True
        break

    if not bTech: return True
    return False

  def doHolyCityTech(self,argsList):
    eTeam = argsList[0]
    ePlayer = argsList[1]
    eTech = argsList[2]
    bFirst = argsList[3]
    return False

  def doGold(self,argsList):
    ePlayer = argsList[0]
    return False

  def doResearch(self,argsList):
    ePlayer = argsList[0]
    return False

  def doGoody(self,argsList):
    ePlayer = argsList[0]
    pPlot = argsList[1]
    pUnit = argsList[2]
    return False

  def doGrowth(self,argsList):
    pCity = argsList[0]
    return False

  def doProduction(self,argsList):
    pCity = argsList[0]
    return False

  def doCulture(self,argsList):
    pCity = argsList[0]
    return False

  def doPlotCulture(self,argsList):
    pCity = argsList[0]
    bUpdate = argsList[1]
    ePlayer = argsList[2]
    iCultureRate = argsList[3]
    return False

  def doReligion(self,argsList):
    pCity = argsList[0]
    return False

  def cannotSpreadReligion(self,argsList):
    iOwner, iUnitID, iReligion, iX, iY = argsList[0]
    return False

  def doGreatPeople(self,argsList):
    pCity = argsList[0]
    return False

  def doMeltdown(self,argsList):
    pCity = argsList[0]
    return False

  def doReviveActivePlayer(self,argsList):
    "allows you to perform an action after an AIAutoPlay"
    iPlayer = argsList[0]
    return False

  def doPillageGold(self, argsList):
    "controls the gold result of pillaging"
    pPlot = argsList[0]
    pUnit = argsList[1]

    iPillageGold = 0
    iPillageGold = self.myRandom(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), None)
    iPillageGold += self.myRandom(gc.getImprovementInfo(pPlot.getImprovementType()).getPillageGold(), None)

    iPillageGold += (pUnit.getPillageChange() * iPillageGold) / 100

    return iPillageGold

  def doCityCaptureGold(self, argsList):
    "controls the gold result of capturing a city"

    pOldCity = argsList[0]

    iCaptureGold = 0

    iCaptureGold += gc.getDefineINT("BASE_CAPTURE_GOLD")
    iCaptureGold += (pOldCity.getPopulation() * gc.getDefineINT("CAPTURE_GOLD_PER_POPULATION"))
    iCaptureGold += self.myRandom(gc.getDefineINT("CAPTURE_GOLD_RAND1"), None)
    iCaptureGold += self.myRandom(gc.getDefineINT("CAPTURE_GOLD_RAND2"), None)

    if (gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS") > 0):
      iCaptureGold *= cyIntRange((CyGame().getGameTurn() - pOldCity.getGameTurnAcquired()), 0, gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS"))
      iCaptureGold /= gc.getDefineINT("CAPTURE_GOLD_MAX_TURNS")

    return iCaptureGold

  def citiesDestroyFeatures(self,argsList):
    iX, iY= argsList
    return True

  def canFoundCitiesOnWater(self,argsList):
    iX, iY= argsList
    return False

  def doCombat(self,argsList):
    pSelectionGroup, pDestPlot = argsList
    return False

  def getConscriptUnitType(self, argsList):
    iPlayer = argsList[0]
    iConscriptUnitType = -1 #return this with the value of the UNIT TYPE you want to be conscripted, -1 uses default system

    return iConscriptUnitType

  def getCityFoundValue(self, argsList):
    iPlayer, iPlotX, iPlotY = argsList
    iFoundValue = -1 # Any value besides -1 will be used

    return iFoundValue

  def canPickPlot(self, argsList):
    pPlot = argsList[0]
    return True

  def getUnitCostMod(self, argsList):
    iPlayer, iUnit = argsList
    iCostMod = -1 # Any value > 0 will be used

    if iPlayer != -1:
      pPlayer = gc.getPlayer(iPlayer)

      # Nomads (TEST)
      #if pPlayer.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_HUNNEN"): return 0

      #Trait Aggressive: Einheiten 20% billiger / units 20% cheaper
      if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")) and gc.getUnitInfo(iUnit).isMilitaryHappiness(): iCostMod = 80

    return iCostMod

  def getBuildingCostMod(self, argsList):
    iPlayer, iCityID, iBuilding = argsList
    pBuildingClass = gc.getBuildingClassInfo(gc.getBuildingInfo(iBuilding).getBuildingClassType())

    iCostMod = -1 # Any value > 0 will be used
    # Trait Builder/Bauherr: buildings 15% cheaper, wonders 25%
    if iPlayer != -1:
        pPlayer = gc.getPlayer(iPlayer)
        #pCity = pPlayer.getCity(iCityID)
        if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_INDUSTRIOUS")):
            if pBuildingClass.getMaxGlobalInstances() == -1 and pBuildingClass.getMaxTeamInstances() == -1 and pBuildingClass.getMaxPlayerInstances() == -1: iCostMod = 85
            else: iCostMod = 75
    #--
    return iCostMod

  def canUpgradeAnywhere(self, argsList):
    pUnit = argsList

    bCanUpgradeAnywhere = 0

    return bCanUpgradeAnywhere

  def getWidgetHelp(self, argsList):
    eWidgetType, iData1, iData2, bOption = argsList

## ---------------------- ##
##   Platy WorldBuilder   ##
## ---------------------- ##
## Religion Screen ##
    if eWidgetType == WidgetTypes.WIDGET_HELP_RELIGION:
      if iData1 == -1:
        return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
## Platy WorldBuilder ##
    elif eWidgetType == WidgetTypes.WIDGET_PYTHON:
      if iData1 == 1027:
        return CyTranslator().getText("TXT_KEY_WB_PLOT_DATA",())
      elif iData1 == 1028:
        return gc.getGameOptionInfo(iData2).getHelp()
      elif iData1 == 1029:
        if iData2 == 0:
          sText = CyTranslator().getText("TXT_KEY_WB_PYTHON", ())
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onFirstContact"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onChangeWar"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onVassalState"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCityAcquired"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCityBuilt"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCultureExpansion"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onGoldenAge"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onEndGoldenAge"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onGreatPersonBorn"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onPlayerChangeStateReligion"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionFounded"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionSpread"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onReligionRemove"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationFounded"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationSpread"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onCorporationRemove"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitCreated"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitLost"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onUnitPromoted"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onBuildingBuilt"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onProjectBuilt"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onTechAcquired"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onImprovementBuilt"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onImprovementDestroyed"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onRouteBuilt"
          sText += "\n" + CyTranslator().getText("[ICON_BULLET]", ()) + "onPlotRevealed"
          return sText
        elif iData2 == 1:
          return CyTranslator().getText("TXT_KEY_WB_PLAYER_DATA",())
        elif iData2 == 2:
          return CyTranslator().getText("TXT_KEY_WB_TEAM_DATA",())
        elif iData2 == 3:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_TECH",())
        elif iData2 == 4:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROJECT",())
        elif iData2 == 5:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_UNIT", ()) + " + " + CyTranslator().getText("TXT_KEY_CONCEPT_CITIES", ())
        elif iData2 == 6:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION",())
        elif iData2 == 7:
          return CyTranslator().getText("TXT_KEY_WB_CITY_DATA2",())
        elif iData2 == 8:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING",())
        elif iData2 == 9:
          return "Platy Builder\nVersion: 4.10"
        elif iData2 == 10:
          return CyTranslator().getText("TXT_KEY_CONCEPT_EVENTS",())
        elif iData2 == 11:
          return CyTranslator().getText("TXT_KEY_WB_RIVER_PLACEMENT",())
        elif iData2 == 12:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_IMPROVEMENT",())
        elif iData2 == 13:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BONUS",())
        elif iData2 == 14:
          return CyTranslator().getText("TXT_KEY_WB_PLOT_TYPE",())
        elif iData2 == 15:
          return CyTranslator().getText("TXT_KEY_CONCEPT_TERRAIN",())
        elif iData2 == 16:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_ROUTE",())
        elif iData2 == 17:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_FEATURE",())
        elif iData2 == 18:
          return CyTranslator().getText("TXT_KEY_MISSION_BUILD_CITY",())
        elif iData2 == 19:
          return CyTranslator().getText("TXT_KEY_WB_ADD_BUILDINGS",())
        elif iData2 == 20:
          return CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_RELIGION",())
        elif iData2 == 21:
          return CyTranslator().getText("TXT_KEY_CONCEPT_CORPORATIONS",())
        elif iData2 == 22:
          return CyTranslator().getText("TXT_KEY_ESPIONAGE_CULTURE",())
        elif iData2 == 23:
          return CyTranslator().getText("TXT_KEY_PITBOSS_GAME_OPTIONS",())
        elif iData2 == 24:
          return CyTranslator().getText("TXT_KEY_WB_SENSIBILITY",())
        elif iData2 == 27:
          return CyTranslator().getText("TXT_KEY_WB_ADD_UNITS",())
        elif iData2 == 28:
          return CyTranslator().getText("TXT_KEY_WB_TERRITORY",())
        elif iData2 == 29:
          return CyTranslator().getText("TXT_KEY_WB_ERASE_ALL_PLOTS",())
        elif iData2 == 30:
          return CyTranslator().getText("TXT_KEY_WB_REPEATABLE",())
        elif iData2 == 31:
          return CyTranslator().getText("TXT_KEY_PEDIA_HIDE_INACTIVE", ())
        elif iData2 == 32:
          return CyTranslator().getText("TXT_KEY_WB_STARTING_PLOT", ())
        elif iData2 == 33:
          return CyTranslator().getText("TXT_KEY_INFO_SCREEN", ())
        elif iData2 == 34:
          return CyTranslator().getText("TXT_KEY_CONCEPT_TRADE", ())
      elif iData1 > 1029 and iData1 < 1040:
        if iData1 %2:
          return "-"
        return "+"
      elif iData1 == 6782:
        return CyGameTextMgr().parseCorporationInfo(iData2, False)
      elif iData1 == 6785:
        return CyGameTextMgr().getProjectHelp(iData2, False, CyCity())
      elif iData1 == 6787:
        return gc.getProcessInfo(iData2).getDescription()
      elif iData1 == 6788:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        return gc.getRouteInfo(iData2).getDescription()
## City Hover Text ##
      elif iData1 > 7199 and iData1 < 7300:
        iPlayer = iData1 - 7200
        pPlayer = gc.getPlayer(iPlayer)
        pCity = pPlayer.getCity(iData2)
        if CyGame().GetWorldBuilderMode():
          sText = "<font=3>"
          if pCity.isCapital():
            sText += CyTranslator().getText("[ICON_STAR]", ())
          elif pCity.isGovernmentCenter():
            sText += CyTranslator().getText("[ICON_SILVER_STAR]", ())
          sText += u"%s: %d<font=2>" %(pCity.getName(), pCity.getPopulation())
          sTemp = ""
          if pCity.isConnectedToCapital(iPlayer):
            sTemp += CyTranslator().getText("[ICON_TRADE]", ())
          for i in xrange(gc.getNumReligionInfos()):
            if pCity.isHolyCityByType(i):
              sTemp += u"%c" %(gc.getReligionInfo(i).getHolyCityChar())
            elif pCity.isHasReligion(i):
              sTemp += u"%c" %(gc.getReligionInfo(i).getChar())

          for i in xrange(gc.getNumCorporationInfos()):
            if pCity.isHeadquartersByType(i):
              sTemp += u"%c" %(gc.getCorporationInfo(i).getHeadquarterChar())
            elif pCity.isHasCorporation(i):
              sTemp += u"%c" %(gc.getCorporationInfo(i).getChar())
          if len(sTemp) > 0:
            sText += "\n" + sTemp

          iMaxDefense = pCity.getTotalDefense(False)
          if iMaxDefense > 0:
            sText += u"\n%s: " %(CyTranslator().getText("[ICON_DEFENSE]", ()))
            iCurrent = pCity.getDefenseModifier(False)
            if iCurrent != iMaxDefense:
              sText += u"%d/" %(iCurrent)
            sText += u"%d%%" %(iMaxDefense)

          sText += u"\n%s: %d/%d" %(CyTranslator().getText("[ICON_FOOD]", ()), pCity.getFood(), pCity.growthThreshold())
          iFoodGrowth = pCity.foodDifference(True)
          if iFoodGrowth != 0:
            sText += u" %+d" %(iFoodGrowth)

          if pCity.isProduction():
            sText += u"\n%s:" %(CyTranslator().getText("[ICON_PRODUCTION]", ()))
            if not pCity.isProductionProcess():
              sText += u" %d/%d" %(pCity.getProduction(), pCity.getProductionNeeded())
              iProduction = pCity.getCurrentProductionDifference(False, True)
              if iProduction != 0:
                sText += u" %+d" %(iProduction)
            sText += u" (%s)" %(pCity.getProductionName())

          iGPRate = pCity.getGreatPeopleRate()
          iProgress = pCity.getGreatPeopleProgress()
          if iGPRate > 0 or iProgress > 0:
            sText += u"\n%s: %d/%d %+d" %(CyTranslator().getText("[ICON_GREATPEOPLE]", ()), iProgress, pPlayer.greatPeopleThreshold(False), iGPRate)

          sText += u"\n%s: %d/%d (%s)" %(CyTranslator().getText("[ICON_CULTURE]", ()), pCity.getCulture(iPlayer), pCity.getCultureThreshold(), gc.getCultureLevelInfo(pCity.getCultureLevel()).getDescription())

          lTemp = []
          for i in xrange(CommerceTypes.NUM_COMMERCE_TYPES):
            iAmount = pCity.getCommerceRateTimes100(i)
            if iAmount <= 0: continue
            sTemp = u"%d.%02d%c" %(pCity.getCommerceRate(i), pCity.getCommerceRateTimes100(i)%100, gc.getCommerceInfo(i).getChar())
            lTemp.append(sTemp)
          if len(lTemp) > 0:
            sText += "\n"
            for i in xrange(len(lTemp)):
              sText += lTemp[i]
              if i < len(lTemp) - 1:
                sText += ", "

          iMaintenance = pCity.getMaintenanceTimes100()
          if iMaintenance != 0:
            sText += "\n" + CyTranslator().getText("[COLOR_WARNING_TEXT]", ()) + CyTranslator().getText("INTERFACE_CITY_MAINTENANCE", ()) + " </color>"
            sText += u"-%d.%02d%c" %(iMaintenance/100, iMaintenance%100, gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())

          lBuildings = []
          lWonders = []
          for i in xrange(gc.getNumBuildingInfos()):
            if pCity.isHasBuilding(i):
              Info = gc.getBuildingInfo(i)
              if isLimitedWonderClass(Info.getBuildingClassType()):
                lWonders.append(Info.getDescription())
              else:
                lBuildings.append(Info.getDescription())
          if len(lBuildings) > 0:
            lBuildings.sort()
            sText += "\n" + CyTranslator().getText("[COLOR_BUILDING_TEXT]", ()) + CyTranslator().getText("TXT_KEY_PEDIA_CATEGORY_BUILDING", ()) + ": </color>"
            for i in xrange(len(lBuildings)):
              sText += lBuildings[i]
              if i < len(lBuildings) - 1:
                sText += ", "
          if len(lWonders) > 0:
            lWonders.sort()
            sText += "\n" + CyTranslator().getText("[COLOR_SELECTED_TEXT]", ()) + CyTranslator().getText("TXT_KEY_CONCEPT_WONDERS", ()) + ": </color>"
            for i in xrange(len(lWonders)):
              sText += lWonders[i]
              if i < len(lWonders) - 1:
                sText += ", "
          sText += "</font>"
          return sText
## Religion Widget Text##
      elif iData1 == 7869:
        return CyGameTextMgr().parseReligionInfo(iData2, False)
## Building Widget Text##
      elif iData1 == 7870:
        return CyGameTextMgr().getBuildingHelp(iData2, False, False, False, None)
## Tech Widget Text##
      elif iData1 == 7871:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        return CyGameTextMgr().getTechHelp(iData2, False, False, False, False, -1)
## Civilization Widget Text##
      elif iData1 == 7872:
        iCiv = iData2 % 10000
        return CyGameTextMgr().parseCivInfos(iCiv, False)
## Promotion Widget Text##
      elif iData1 == 7873:
        return CyGameTextMgr().getPromotionHelp(iData2, False)
## Feature Widget Text##
      elif iData1 == 7874:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        iFeature = iData2 % 10000
        return CyGameTextMgr().getFeatureHelp(iFeature, False)
## Terrain Widget Text##
      elif iData1 == 7875:
        return CyGameTextMgr().getTerrainHelp(iData2, False)
## Leader Widget Text##
      elif iData1 == 7876:
        iLeader = iData2 % 10000
        return CyGameTextMgr().parseLeaderTraits(iLeader, -1, False, False)
## Improvement Widget Text##
      elif iData1 == 7877:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        return CyGameTextMgr().getImprovementHelp(iData2, False)
## Bonus Widget Text##
      elif iData1 == 7878:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        return CyGameTextMgr().getBonusHelp(iData2, False)
## Specialist Widget Text##
      elif iData1 == 7879:
        return CyGameTextMgr().getSpecialistHelp(iData2, False)
## Yield Text##
      elif iData1 == 7880:
        return gc.getYieldInfo(iData2).getDescription()
## Commerce Text##
      elif iData1 == 7881:
        return gc.getCommerceInfo(iData2).getDescription()
## Corporation Screen ##
      elif iData1 == 8201:
        return CyGameTextMgr().parseCorporationInfo(iData2, False)
## Military Screen ##
      elif iData1 == 8202:
        if iData2 == -1:
          return CyTranslator().getText("TXT_KEY_PEDIA_ALL_UNITS", ())
        return CyGameTextMgr().getUnitHelp(iData2, False, False, False, None)
      elif iData1 > 8299 and iData1 < 8400:
        iPlayer = iData1 - 8300
        pUnit = gc.getPlayer(iPlayer).getUnit(iData2)
        sText = CyGameTextMgr().getSpecificUnitHelp(pUnit, True, False)
        if CyGame().GetWorldBuilderMode():
          sText += "\n" + CyTranslator().getText("TXT_KEY_WB_UNIT", ()) + " ID: " + str(iData2)
          sText += "\n" + CyTranslator().getText("TXT_KEY_WB_GROUP", ()) + " ID: " + str(pUnit.getGroupID())
          sText += "\n" + "X: " + str(pUnit.getX()) + ", Y: " + str(pUnit.getY())
          sText += "\n" + CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()) + ": "  + str(pUnit.plot().getArea())
        return sText
## Civics Screen ##
      elif iData1 == 8205 or iData1 == 8206:
        sText = CyGameTextMgr().parseCivicInfo(iData2, False, True, False)
        if gc.getCivicInfo(iData2).getUpkeep() > -1:
          sText += "\n" + gc.getUpkeepInfo(gc.getCivicInfo(iData2).getUpkeep()).getDescription()
        else:
          sText += "\n" + CyTranslator().getText("TXT_KEY_CIVICS_SCREEN_NO_UPKEEP", ())
        return sText
## ---------------------- ##
## Platy WorldBuilder End ##
## ---------------------- ##

    iType = WidgetTypes.WIDGET_GENERAL
    if (eWidgetType == iType):
      #Inquisitor
      if iData1 == 665:
        return CyTranslator().getText("TXT_KEY_GODS_INQUISTOR_CLEANSE_MOUSE_OVER",())
      # Horse down
      if (iData1 == 666):
        return CyTranslator().getText("TXT_KEY_BUTTON_HORSE_DOWN",())
      # Horse up
      if (iData1 == 667):
        return CyTranslator().getText("TXT_KEY_BUTTON_HORSE_UP",())
      # Sklave -> Bordell
      if (iData1 == 668):
        return CyTranslator().getText("TXT_KEY_BUTTON_BORDELL",())
      # Sklave -> Gladiator
      if (iData1 == 669):
        return CyTranslator().getText("TXT_KEY_BUTTON_GLADIATOR",())
      # Sklave -> Theater
      if (iData1 == 670):
        return CyTranslator().getText("TXT_KEY_BUTTON_THEATRE",())

      # ID 671 PopUp Vassal01 und Vassal02

      # Auswanderer / Emigrant
      if (iData1 == 672):
        return CyTranslator().getText("TXT_KEY_BUTTON_EMIGRANT",())
      # Stadt aufloesen / disband city
      if (iData1 == 673):
        if bOption: return CyTranslator().getText("TXT_KEY_BUTTON_DISBAND_CITY",())
        else: return CyTranslator().getText("TXT_KEY_BUTTON_DISBAND_CITY2",())

      # ID 674 vergeben durch Hunnen-PopUp (CvScreensInterface - popupHunsPayment)

      # ID 675 vergeben durch Revolten-PopUp (CvScreensInterface - popupRevoltPayment)

      if (iData1 == 676):
        return CyTranslator().getText("TXT_KEY_MESSAGE_TECH_UNIT_1",())
      if (iData1 == 677):
        return CyTranslator().getText("TXT_KEY_MESSAGE_GOLDKARREN",())

      # ID 678 vergeben durch Provinz-PopUp (CvScreensInterface - popupProvinzPayment)

      # Sklave -> Schule
      if (iData1 == 679):
        return CyTranslator().getText("TXT_KEY_BUTTON_SCHULE",())

      # Sklave -> Manufaktur Nahrung
      if (iData1 == 680):
        return CyTranslator().getText("TXT_KEY_BUTTON_MANUFAKTUR_FOOD",())

      # Sklave -> Manufaktur Produktion
      if (iData1 == 681):
        return CyTranslator().getText("TXT_KEY_BUTTON_MANUFAKTUR_PROD",())

      # ID 682 PopUp Vassal03
      # ID 683 PopUp Vassal04
      # ID 684 PopUp Vassal05
      # ID 685 PopUp Vassal06
      # ID 686 PopUp Vassal07
      # ID 687 PopUp Vassal08
      # ID 688 PopUp Vassal09
      # ID 689 PopUp Vassal10
      # ID 690 PopUp Vassal11
      # ID 691 PopUp Vassal12

      # Sklave -> Palace
      if (iData1 == 692):
        return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2PALACE",())
      # Sklave -> Temple
      if (iData1 == 693):
        return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2TEMPLE",())
      # Sklave -> sell
      if (iData1 == 694):
        return CyTranslator().getText("TXT_KEY_BUTTON_SELL_SLAVE",())
      # Unit -> sell
      if (iData1 == 695):
        return CyTranslator().getText("TXT_KEY_BUTTON_SELL_UNIT",(iData2,))
      # Slave -> Feuerwehr
      if (iData1 == 696):
        return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2FEUERWEHR",())
      # Trojanisches Pferd
      if (iData1 == 697):
        return CyTranslator().getText("TXT_KEY_BUTTON_TROJAN_HORSE",())
      # Freie Unit bei Tech (Religion)
      if (iData1 == 698):
        return CyTranslator().getText("TXT_KEY_MESSAGE_TECH_UNIT_2",())
      # Unit -> Edle Ruestung
      if (iData1 == 699):
        if bOption: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_EDLE_RUESTUNG",(iData2,))
        elif iData2 == -1: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_EDLE_RUESTUNG_3",(iData2,))
        else: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_EDLE_RUESTUNG_2",(iData2,))
      # Pillage road
      if (iData1 == 700):
        return CyTranslator().getText("TXT_KEY_MESSAGE_PILLAGE_ROAD",())
      # Unit -> Wellen-Oil
      if (iData1 == 701):
        if bOption: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_WATER_OIL",(iData2,))
        elif iData2 == -1: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_WATER_OIL_3",(iData2,))
        else: return CyTranslator().getText("TXT_KEY_BUTTON_BUY_WATER_OIL_2",(iData2,))

      # ID 702 PopUp VassalTech HI-Hegemon
      # ID 703 PopUp VassalTech HI-Vassal
      # ID 704 PopUp Religionsaustreibung

      # Veteran -> Unit Upgrade eg. Principes + Hastati -> Triarii
      if (iData1 == 705 and iData2 > -1):
        return CyTranslator().getText("TXT_KEY_HELP_VETERAN2ELITE",(PyInfo.UnitInfo(iData2).getDescription(),gc.getUnitCombatInfo(PyInfo.UnitInfo(iData2).getUnitCombatType()).getDescription(), gc.getUnitInfo(iData2).getCombat(), gc.getUnitInfo(iData2).getMoves(), gc.getUnitInfo(iData2).getExtraCost() ))

      # ID 706 PopUp Renegade City (keep or raze)

      # PopUp Hire/Assign Mercenaries (City Button)
      if (iData1 == 707):
        return CyTranslator().getText("TXT_KEY_HELP_MERCENARIES_CITYBUTTON",())

      # ID 708-715 Hire/Assign Mercenaries

      # ID 716-717 Torture of assigend mercenary

      # Unit Formations
      if (iData2 == 718):
        if iData1 == -1: return u"<color=155,255,255,0>" + CyTranslator().getText("TXT_KEY_PROMOTION_FORM_NONE",()) + u"</color>"
        else: return u"<color=155,255,255,0>%s</color>" % gc.getPromotionInfo(iData1).getDescription()

      # ID 719 Promo 1 Trainer Building (Forest 1, Hills 1, City Defense 1, City Attack 1,...)
      if (iData1 == 719):
        if iData2 > -1:
          if   iData2 == gc.getInfoTypeForString("BUILDING_PROMO_FOREST"): iPromo = gc.getInfoTypeForString("PROMOTION_WOODSMAN1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_HILLS"): iPromo = gc.getInfoTypeForString("PROMOTION_GUERILLA1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_JUNGLE"): iPromo = gc.getInfoTypeForString("PROMOTION_JUNGLE1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_SWAMP"): iPromo = gc.getInfoTypeForString("PROMOTION_SUMPF1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_DESERT"): iPromo = gc.getInfoTypeForString("PROMOTION_DESERT1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_CITY_A"): iPromo = gc.getInfoTypeForString("PROMOTION_CITY_RAIDER1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_CITY_D"): iPromo = gc.getInfoTypeForString("PROMOTION_CITY_GARRISON1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_PILLAGE"): iPromo = gc.getInfoTypeForString("PROMOTION_PILLAGE1")
          elif iData2 == gc.getInfoTypeForString("BUILDING_PROMO_NAVI"): iPromo = gc.getInfoTypeForString("PROMOTION_NAVIGATION1")
          return  CyTranslator().getText("TXT_KEY_HELP_PROMO_BUILDING",(gc.getBuildingInfo(iData2).getDescription(),gc.getPromotionInfo(iPromo).getDescription()))

      # Legendary Hero can become a Great General
      if (iData1 == 720):
        return CyTranslator().getText("TXT_KEY_HELP_LEGEND_HERO_TO_GENERAL",())

      # Elefantenstall
      if (iData1 == 721):
        if iData2 == 1: return CyTranslator().getText("TXT_KEY_HELP_ELEFANTENSTALL1",())
        elif iData2 == 2: return CyTranslator().getText("TXT_KEY_HELP_ELEFANTENSTALL2",())
        else: return CyTranslator().getText("TXT_KEY_HELP_ELEFANTENSTALL3",())

      # Piraten-Feature
      if (iData1 == 722):
        if iData2 == 1: return CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE",())
        elif iData2 == 2: return CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE2",())
        elif iData2 == 3: return CyTranslator().getText("TXT_KEY_HELP_GO2PIRATE4",())

      # EspionageInfos (TechChooser)
      if (iData1 == 723):
        return gc.getEspionageMissionInfo(iData2).getText()
      # Veteran -> Reservist
      if (iData1 == 724):
        return CyTranslator().getText("TXT_KEY_SPECIALIST_RESERVIST_STRATEGY",())
      # Reservist -> Veteran
      if (iData1 == 725):
        return CyTranslator().getText("TXT_KEY_HELP_RESERVIST_TO_VETERAN",())
      # Bonusverbreitung
      if (iData1 == 726):
        return CyTranslator().getText("TXT_KEY_HELP_BONUSVERBREITUNG",())
      # Bonusverbreitung
      if (iData1 == 727):
        return CyTranslator().getText("TXT_KEY_HELP_GETREIDE_ABLIEFERN",())
      # Karte zeichnen
      if (iData1 == 728):
        return CyTranslator().getText("TXT_KEY_HELP_KARTE_ZEICHNEN",())
      # Slave -> Library
      if (iData1 == 729):
        return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2LIBRARY",())
      # Release slaves
      if (iData1 == 730):
        return CyTranslator().getText("TXT_KEY_BUTTON_RELEASESLAVES",())
      # Send Missionary to a friendly city and spread its religion
      if (iData1 == 731):
        return CyTranslator().getText("TXT_KEY_BUTTON_SPREAD_RELIGION",())
      # Send Trade Merchant into next foreign city
      if (iData1 == 732):
        return CyTranslator().getText("TXT_KEY_MISSION_AUTOMATE_MERCHANT",())
      # Limes
      if (iData1 == 733):
        if iData2 == -1: return CyTranslator().getText("TXT_KEY_INFO_LIMES_0",())
        elif iData2 == 0: return CyTranslator().getText("TXT_KEY_INFO_LIMES_1",())
        else: return CyTranslator().getText("TXT_KEY_INFO_LIMES_2",())
      # Sklave -> SPECIALIST_SLAVE_FOOD oder SPECIALIST_SLAVE_PROD
      if (iData1 == 734):
        if iData2 == 1:
          if bOption: return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2SPECIALIST1_TRUE",(iData2,))
          else: return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2SPECIALIST1_FALSE",(iData2,))
        elif iData2 == 2:
          if bOption: return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2SPECIALIST2_TRUE",(iData2,))
          else: return CyTranslator().getText("TXT_KEY_BUTTON_SLAVE2SPECIALIST2_FALSE",(iData2,))
      # Salae oder Dezimierung
      if (iData1 == 735):
        if iData2 == 1:
          return CyTranslator().getText("TXT_KEY_ACTION_SALAE_1",())
        elif iData2 == 2:
          return CyTranslator().getText("TXT_KEY_ACTION_DECIMATIO_1",())
      # Handelsposten errichten
      if (iData1 == 736):
        return CyTranslator().getText("TXT_KEY_BUTTON_HANDELSPOSTEN",())
      # Provinzstatthalter / Tribut
      if (iData1 == 737):
        return CyTranslator().getText("TXT_KEY_BUTTON_CONTACT_STATTHALTER",())

      # -------------------------------------
      # Allgemeine Infos (aktionslose Buttons)
      # 1: no cults with civic Animism
      if (iData1 == 738):
        if iData2 == 1: return CyTranslator().getText("TXT_KEY_INFO_CIVIC_NOCULT",())
      # -------------------------------------




      # CITY_TAB replacements
      if (iData1 == 88000):
        return gc.getCityTabInfo(iData2).getDescription()

    # ***TEST***
    #CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("X",iData1)), None, 2, None, ColorTypes(12), 0, 0, False, False)

    return u""

  def getUpgradePriceOverride(self, argsList):
    iPlayer, iUnitID, iUnitTypeUpgrade = argsList

    pPlayer = gc.getPlayer(iPlayer)
    pUnit = pPlayer.getUnit(iUnitID)

    iPrice = gc.getDefineINT("BASE_UNIT_UPGRADE_COST")

    # PAE (for iCost -1 Units)
    iSub = pPlayer.getUnitProductionNeeded(pUnit.getUnitType())
    if iSub <= 1: iSub = pPlayer.getUnitProductionNeeded(iUnitTypeUpgrade) / 4 * 3

    iPrice += (max(0, (pPlayer.getUnitProductionNeeded(iUnitTypeUpgrade) - iSub)) * gc.getDefineINT("UNIT_UPGRADE_COST_PER_PRODUCTION"))

    if not pPlayer.isHuman() and not pPlayer.isBarbarian():
     pHandicapInfo = gc.getHandicapInfo(gc.getGame().getHandicapType())
     iPrice *= pHandicapInfo.getAIUnitUpgradePercent() / 100
     iPrice *= max(0, ((pHandicapInfo.getAIPerEraModifier() * pPlayer.getCurrentEra()) + 100)) / 100

    iPrice = iPrice * (100 - pUnit.getUpgradeDiscount()) / 100
    if pPlayer.hasTrait(gc.getInfoTypeForString("TRAIT_ORGANIZED")): iPrice /= 2
    return max(0, iPrice)


  # Elefantenstall
  def doElefant_AI( self, pUnit ):
    pUnitGroup = pUnit.getGroup()
    if pUnitGroup.getMissionType(0) != 0:
     iOwner = pUnit.getOwner()

     # Nur 1x pro Runde alle Staedte checken
     # PAE AI Unit Instances (better turn time)
     if self.PAE_AI_ID != iOwner:
      self.PAE_AI_ID = iOwner

      pPlayer = gc.getPlayer(iOwner)

      lCities = PyPlayer(iOwner).getCityList()
      iDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
      iJungle = gc.getInfoTypeForString("FEATURE_JUNGLE")

      iRange = len(lCities)
      for iCity in range(iRange):
        pCity = pPlayer.getCity( lCities[ iCity ].getID( ) )
        if not pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
           # Check plots (Klima / climate)
           bOK = false
           for i in range(3):
             for j in range(3):
               loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
               if loopPlot != None and not loopPlot.isNone():
                 if loopPlot.getTerrainType() == iDesert or loopPlot.getFeatureType() == iJungle:
                   bOK = true
                   break
             if bOK: break

           if bOK:
             if pUnit.generatePath( pCity.plot(), 0, False, None ):
               if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
                 pUnitGroup.clearMissionQueue()
                 pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
               else:
                 pCity.setNumRealBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE"),1)
                 #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                 pUnit.kill(1,pUnit.getOwner())
                 return True


  # Inquisitor -------------------
  def doInquisitorCore_AI( self, pUnit ):
    iOwner = pUnit.getOwner( )
    pOwner = gc.getPlayer(iOwner)
    iStateReligion = pOwner.getStateReligion()

    # CAN AI use inquisitor
    if iStateReligion >= 0 and pUnit.getGroup().getMissionType(0) != 0:
      #iTurn = PyGame().getGameTurn()
      #iOwnCulture = pOwner.getCultureHistory(iTurn)
      #lPlayers = PyGame().getCivPlayerList()
      lCities = PyPlayer(iOwner).getCityList()
      iNumReligions = gc.getNumReligionInfos()


      ##--------Gegen Relisieg
      #iStateReligionPercent = CyGame().calculateReligionPercent(iStateReligion)
      #Checks religion percents
      #bestReligionPercent = 0
      #iBestReligion = -1
      #for iReligionLoop in range(iNumReligions):
      #  if (iReligionLoop != iStateReligion):
      #    religionPercent = CyGame().calculateReligionPercent(iReligionLoop)
      #    if (religionPercent > bestReligionPercent):
      #      bestReligionPercent = religionPercent
      #      iBestReligion = iReligionLoop

      #Prevent religious victory
      #if bestReligionPercent >= 90 or bestReligionPercent > iStateReligionPercent:
      #  for iCity in range(len(lCities)):
      #    pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
      #    if pCity.isHasReligion(iBestReligion) and pCity.isHasReligion(iStateReligion):
      #      #Makes the unit move to the City and purge it
      #      iPlayer = pOwner.getID()
      #      CvEventInterface.getEventManager().doInquisitorPersecution2(iPlayer, pCity.getID(), -1, iReligion, pUnit.getID())
      #      #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #      pUnit.kill(1,pUnit.getOwner())
      #      return
      ##--------Ende Relisieg

      # First Version
      #Looks to see if the AI controls a City with unhappiness and non-state religions
      #iRange = len(lCities)
      #for iCity in range(iRange):
      #    pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
      #    # has this city probably unhappiness of religion cause
      #    if pCity.happyLevel() < pCity.unhappyLevel(0):
      #      for iReligion in range(iNumReligions):
      #        if iReligion != iStateReligion and pCity.isHasReligion( iReligion ) and pCity.isHolyCityByType( iReligion ) == 0:
      #          #Makes the unit purge it
      #          iPlayer = pOwner.getID()
      #          CvEventInterface.getEventManager().doInquisitorPersecution2(iPlayer, pCity.getID(), -1, iReligion, pUnit.getID())
      #          #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #          pUnit.kill(1,pUnit.getOwner())
      #          return 1

      # lReligions.difference = Fehler: list object: GIBTS NICHT
      #for pCity in lCities:
      #  # has this city probably unhappiness of religion cause
      #  if pCity.getAngryPopulation() > 0:
      #    lReligions = pCity.getReligions()
      #    lHoly = pCity.getHolyCity()
      #    lReligionsWithoutHolyOrState = lReligions.difference(lHoly,iStateReligion)
      #    iRand = self.myRandom(len(lReligionsWithoutHolyOrState),None)
      #    iReligion = lReligionsWithoutHolyOrState(iRand)
      #    iPlayer = pOwner.getID( )       #
      #    CvEventInterface.getEventManager().doInquisitorPersecution2(iPlayer,pCity.getID(), -1, iReligion, pUnit.getID())
      #    #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
      #    pUnit.kill(1,pUnit.getOwner())
      #    return 1


      for pyCity in lCities:
        # has this city probably unhappiness of religion cause
        if pyCity.getAngryPopulation() > 0:
          lReligions = pyCity.getReligions()
          if len(lReligions) > 1:
            pCity = pOwner.getCity( pyCity.getID() )
            for iReligion in lReligions:
              if iReligion != iStateReligion:
                if pCity.isHolyCityByType( iReligion ) == 0:
                  #Makes the unit purge it
                  CvEventInterface.getEventManager().doInquisitorPersecution2(iOwner, pCity.getID(), -1, iReligion, pUnit.getID())
                  #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                  pUnit.kill(1,pUnit.getOwner())
                  return True

    return

  #def doHolyCitySeekAndDestroy( self, pUnit, pCity ):
  #
  #  if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
  #    pUnit.getGroup().clearMissionQueue()
  #    pUnit.getGroup().pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
  #  else:
  #    CvEventInterface.getEventManager().doInquisitorPersecution( pCity, pUnit )

  def getExperienceNeeded(self, argsList):
    # use this function to set how much experience a unit needs
    iLevel, iOwner = argsList

    iExperienceNeeded = 0

    # BTS: regular epic game experience
    # and PAE VI again
    iExperienceNeeded = iLevel * iLevel + 1

    # PAE IV: ab Lvl 7 mehr XP notwendig
    #if iLevel > 7: iExperienceNeeded += iLevel * 2

    # PAE V: L * (L+2) - (L / 2)
    #iExperienceNeeded = (iLevel * (iLevel+2)) - (iLevel/2)

    iModifier = gc.getPlayer(iOwner).getLevelExperienceModifier()
    if (0 != iModifier):
      iExperienceNeeded += (iExperienceNeeded * iModifier + 99) / 100   # ROUND UP

    return iExperienceNeeded

  # Freed slaves for AI
  def doSettleFreedSlaves_AI( self, pUnit ):
    pUnitGroup = pUnit.getGroup()

    if pUnitGroup.getMissionType(0) != 0:
      iOwner = pUnit.getOwner( )
      pOwner = gc.getPlayer(iOwner)
      lCities = PyPlayer(iOwner).getCityList()
      iCities = len(lCities)

      pSeekCity = None
      iSeek = 0

      for iCity in range(iCities):
         pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
         iNum = pCity.getYieldRate(1)
         if iNum <= iSeek or iNum == 0:
           pSeekCity = pCity
           iSeek = iNum

      # PAE Better AI soll direkt ansiedeln
      if pSeekCity != None and not pSeekCity.isNone():
        #if pUnit.getX() != pSeekCity.getX() or pUnit.getY() != pSeekCity.getY():
        #  pUnitGroup.clearMissionQueue()
        #  pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pSeekCity.getX(), pSeekCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
        #else:
        pSeekCity.changeFreeSpecialistCount(0,1) # Spezialist Citizen
        #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
        pUnit.kill(1,pUnit.getOwner())
        return True

    return

  # Veteran -> Reservist in city for AI
  def doReservist_AI( self, pUnit ):
    pUnitGroup = pUnit.getGroup()

    if pUnitGroup.getMissionType(0) != 0:
      iOwner = pUnit.getOwner( )
      pOwner = gc.getPlayer(iOwner)
      lCities = PyPlayer(iOwner).getCityList()
      iCities = len(lCities)

      # nur im Friedensfall
      bWar = False
      iThisTeam = pOwner.getTeam()
      pThisTeam = gc.getTeam(iThisTeam)

      if pThisTeam.isHasTech(gc.getInfoTypeForString("TECH_RESERVISTEN")):
        iRange = gc.getMAX_CIV_TEAMS()
        for i in range(iRange):
          if gc.getPlayer(i).isAlive():
            iTeam = gc.getPlayer(i).getTeam()
            if pThisTeam.isAtWar(iTeam): bWar = True

        if not bWar:
          if pUnit.getUnitType() not in self.lUnitsNoAIReservists:

            pSeekCity = None
            iSeek = 0

            for iCity in range(iCities):
              pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
              iNum = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST
              if iNum <= iSeek or iNum == 0:
                pSeekCity = pCity
                iSeek = iNum

            # PAE Better AI soll direkt ansiedeln - rausgegeben
            if pSeekCity != None and not pSeekCity.isNone():
              if pUnit.getX() != pSeekCity.getX() or pUnit.getY() != pSeekCity.getY():
                pUnitGroup.clearMissionQueue()
                pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pSeekCity.getX(), pSeekCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
              else:
                pSeekCity.changeFreeSpecialistCount(19,1) # SPECIALIST_RESERVIST
                #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                pUnit.kill(1,pUnit.getOwner())
                return True

      return


  # Upgrade Veteran Unit to Elite Unit
  # Veteran -> Eliteunit
  def doUpgradeVeteran_AI( self, pUnit, iNewUnit):
    CvEventInterface.getEventManager().doUpgradeVeteran(pUnit, iNewUnit)
    return


  # Promotion Trainer Building (Forest 1, Hills 1, ...) -------------------
  def doAISettleTrainer( self, pUnit ):
    iPlayer = pUnit.getOwner()
    pPlayer = gc.getPlayer(iPlayer)
    lCities = PyPlayer(iPlayer).getCityList()
    pPlot = CyMap().plot(pUnit.getX(), pUnit.getY())

    # An necessary advantage for the AI: AI does not need to move unit into a city
    # An undone possibility: units gets some strong escort units to move to an own city
    if pPlot.getOwner() == iPlayer:

      lPromos = []
      lPromos.append(gc.getInfoTypeForString("PROMOTION_WOODSMAN5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_GUERILLA5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_JUNGLE5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_SUMPF5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_DESERT5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_PILLAGE5"))
      lPromos.append(gc.getInfoTypeForString("PROMOTION_NAVIGATION4"))

      iNumCities = len(lCities)
      for iPromo in lPromos:
        if pUnit.isHasPromotion(iPromo):
          if   iPromo == gc.getInfoTypeForString("PROMOTION_WOODSMAN5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_FOREST")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_GUERILLA5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_HILLS")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_JUNGLE5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_JUNGLE")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_SUMPF5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_SWAMP")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_DESERT5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_DESERT")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_CITY_A")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_CITY_D")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_PILLAGE5"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_PILLAGE")
          elif iPromo == gc.getInfoTypeForString("PROMOTION_NAVIGATION4"): iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_NAVI")

          for iCity in range(iNumCities):
            pCity = pPlayer.getCity( lCities[iCity].getID() )
            if not pCity.isHasBuilding(iBuilding):
              if iPromo != gc.getInfoTypeForString("PROMOTION_NAVIGATION4") or pCity.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
                pCity.setNumRealBuilding(iBuilding,1)
                pUnit.kill(1,pUnit.getOwner())
                #pUnit.doCommand(CommandTypes.COMMAND_DELETE, 1, 1)
                return True

    return

  # Bonusverbreitung -------------------
  # Schritt 1: Bonus verbreiten
  # Schritt 2: Stadt mit Getreide fuellen
  def doBonusverbreitung_AI ( self, pUnit ):
    pUnitGroup = pUnit.getGroup()

    if pUnitGroup.getMissionType(0) != 0:
      # Inits
      iOwner = pUnit.getOwner( )
      pOwner = gc.getPlayer(iOwner)
      lCities = PyPlayer(iOwner).getCityList()
      iCities = len(lCities)
      pPlot = gc.getMap().plot(pUnit.getX(), pUnit.getY())
      PAE_Event_Manager = CvEventInterface.getEventManager()

      # Wenn mehr als 2 Karren unterwegs sind: killen
      #if pOwner.getUnitClassCount(gc.getInfoTypeForString("UNITCLASS_SUPPLY_FOOD")) > 2:
      #   pUnit.kill(1,pUnit.getOwner())
      #   return True

      # Boni
      lBonuses = []
      # Gruppe 1
      a1 = gc.getInfoTypeForString("BONUS_WHEAT")
      a2 = gc.getInfoTypeForString("BONUS_GERSTE")
      a3 = gc.getInfoTypeForString("BONUS_HAFER")
      a4 = gc.getInfoTypeForString("BONUS_ROGGEN")
      a5 = gc.getInfoTypeForString("BONUS_HIRSE")
      a6 = gc.getInfoTypeForString("BONUS_RICE")
      a1sum = pOwner.getNumAvailableBonuses(a1)
      a2sum = pOwner.getNumAvailableBonuses(a2)
      a3sum = pOwner.getNumAvailableBonuses(a3)
      a4sum = pOwner.getNumAvailableBonuses(a4)
      a5sum = pOwner.getNumAvailableBonuses(a5)
      a6sum = pOwner.getNumAvailableBonuses(a6)
      lBonuses.append(a1)
      lBonuses.append(a2)
      lBonuses.append(a3)
      lBonuses.append(a4)
      lBonuses.append(a5)
      lBonuses.append(a6)
      # Gruppe 2
      b1 = gc.getInfoTypeForString("BONUS_COW")
      b2 = gc.getInfoTypeForString("BONUS_PIG")
      b3 = gc.getInfoTypeForString("BONUS_SHEEP")
      b1sum = pOwner.getNumAvailableBonuses(b1)
      b2sum = pOwner.getNumAvailableBonuses(b2)
      b3sum = pOwner.getNumAvailableBonuses(b3)
      lBonuses.append(b1)
      lBonuses.append(b2)
      lBonuses.append(b3)
      # Gruppe 3
      c1 = gc.getInfoTypeForString("BONUS_OLIVES")
      c2 = gc.getInfoTypeForString("BONUS_DATTELN")
      c1sum = pOwner.getNumAvailableBonuses(c1)
      c2sum = pOwner.getNumAvailableBonuses(c2)
      lBonuses.append(c1)
      lBonuses.append(c2)
      # Gruppe 4
      d1 = gc.getInfoTypeForString("BONUS_CAMEL")
      d1sum = pOwner.getNumAvailableBonuses(d1)
      lBonuses.append(d1)

      # Hat die KI Boni zum Verbreiten?
      # Eigene Liste der Boni fuer die KI fuer schneller Abfragen
      lAIBonuses = []
      iRange = len(lBonuses)
      for i in range (iRange):
        if pOwner.getNumAvailableBonuses(lBonuses[i]) > 0:
          lAIBonuses.append(lBonuses[i])

      if len(lAIBonuses): bAIHasBonus = true
      else: bAIHasBonus = false

      # -------

      # --- Zuerst diese Stadt checken
      pThisPlotCity = None
      if bAIHasBonus and pPlot.isCity():
        # Inits
        pThisPlotCity = pPlot.getPlotCity()
        lNewBonus = []

        # Moegliche Boni
        iRange = len(lAIBonuses)
        i=0
        for i in range (iRange):
          seekPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pThisPlotCity, lAIBonuses[i])
          if seekPlot != None and not seekPlot.isNone():

            iBonusHier = seekPlot.getBonusType(iOwner)
            # Unerforschte Resource?
            if iBonusHier == -1: iBonusHier = seekPlot.getBonusType(-1)

            # kein gleiches Bonusgut
            if iBonusHier != lAIBonuses[i]:
              # kein Bonusgut => fix dabei
              if iBonusHier == -1: lNewBonus.append(lAIBonuses[i])
              else:
                # Boni der selben Gruppe herausfinden und vergleichen
                if lAIBonuses[i] == a1:
                  if a1sum+1 < a2sum and a2sum > 1 or a1sum+1 < a3sum and a3sum > 1 or a1sum+1 < a4sum and a4sum > 1 or a1sum+1 < a5sum and a5sum > 1 or a1sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a2:
                  if a2sum+1 < a1sum and a1sum > 1 or a2sum+1 < a3sum and a3sum > 1 or a2sum+1 < a4sum and a4sum > 1 or a2sum+1 < a5sum and a5sum > 1 or a2sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a3:
                  if a3sum+1 < a1sum and a1sum > 1 or a3sum+1 < a2sum and a2sum > 1 or a3sum+1 < a4sum and a4sum > 1 or a3sum+1 < a5sum and a5sum > 1 or a3sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a4:
                  if a4sum+1 < a1sum and a1sum > 1 or a4sum+1 < a2sum and a2sum > 1 or a4sum+1 < a3sum and a3sum > 1 or a4sum+1 < a5sum and a5sum > 1 or a4sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a5:
                  if a5sum+1 < a1sum and a1sum > 1 or a5sum+1 < a2sum and a2sum > 1 or a5sum+1 < a3sum and a3sum > 1 or a5sum+1 < a4sum and a4sum > 1 or a5sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a6:
                  if a6sum+1 < a1sum and a1sum > 1 or a6sum+1 < a2sum and a2sum > 1 or a6sum+1 < a3sum and a3sum > 1 or a6sum+1 < a4sum and a4sum > 1 or a6sum+1 < a5sum and a5sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b1:
                  if b1sum+1 < b2sum and b2sum > 1 or b1sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b2:
                  if b2sum+1 < b1sum and b1sum > 1 or b2sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b3:
                  if b3sum+1 < b1sum and b1sum > 1 or b3sum+1 < b2sum and b2sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == c1:
                  if c1sum+1 < c2sum and c2sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == c2:
                  if c2sum+1 < c1sum and c1sum > 1: lNewBonus.append(lAIBonuses[i])


        # Wenn leer, dann gehts unten weiter (Stadt suchen)
        if len(lNewBonus):
          iRand = self.myRandom(len(lNewBonus), None)
          iBonus = lNewBonus[iRand]

          # Bonus verbreiten (aber nicht, wenn dieses bereits auf dem Plot ist)
          if iBonus > -1:
              loopPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pThisPlotCity, iBonus)
              if loopPlot != None and not loopPlot.isNone() and loopPlot.getBonusType(iOwner) != iBonus:

                ### TEST ###
                #CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iY",loopPlot.getY())), None, 2, None, ColorTypes(12), 0, 0, False, False)
                #CyInterface().addMessage(CyGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("iX",loopPlot.getX())), None, 2, None, ColorTypes(12), 0, 0, False, False)

                # KI 10% mehr Chance
                if self.myRandom(100, None) < iChance + 10:
                  loopPlot.setBonusType(iBonus)
                pUnit.kill(1,pUnit.getOwner())
                return True

      # --- Stadt gecheckt


      # Alle moeglichen Staedte durchsuchen
      pSeekCity = None
      pSeekCityList = []
      pSeekCity2 = None
      iSeek2 = 0
      iAIBoni = len(lAIBonuses)

      # Check 1: Anzahl der bereits zugewiesenen Boni pro Stadt
      # Check 2: Foodstorage
      for iCity in range(iCities):
        pCity = pOwner.getCity( lCities[ iCity ].getID( ) )
        bCheck = true

        if pThisPlotCity != None and not pThisPlotCity.isNone():
          if pCity.getID() == pThisPlotCity.getID(): bCheck = false

        # 1: BONUS
        # anfangs leere Liste StadtBoni (falls eine stadt 2 gleiche boni hat)
        if bAIHasBonus and bCheck:
          lNewBonus = []
          i=0
          for i in range (iAIBoni):
            seekPlot, iChance = PAE_Event_Manager.doBonusCityGetPlot(pCity, lAIBonuses[i])
            if seekPlot != None:

             iBonusHier = seekPlot.getBonusType(iOwner)
             # Unerforschte Resource?
             if iBonusHier == -1: iBonusHier = seekPlot.getBonusType(-1)

             # kein gleiches Bonusgut
             if iBonusHier != lAIBonuses[i]:
              # kein Bonusgut => fix dabei
              if iBonusHier == -1: lNewBonus.append(lAIBonuses[i])
              else:
                # Boni der selben Gruppe herausfinden und vergleichen
                if lAIBonuses[i] == a1:
                  if a1sum+1 < a2sum and a2sum > 1 or a1sum+1 < a3sum and a3sum > 1 or a1sum+1 < a4sum and a4sum > 1 or a1sum+1 < a5sum and a5sum > 1 or a1sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a2:
                  if a2sum+1 < a1sum and a1sum > 1 or a2sum+1 < a3sum and a3sum > 1 or a2sum+1 < a4sum and a4sum > 1 or a2sum+1 < a5sum and a5sum > 1 or a2sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a3:
                  if a3sum+1 < a1sum and a1sum > 1 or a3sum+1 < a2sum and a2sum > 1 or a3sum+1 < a4sum and a4sum > 1 or a3sum+1 < a5sum and a5sum > 1 or a3sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a4:
                  if a4sum+1 < a1sum and a1sum > 1 or a4sum+1 < a2sum and a2sum > 1 or a4sum+1 < a3sum and a3sum > 1 or a4sum+1 < a5sum and a5sum > 1 or a4sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a5:
                  if a5sum+1 < a1sum and a1sum > 1 or a5sum+1 < a2sum and a2sum > 1 or a5sum+1 < a3sum and a3sum > 1 or a5sum+1 < a4sum and a4sum > 1 or a5sum+1 < a6sum and a6sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == a6:
                  if a6sum+1 < a1sum and a1sum > 1 or a6sum+1 < a2sum and a2sum > 1 or a6sum+1 < a3sum and a3sum > 1 or a6sum+1 < a4sum and a4sum > 1 or a6sum+1 < a5sum and a5sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b1:
                  if b1sum+1 < b2sum and b2sum > 1 or b1sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b2:
                  if b2sum+1 < b1sum and b1sum > 1 or b2sum+1 < b3sum and b3sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == b3:
                  if b3sum+1 < b1sum and b1sum > 1 or b3sum+1 < b2sum and b2sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == c1:
                  if c1sum+1 < c2sum and c2sum > 1: lNewBonus.append(lAIBonuses[i])
                elif lAIBonuses[i] == c2:
                  if c2sum+1 < c1sum and c1sum > 1: lNewBonus.append(lAIBonuses[i])

          if len(lNewBonus):
            pSeekCityList.append(pCity)


        # 2: FOOD Storage
        iFood = pCity.getFood()
        if iSeek2 > iFood or iSeek2 == 0:
          pSeekCity2 = pCity
          iSeek2 = iFood


      # Stadt fuer die Verbreitung auswaehlen
      if len(pSeekCityList) > 0:
        iRand = self.myRandom(len(pSeekCityList), None)
        pSeekCity = pSeekCityList[iRand]


      # Schritt 1: Bonus verbreiten
      # Es gibt maximal 4 Plots zu bewirtschaften
      if pSeekCity != None and not pSeekCity.isNone():
        pCity = pSeekCity

        # Stadt aufsuchen
        if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
          pUnitGroup.clearMissionQueue()
          pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)
          return True

      # Schritt 2: Stadt mit Getreide fuellen
      if pSeekCity2 != None and not pSeekCity2.isNone():
        pCity = pSeekCity2

        # Stadt aufsuchen
        if pUnit.getX() != pCity.getX() or pUnit.getY() != pCity.getY():
          pUnitGroup.clearMissionQueue()
          pUnitGroup.pushMission(MissionTypes.MISSION_MOVE_TO, pCity.getX(), pCity.getY(), 0, False, True, MissionAITypes.NO_MISSIONAI, pUnit.plot(), pUnit)

        # Stadt mit Getreide auffuellen
        else:
          pCity.changeFood(50)
          pUnit.kill(1,pUnit.getOwner())
          return True

    return