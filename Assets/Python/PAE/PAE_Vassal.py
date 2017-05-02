### Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import random

### Defines
gc = CyGlobalContext()

def myRandom (num):
    #return gc.getGame().getMapRandNum(num, None)
    if num <= 1: return 0
    else: return random.randint(0, num-1)

def onCityAcquired(pCity, iNewOwner, iPreviousOwner):
  pWinner = gc.getPlayer(iNewOwner)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)

  # Der Gewinner muss die TECH Vassallentum erforscht haben
  iTechVasallentum = gc.getInfoTypeForString("TECH_VASALLENTUM")
  if pWinnerTeam.isHasTech(iTechVasallentum) and iNewOwner != gc.getBARBARIAN_PLAYER():

    pLoser = gc.getPlayer(iPreviousOwner)
    iLoserTeam = pLoser.getTeam()
    pLoserTeam = gc.getTeam(iLoserTeam)
    iLoserPowerWithVassals = pLoserTeam.getPower(True) # mit Vasallen
    iWinnerPower = pWinnerTeam.getPower(True) # mit Vasallen

    # ***TEST***
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Winner Power",iWinnerPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)
    #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Loser Power",iLoserPowerWithVassals)), None, 2, None, ColorTypes(10), 0, 0, False, False)

    # Hegemon verliert eine Stadt, Vasallen werden gecheckt
    iRange = gc.getMAX_PLAYERS()
    for iVassal in range(iRange):
      pPlayer = gc.getPlayer(iVassal)
      if pPlayer.isAlive():
        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)
        if pTeam.isVassal(iLoserTeam):
          iVassalPower = pTeam.getPower(True)

          iLoserPower = iLoserPowerWithVassals - iVassalPower

          # ***TEST***
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Hegemon Power",iLoserPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)
          #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Vasall Power",iVassalPower)), None, 2, None, ColorTypes(10), 0, 0, False, False)

          # Wenn Vasall gemeinsam mit dem Feind staerker als Hegemon ist
          # weiters trotzdem loyal zum Hegemon 1:3
          if iVassalPower + iWinnerPower > iLoserPower and 10 > (myRandom(30) + pPlayer.AI_getAttitude(iPreviousOwner) - pPlayer.AI_getAttitude(iNewOwner)):

            # ***TEST***
            #CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Vassal interaction",1)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            # Initials
            iWinnerGold = pWinner.getGold()

            # 1/3 Gold, aber mind. > 300
            if iVassalPower > iLoserPower - iLoserPower/3 + 1:
              fGold = 0.33
              iMinGold = 300

            # 1/2 Gold, aber mind. > 400
            elif iVassalPower > iLoserPower / 2:
              fGold = 0.5
              iMinGold = 400

            # 2/3 Gold, aber mind. > 500
            else:
              fGold = 0.66
              iMinGold = 500


            # HI Vassal
            # ------------------------------
            if pPlayer.isHuman():
              # Wir sind staerker als der Hegemon
              if iVassalPower > iLoserPower:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09",(pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0),pPlayer.getCivilizationAdjective(3))) )
                popupInfo.setData1(iNewOwner)
                popupInfo.setData2(iPreviousOwner)
                popupInfo.setData3(iVassal)
                popupInfo.setOnClickedPythonCallback("popupVassal09") # EntryPoints/CvScreenInterface und CvGameUtils / 688
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_YES",(pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0))), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_NO", (pLoser.getCivilizationShortDescription(0),pWinner.getCivilizationShortDescription(0))), "")
                popupInfo.addPopup(iVassal)

              # Gemeinsam sind wir staerker als der Hegemon
              # HI-HI-Interaktion
              elif pWinner.isHuman() and iWinnerGold >= iMinGold:
                iBribe = int(iWinnerGold * fGold)
                if iMinGold > iBribe: iBribe = iMinGold

                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10",(pCity.getName(), pPlayer.getCivilizationAdjective(3), gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription() )) )
                popupInfo.setData1(iNewOwner)
                popupInfo.setData2(iPreviousOwner)
                popupInfo.setData3(iVassal)
                popupInfo.setFlags(iBribe)
                popupInfo.setOnClickedPythonCallback("popupVassal10") # EntryPoints/CvScreenInterface und CvGameUtils / 689
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10_YES",(gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription(),iBribe)), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_10_NO", (gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getDescription(),)), "")
                popupInfo.addPopup(iNewOwner)


              # HI-KI Interaktion
              elif iWinnerGold >= iMinGold:
                iBribe = int(iWinnerGold * fGold)
                if iMinGold > iBribe: iBribe = iMinGold

                # KI bietet zu 50% ein Angebot an
                if 1 > myRandom(2):
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                  popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iBribe,pWinner.getCivilizationShortDescription(0))) )
                  popupInfo.setData1(iNewOwner)
                  popupInfo.setData2(iPreviousOwner)
                  popupInfo.setData3(iVassal)
                  popupInfo.setFlags(iBribe)
                  popupInfo.setOnClickedPythonCallback("popupVassal11") # EntryPoints/CvScreenInterface und CvGameUtils / 690
                  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription())), "")
                  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_NO",()), "")
                  iRand = 1 + myRandom(9)
                  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
                  popupInfo.addPopup(iVassal)

                # Winner hat kein Interesse
                # Vasall darf entscheiden, ob er Krieg erklaert
                else:
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                  popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
                  popupInfo.setData1(iNewOwner)
                  popupInfo.setData2(iPreviousOwner)
                  popupInfo.setData3(iVassal)
                  popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
                  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
                  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
                  popupInfo.addPopup(iVassal)

              # Winner hat kein Gold
              # Vasall darf entscheiden, ob er Krieg erklaert
              else:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_13",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
                popupInfo.setData1(iNewOwner)
                popupInfo.setData2(iPreviousOwner)
                popupInfo.setData3(iVassal)
                popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
                popupInfo.addPopup(iVassal)

              # ------------------------------

            # HI Winner
            # ----------------------------
            elif pWinner.isHuman():
              iBribe = int(iWinnerGold * fGold)
              if iMinGold > iBribe: iBribe = iMinGold

              if iWinnerGold >= iBribe:
                popupInfo = CyPopupInfo()
                popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
                popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08",(pPlayer.getCivilizationShortDescription(0),gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),iBribe)) )
                popupInfo.setData1(iNewOwner)
                popupInfo.setData2(iPreviousOwner)
                popupInfo.setData3(iVassal)
                popupInfo.setFlags(iBribe)
                popupInfo.setOnClickedPythonCallback("popupVassal08") # EntryPoints/CvScreenInterface und CvGameUtils / 687
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08_YES",(pLoser.getCivilizationShortDescription(0),iBribe)), "")
                popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_08_NO",()), "")
                popupInfo.addPopup(iNewOwner)

            # KI Vassal
            # ------------------------------
            else:
              bDeclareWar = False
              if iVassalPower > iLoserPower:
                # 2/3 Chance, dass Vasall dem Hegemon Krieg erklaert
                if 2 > myRandom(3):
                  bDeclareWar = True

              # KI-KI-Interaktion
              # Winner hat mehr als das erforderte Gold, Akzeptanz: Winner: 50%, Loser: 100%
              if not bDeclareWar and iMinGold <= iWinnerGold * fGold:
                  if 1 > myRandom(2):
                    bDeclareWar = True
                    pPlayer.changeGold(int(iWinnerGold * fGold))
                    pWinner.changeGold(int(iWinnerGold * fGold) * (-1))

              # Winner hat das mindest geforderte Gold, Akzeptanz: Winner: 100%, Loser: 50%
              if not bDeclareWar and iWinnerGold >= iMinGold:
                  if 1 > myRandom(2):
                    bDeclareWar = True
                    pPlayer.changeGold(iMinGold)
                    pWinner.changeGold(iMinGold * (-1))

              if bDeclareWar:
                #pHegemonTeam.freeVassal(iTeam)
                pTeam.declareWar(iLoserTeam, 0, 4)
                if pWinner.isHuman():
                  popupInfo = CyPopupInfo()
                  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                  popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_1",(pTeam.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pTeam.getLeaderType()).getDescription(),)) )
                  popupInfo.addPopup(iNewOwner)

    # Hegemon verliert Stadt Ende -----


    # ------------
    # Wenn man selbst eine Stadt verliert
    # Loser und Winner-Werte von oben
    # ------------

    # -------------------------------
    # Wird der Verlierer zum Vasall ?
    iMinimumCities = 5
    if pLoser.hasTrait(gc.getInfoTypeForString("TRAIT_AGGRESSIVE")): iMinimumCities = 3

    if iLoserPowerWithVassals < iWinnerPower and pLoser.getNumCities() > 0 and pLoser.getNumCities() < iMinimumCities and iNewOwner != gc.getBARBARIAN_PLAYER() and iPreviousOwner != gc.getBARBARIAN_PLAYER():
      #Abfrage ob man als Gewinner den Schwaecheren zum Vasall nimmt
      # HI-HI
      if pWinner.isHuman() and pLoser.isHuman():
        VassalHItoHI (iNewOwner, iPreviousOwner, pCity)

      # KI bietet der HI Vasallenstatus an, 120% - 10% pro Stadt
      elif pWinner.isHuman():
        if 12 - pLoser.getNumCities() > myRandom(10):
          iGold = pLoser.getGold() / 2 + myRandom(pLoser.getGold() / 2)
          iGold = int(iGold)
          popupInfo = CyPopupInfo()
          popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
          popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0),iGold)) )
          popupInfo.setData1(iNewOwner)
          popupInfo.setData2(iPreviousOwner)
          popupInfo.setData3(iGold)
          popupInfo.setFlags(0) # to Loser
          popupInfo.setOnClickedPythonCallback("popupVassal01") # EntryPoints/CvScreenInterface und CvGameUtils / 671
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_YES",()), "")
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_NO",()), "")
          iRand = 1 + myRandom(9)
          popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
          popupInfo.addPopup(iNewOwner)

    # HI: Abfrage ob HI als Verlierer Vasall werden will
    elif pLoser.isHuman():
      iGold = pLoser.getGold() / 2 + myRandom(pLoser.getGold() / 2)
      iGold = int(iGold)
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_02",(pCity.getName(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iGold)) )
      popupInfo.setData1(iNewOwner)
      popupInfo.setData2(iPreviousOwner)
      popupInfo.setData3(iGold)
      popupInfo.setFlags(1) # to Winner
      popupInfo.setOnClickedPythonCallback("popupVassal01") # EntryPoints/CvScreenInterface und CvGameUtils / 671
      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_02_YES",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(), pWinner.getCivilizationShortDescription(0))), "")
      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_01_NO",()), "")
      iRand = 1 + myRandom(9)
      popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
      popupInfo.addPopup(iPreviousOwner)

  # KI-KI Vasall, 120% - 10% pro Stadt
  # PAE V Patch 4: deaktiviert
  # else:
  #   if 12 - pLoser.getNumCities() > myRandom(10):
  #     pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
  #     VassalHegemonGetsVassal(iPreviousOwner) # Hegemon verliert seine Vasallen
  #     iGold = pLoser.getGold() / 2 + myRandom(pLoser.getGold() / 2)
  #     pWinner.changeGold(iGold)
  #     pLoser.changeGold(iGold * (-1))

