# Christian features and events

### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random

### Defines
gc = CyGlobalContext()

### Globals
bChristentum = False

def init():
  global bChristentum
  if gc.getGame().isReligionFounded (gc.getInfoTypeForString("RELIGION_CHRISTIANITY")):
    bChristentum = True

def myRandom (num):
    if num <= 1: return 0
    else: return random.randint(0, num-1)

def setHolyCity():
    global bChristentum
    # Stadt finden
    pCity = None
    iJudentum = gc.getInfoTypeForString("RELIGION_JUDAISM")
    # Prio1: Heilige Stadt des Judentums
    if gc.getGame().isReligionFounded(iJudentum): pCity = gc.getGame().getHolyCity(iJudentum)

    # Prio 2: Juedische Stadt
    if pCity == None:
      lCities = []
      iNumPlayers = gc.getMAX_PLAYERS()
      for i in range(iNumPlayers):
        loopPlayer = gc.getPlayer(i)
        if loopPlayer.isAlive():
          iNumCities = loopPlayer.getNumCities()
          for j in range (iNumCities):
            loopCity = loopPlayer.getCity(j)
            if not loopCity.isNone():
              if loopCity.isHasReligion(iJudentum): lCities.append(loopCity)

      if len(lCities) > 0:
        pCity = lCities[myRandom(len(lCities))]

    # Prio3: Hauptstadt mit den meisten Sklaven (ink. Gladiatoren)
    # oder Prio 4: biggest capital city
    if pCity == None:
      # falls es nur Staedte ohne Sklaven gibt
      lCities = []
      # fuer den Vergleich mit Staedten mit Sklaven
      iSumSlaves = 0
      # biggest capital
      iPop = 0

      iNumPlayers = gc.getMAX_PLAYERS()
      for i in range(iNumPlayers):
        loopPlayer = gc.getPlayer(i)
        if loopPlayer.isAlive():
          loopCity = loopPlayer.getCapitalCity()
          if not loopCity.isNone():

            iSlaves = loopCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
            iSlaves += loopCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
            iSlaves += loopCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
            iSlaves += loopCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD

            iCityPop = loopCity.getPopulation()
            if iSlaves == 0:
              if iCityPop > iPop:
                iPop = iCityPop
                lCities = []
                lCities.append(loopCity)
              elif iCityPop == iPop:
                lCities.append(loopCity)
            elif iSumSlaves < iSlaves:
              iSumSlaves = iSlaves
              pCity = loopCity

      if pCity == None:
        if len(lCities) > 0: pCity = lCities[myRandom(len(lCities))]


    # --- Heilige Stadt setzen ---
    if pCity != None:
      gc.getGame().setHolyCity (gc.getInfoTypeForString("RELIGION_CHRISTIANITY"), pCity, True)
      bChristentum = True