# Vasall soll seinen Hegemon verlieren
def VassalUnsetHegemon (iVassal):
  pVassal =  gc.getPlayer(iVassal)
  iVassalTeam = pVassal.getTeam()
  pVassalTeam = gc.getTeam(iVassalTeam)
  iRange = gc.getMAX_PLAYERS()
  for i in range(iRange):
    pPlayer = gc.getPlayer(i)
    if pPlayer.isAlive():
      iTeam = pPlayer.getTeam()
      pTeam = gc.getTeam(iTeam)
      if pVassalTeam.isVassal(pTeam.getID()):
        pTeam.setVassal (iVassalTeam, 0, 0)


# Hegemon verliert seine Vasallen
def VassalHegemonGetsVassal (iHegemon):
  pHegemon = gc.getPlayer(iHegemon)
  iHegemonTeam = pHegemon.getTeam()
  pHegemonTeam = gc.getTeam(iHegemonTeam)
  iRange = gc.getMAX_PLAYERS()
  for i in range(iRange):
    pPlayer = gc.getPlayer(i)
    if pPlayer.isAlive():
      iTeam = pPlayer.getTeam()
      pTeam = gc.getTeam(iTeam)
      if pTeam.isVassal(pHegemonTeam.getID()):
        #pHegemonTeam.setVassal (iTeam, 0, 0)
        pHegemonTeam.freeVassal (iTeam)


def VassalHItoHI (iNewOwner, iPreviousOwner, pCity):
  pLoser = gc.getPlayer(iPreviousOwner)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)
  iLoserPower = pLoserTeam.getPower(False) # ohne Vasallen
  iLoserPowerWithVassals = pLoserTeam.getPower(True) # mit Vasallen
  pWinner = gc.getPlayer(iNewOwner)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iWinnerPower = pWinnerTeam.getPower(True) # mit Vasallen
  # HI-HI Interaktion
  # 1) Der Loser darf beginnen und sich als Vasall vorschlagen
  # 1a) Wenn negativ, dann soll Winner eine Meldung bekommen und dem Loser einen Vorschlag unterbreiten => 2
  # 1b) Der Winner darf entscheiden, ob der Vorschlag angenommen wird
  # 2) Der Loser darf entscheiden, ob er mit dem Angebot des Winners Vasall wird
  iGold1 = myRandom(pLoser.getGold() / 2)
  if iGold1 < pLoser.getGold() / 4: iGold1 = pLoser.getGold() / 4
  iGold2 = iGold1 * 2
  iGold1 = int(iGold1)
  iGold2 = int(iGold2)
  popupInfo = CyPopupInfo()
  popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
  if iLoserPower < iWinnerPower / 2: szBuffer = "TXT_KEY_POPUP_VASSAL_03_A"
  elif iLoserPower < iWinnerPower - iWinnerPower / 3:
    # Gemeinsam mit unseren Vasallen
    if iLoserPower < iLoserPowerWithVassals: szBuffer = "TXT_KEY_POPUP_VASSAL_03_C"
    else: szBuffer = "TXT_KEY_POPUP_VASSAL_03_B"
  else: szBuffer = "TXT_KEY_POPUP_VASSAL_03_D"

  if pCity == None:
    CityName = ""
    szBuffer = "TXT_KEY_POPUP_VASSAL_03_E"
  else:
    CityName = pCity.getName()
  popupInfo.setText( CyTranslator().getText(szBuffer,(CityName,pWinner.getCivilizationAdjective(2),pWinner.getCivilizationShortDescription(0))) )
  popupInfo.setData1(iNewOwner)
  popupInfo.setData2(iPreviousOwner)
  popupInfo.setData3(iGold1)
  popupInfo.setFlags(iGold2)
  popupInfo.setOnClickedPythonCallback("popupVassal03") # EntryPoints/CvScreenInterface und CvGameUtils / 682
  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_1",(pWinner.getCivilizationShortDescription(0),iGold1)), "")
  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_2",(pWinner.getCivilizationShortDescription(0),iGold2)), "")
  popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_03_NO",()), "")
  popupInfo.addPopup(iPreviousOwner)

def onModNetMessage(iData1, iData2, iData3, iData4, iData5):
  # iLoser gets Vassal of iWinner with 1/2 Gold of iLoser
    if iData1 == 671:
      do671(iData2, iData3, iData4, iData5)

    # HI-HI Interaktion Start ++++++++++++++++++++++++++++++
    # 1) Der Loser darf beginnen und sich als Vasall vorschlagen
    # 1a) Wenn negativ, dann soll Winner eine Meldung bekommen und dem Loser einen Vorschlag unterbreiten => 2
    # 1b) Der Winner darf entscheiden, ob der Vorschlag angenommen wird
    # 2) Der Loser darf entscheiden, ob er mit dem Angebot des Winners Vasall wird
    # = Net-ID , iWinner , iLoser, iGold1
    elif iData1 == 682:
      do682(iData2, iData3, iData4)

    # 1a => 2
    elif iData1 == 683:
      do683(iData2, iData3, iData4)

    # 2 => Loser entscheidet: YES: Loser wird Vasall, NO: Winner bekommt Meldung
    elif iData1 == 684:
      do684(iData2, iData3, iData4)

    # 1b Winner entscheidet: YES: Loser wird Vasall, NO: Loser bekommt Meldung
    elif iData1 == 685:
      do685(iData2, iData3, iData4)

    # Es wird nochmal entschieden
    elif iData1 == 686:
      # zur Loserauswahl
      if iData4 == 0:
        # iWinner , iLoser, pCity
        VassalHItoHI (iData2, iData3, None)
      # zur Winnerauswahl
      else:
        CyMessageControl().sendModNetMessage( 682, iData1, iData2, -1, 0 )

    # HI-HI Interaktion Ende +++++++++++++++++++++++++++++++++

    # Winner greift einen Hegemon an und bekommt ein positives Kriegsangebot von einem seiner Vasallen
    # Message-ID / HI - Winner / KI-Loser (Hegemon) / KI-Vasall / Bestechungsgeld
    elif iData1 == 687:
      do687(iData2, iData3, iData4, iData5)

    # HI ist Vasall eines Hegemons, der soeben eine Stadt verloren hat
    # iData5: 0=Krieg gegen Hegemon, 1=treu
    elif iData1 == 688:
      do688(iData2, iData3, iData4, iData5)

    # 1. Schritt HI-Winner und HI-Vasall
    elif iData1 == 689:
      do689(iData2, iData3, iData4, iData5)

    # HI Vasall: Kriegserklaerung an Hegemon oder Botschafterkill
    elif iData1 == 690:
      do690(iData2, iData3, iData4, iData5)

    # HI Vasall erklaert eigenmaechtig Krieg gegen Hegemon
    elif iData1 == 691:
      do691(iData2, iData3, iData4)


def do671(iWinner, iLoser, iGold, iData5):

  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Botschafter Kill
  # Verschlechterung der Beziehungen um -1
  # Verbesserung der Beziehungen mit jenen, die mit diesem im Krieg sind um +1
  if iGold == -1:
    # Verlierer bekommt Absage
    if iData5 == 0:
      # Verlierer bekommt -1 zum Gewinner
      pLoser.AI_changeAttitudeExtra(iWinner,-1)
      # Alle, die mit dem Verlierer im Krieg sind, bekommen zum Gewinner +1
      # ausser die Vasallen des Gewinners
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        if gc.getPlayer(i).isAlive():
          iTeam = gc.getPlayer(i).getTeam()
          if pLoserTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(iWinnerTeam): gc.getPlayer(i).AI_changeAttitudeExtra(iWinner,1)
    # Gewinner bekommt Absage
    else:
      # Gewinner bekommt -1 zum Verlierer
      pWinner.AI_changeAttitudeExtra(iLoser,-1)
      # Alle, die mit dem Gewinner im Krieg sind, bekommen zum Verlierer +1
      # ausser die Vasallen des Verlierers
      iRange = gc.getMAX_PLAYERS()
      for i in range(iRange):
        if gc.getPlayer(i).isAlive():
          iTeam = gc.getPlayer(i).getTeam()
          if pWinnerTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(iLoserTeam): gc.getPlayer(i).AI_changeAttitudeExtra(iLoser,1)
  else:
    if pLoserTeam.isAVassal(): VassalUnsetHegemon(iLoser) # Vasall verliert seinen Hegemon
    VassalHegemonGetsVassal(iLoser) # Hegemon verliert seine Vasallen
    pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
    pWinner.changeGold(iGold)
    pLoser.changeGold(iGold * (-1))
    if iWinner == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

def do682(iWinner, iLoser, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Loser moechte nix zu tun haben = 1a
  # Winner bietet Hegemonschaft an
  if iGold == -1:
    iGold1 = myRandom(pWinner.getGold() / 4)
    if iGold1 < pWinner.getGold() / 8: iGold1 = pWinner.getGold() / 8 + iGold1
    iGold2 = iGold1 * 2
    iGold1 = int(iGold1)
    iGold2 = int(iGold2)
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(iGold1)
    popupInfo.setFlags(iGold2)
    popupInfo.setOnClickedPythonCallback("popupVassal04") # EntryPoints/CvScreenInterface und CvGameUtils / 683
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_1",(iGold1,pWinner.getCivilizationAdjective(2))), "")
    if iGold2 > 0: popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_2",(iGold2,pWinner.getCivilizationAdjective(2))), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_04_NO",()), "")
    popupInfo.addPopup(iWinner)
  # Loser schlagt vor, Winner entscheidet = 1b
  else:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0),iGold)) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(iGold)
    popupInfo.setOnClickedPythonCallback("popupVassal06") # EntryPoints/CvScreenInterface und CvGameUtils / 685
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06_YES",()), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_06_NO",()), "")
    iRand = 1 + myRandom(9)
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
    popupInfo.addPopup(iWinner)

def do683(iWinner, iLoser, iData4):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Winner bietet Hegemonschaft an
  # Loser entscheidet
  if iData4 >= 0:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0),iData4)) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(iData4)
    popupInfo.setOnClickedPythonCallback("popupVassal05") # EntryPoints/CvScreenInterface und CvGameUtils / 684
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_YES",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_NO",(iData4,)), "")
    iRand = 1 + myRandom(9)
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
    popupInfo.addPopup(iLoser)

def do684(iWinner, iLoser, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Winner bietet Hegemonschaft an
  # Loser nicht einverstanden
  if iGold == 0:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(1) # zur Winnerauswahl
    popupInfo.setOnClickedPythonCallback("popupVassal07") # EntryPoints/CvScreenInterface und CvGameUtils / 686 / 1
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_YES",()), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_NO",()), "")
    popupInfo.addPopup(iWinner)

  # Botschafter vom Winner wird gekillt
  elif iGold == -1:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),pLoser.getCivilizationShortDescription(0))) )
    popupInfo.addPopup(iData3)

    # Verschlechterung der Beziehungen des Gewinners zum Verlierer -1
    pWinner.AI_changeAttitudeExtra(iData3,-1)
    # Alle, die mit dem Gewinner im Krieg sind, bekommen zum Verlierer +1
    # ausser die Vasallen des Verlierers
    iRange = gc.getMAX_PLAYERS()
    for i in range(iRange):
      if gc.getPlayer(i).isAlive():
        iTeam = gc.getPlayer(i).getTeam()
        if pWinnerTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pLoserTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iLoser,1)

  else:
    if pLoserTeam.isAVassal(): VassalUnsetHegemon(iData3) # Vasall verliert seinen Hegemon
    VassalHegemonGetsVassal(iLoser) # Hegemon verliert seine Vasallen
    pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
    pLoser.changeGold(iGold)
    pWinner.changeGold(iGold * (-1))
    if iLoser == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

def do685(iWinner, iLoser, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  iWinnerTeam = pWinner.getTeam()
  pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Winner bietet Hegemonschaft an
  # Loser entscheidet

  # Winner lehnt ab, nochmal entscheiden?
  if iGold == 0:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0))) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(0) # zur Loserauswahl
    popupInfo.setOnClickedPythonCallback("popupVassal07") # EntryPoints/CvScreenInterface und CvGameUtils / 686 / 0
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_YES",()), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_07_NO",()), "")
    popupInfo.addPopup(iLoser)

  # Botschafter vom Loser wird gekillt
  elif iGold == -1:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationShortDescription(0))) )
    popupInfo.addPopup(iLoser)
    # Verschlechterung der Beziehungen vom Verlierer zum Gewinner -1
    pLoser.AI_changeAttitudeExtra(iWinner,-1)
    # Alle, die mit dem Verlierer im Krieg sind, bekommen zum Gewinner +1
    # ausser die Vasallen des Gewinners
    iRange = gc.getMAX_PLAYERS()
    for i in range(iRange):
      if gc.getPlayer(i).isAlive():
        iTeam = gc.getPlayer(i).getTeam()
        if pLoserTeam.isAtWar(iTeam) and not gc.getTeam(iTeam).isVassal(pWinnerTeam.getID()): gc.getPlayer(i).AI_changeAttitudeExtra(iWinner,1)

  # Vasall werden
  else:
    if pLoserTeam.isAVassal(): VassalUnsetHegemon(iLoser) # Vasall verliert seinen Hegemon
    VassalHegemonGetsVassal(iLoser) # Hegemon verliert seine Vasallen
    pWinnerTeam.assignVassal (iLoserTeam, 1) # surrender
    pWinner.changeGold(iGold)
    pLoser.changeGold(iGold * (-1))
    if iWinner == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

def do687(iWinner, iLoser, iVassal, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  pVassal = gc.getPlayer(iVassal)

  #iWinnerTeam = pWinner.getTeam()
  #pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)
  iVassalTeam = pVassal.getTeam()
  pVassalTeam = gc.getTeam(iVassalTeam)

  # Vasall vom Hegemon loesen
  pLoserTeam.setVassal (iVassalTeam,0,0)

  # Dann mit allen Frieden schliessen
  iRange = gc.getMAX_PLAYERS()
  for i in range(iRange):
    if gc.getPlayer(i).isAlive():
      iTeam = gc.getPlayer(i).getTeam()
      if pVassalTeam.isAtWar(iTeam) and i != gc.getBARBARIAN_PLAYER(): gc.getTeam(iTeam).makePeace(iVassalTeam)

  # Danach dem alten Hegemon Krieg erklaeren
  pVassalTeam.declareWar(iLoserTeam, 0, 4)
  pVassal.changeGold(iGold)
  pWinner.changeGold(iGold * (-1))
  if iVassal == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

def do688(iWinner, iLoser, iVassal, iFlag):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  pVassal = gc.getPlayer(iVassal)
  #iWinnerTeam = pWinner.getTeam()
  #pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  #pLoserTeam = gc.getTeam(iLoserTeam)

  if iFlag == 0:
    gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)
    # Beziehungsstatus aendern
    pLoser.AI_changeAttitudeExtra(iVassal,-2)
    pWinner.AI_changeAttitudeExtra(iVassal,2)
    if pWinner.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
      popupInfo.addPopup(iWinner)
    if pLoser.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_2",(pVassal.getCivilizationAdjective(4),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
      popupInfo.addPopup(iLoser)
  else:
    # Beziehungsstatus aendern
    pLoser.AI_changeAttitudeExtra(iVassal,3)
    pWinner.AI_changeAttitudeExtra(iVassal,-1)
    if pWinner.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_3",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
      popupInfo.addPopup(iWinner)
    if pLoser.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_09_4",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),)) )
      popupInfo.addPopup(iLoser)

def do689(iWinner, iLoser, iVassal, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  pVassal = gc.getPlayer(iVassal)
  #iWinnerTeam = pWinner.getTeam()
  #pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  #pLoserTeam = gc.getTeam(iLoserTeam)

  # Winner bietet dem Vasall ein Angebot an (iData5 = Gold)
  if iGold > 0:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),iGold,gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription())) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(iVassal)
    popupInfo.setFlags(iGold)
    popupInfo.setOnClickedPythonCallback("popupVassal11") # EntryPoints/CvScreenInterface und CvGameUtils / 690
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription())), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_NO",()), "")
    iRand = 1 + myRandom(9)
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_KILL_"+str(iRand),(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),)), "")
    popupInfo.addPopup(iVassal)

  # Winner hat kein Interesse
  # Vasall darf entscheiden, ob er Krieg erklaert
  else:
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12",(gc.getLeaderHeadInfo(pWinner.getLeaderType()).getDescription(),pWinner.getCivilizationAdjective(2) )) )
    popupInfo.setData1(iWinner)
    popupInfo.setData2(iLoser)
    popupInfo.setData3(iVassal)
    popupInfo.setOnClickedPythonCallback("popupVassal12") # EntryPoints/CvScreenInterface und CvGameUtils / 691
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_YES",(gc.getLeaderHeadInfo(pLoser.getLeaderType()).getDescription(),)), "")
    popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_NO",()), "")
    popupInfo.addPopup(iVassal)

def do690(iWinner, iLoser, iVassal, iGold):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  pVassal = gc.getPlayer(iVassal)
  #iWinnerTeam = pWinner.getTeam()
  #pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Botschafter-Kill
  if iGold == -1:
    pWinner.AI_changeAttitudeExtra(iVassal,-1)
    if pWinner.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT) # Vorsicht Text PopUp only!
      popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_05_1",(gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription(),pVassal.getCivilizationShortDescription(0))) )
      popupInfo.addPopup(iWinner)

  # Angebot angenommen mit Kriegserklaerung
  else:
    # Zuerst mit allen Frieden schliessen
    iVassalTeam = pVassal.getTeam()
    pVassalTeam = gc.getTeam(iVassalTeam)
    iRange = gc.getMAX_PLAYERS()
    for i in range(iRange):
      if gc.getPlayer(i).isAlive():
        iTeam = gc.getPlayer(i).getTeam()
        if pVassalTeam.isAtWar(iTeam) and i != gc.getBARBARIAN_PLAYER(): gc.getTeam(iTeam).makePeace(iVassalTeam)

    # Vom Hegemon loesen
    pLoserTeam.setVassal(pVassal.getTeam(),0,0)

    # Danach Krieg erklaeren
    gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)
    pVassal.changeGold(iGold)
    pWinner.changeGold(iGold * (-1))
    if iVassal == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')

    if pWinner.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_11_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription())))
      popupInfo.addPopup(iWinner)

def do691(iWinner, iLoser, iVassal):
  pWinner = gc.getPlayer(iWinner)
  pLoser = gc.getPlayer(iLoser)
  pVassal = gc.getPlayer(iVassal)
  #iWinnerTeam = pWinner.getTeam()
  #pWinnerTeam = gc.getTeam(iWinnerTeam)
  iLoserTeam = pLoser.getTeam()
  pLoserTeam = gc.getTeam(iLoserTeam)

  # Vom Hegemon loesen
  pLoserTeam.setVassal(pVassal.getTeam(),0,0)
  gc.getTeam(pVassal.getTeam()).declareWar(iLoserTeam, 0, 4)

  if pWinner.isHuman():
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
    popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_12_1",(pVassal.getCivilizationAdjective(3),gc.getLeaderHeadInfo(pVassal.getLeaderType()).getDescription() )) )
    popupInfo.addPopup(iWinner)

# 702 , iHegemon (HI) , iVassal, iTech , iTechCost
# Yes  : iTech und iTechCost = -1 (+1 Beziehung)
# Money: iTech und iTechCost
# NO:  : iTech = -1
def do702(iHegemon, iVassal, iTech, iTechCost):
  pHegemon = gc.getPlayer(iHegemon)
  pVassal = gc.getPlayer(iVassal)
  iVassalTeam = pVassal.getTeam()
  pVassalTeam = gc.getTeam(iVassalTeam)

  # Yes
  if iTech > -1 and iTechCost == -1:
    pVassalTeam.setHasTech(iTech, 1, iVassal, 0, 1)
    if pVassal.isHuman():
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_GETTING_TECH",(gc.getTechInfo(iTech).getDescription(),)))
      popupInfo.addPopup(iVassal)
    else: pVassal.AI_changeAttitudeExtra(iHegemon,1)

  # Money
  elif iTech > -1:
    if pVassal.getGold() >= iTechCost:
      # HI - HI Konfrontation
      if pVassal.isHuman():
        popupInfo = CyPopupInfo()
        popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
        popupInfo.setText( CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2",(gc.getTechInfo(iTech).getDescription(),iTechCost)))
        popupInfo.setData1(iHegemon)
        popupInfo.setData2(iVassal)
        popupInfo.setData3(iTech)
        popupInfo.setFlags(iTechCost)
        popupInfo.setOnClickedPythonCallback("popupVassalTech2") # EntryPoints/CvScreenInterface und CvGameUtils / 702
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_YES",("",iTechCost)), "")
        popupInfo.addPythonButton(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_NO",("",)), "")
        popupInfo.addPopup(iVassal)
      else:
        pVassalTeam.setHasTech(iTech, 1, iVassal, 0, 1)
        pVassal.changeGold(-iTechCost)
        pHegemon.changeGold(iTechCost)
        if iData2 == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')
        CyInterface().addMessage(iHegemon, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_THX",(gc.getTechInfo(iTech).getDescription(),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
    else:
      popupInfo = CyPopupInfo()
      popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
      popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_HAS_NO_MONEY",(gc.getTechInfo(iTech).getDescription(), iTechCost)))
      popupInfo.addPopup(iHegemon)

  # No
  elif not pVassal.isHuman(): pVassal.AI_changeAttitudeExtra(iHegemon,-1)

# 703 , iHegemon (HI) , iVassal (HI), iTech , iTechCost
# Yes  : iTech und iTechCost
# NO:  : iTechCost = -1
def do703(iHegemon, iVassal, iTech, iTechCost):
  pHegemon = gc.getPlayer(iHegemon)
  pVassal = gc.getPlayer(iVassal)
  iVassalTeam = pVassal.getTeam()
  pVassalTeam = gc.getTeam(iVassalTeam)

  if iTechCost == -1:
    CyInterface().addMessage(iHegemon, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_DECLINE",("",)), None, 2, None, ColorTypes(8), 0, 0, False, False)
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_2_DECLINE",("", )))
    popupInfo.addPopup(iHegemon)
  else:
    pVassalTeam.setHasTech(iTech, 1, iVassal, 0, 1)
    pVassal.changeGold(-iTechCost)
    pHegemon.changeGold(iTechCost)
    if iHegemon == gc.getGame().getActivePlayer(): CyAudioGame().Play2DSound('AS2D_COINS')
    # Meldungen
    CyInterface().addMessage(iHegemon, True, 10, CyTranslator().getText("TXT_KEY_POPUP_VASSAL_TECH_THX",(gc.getTechInfo(iTech).getDescription (),)), None, 2, None, ColorTypes(8), 0, 0, False, False)
    popupInfo = CyPopupInfo()
    popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
    popupInfo.setText(CyTranslator().getText("TXT_KEY_POPUP_VASSAL_GETTING_TECH",(gc.getTechInfo(iTech).getDescription(),)))
    popupInfo.addPopup(iVassal)