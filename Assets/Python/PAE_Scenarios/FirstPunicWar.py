# Scenario FirstPunicWar

# Imports
from CvPythonExtensions import *
import CvEventInterface
import CvUtil
import PyHelpers

# Defines
gc = CyGlobalContext()


def onEndPlayerTurn(iPlayer, iGameTurn):
    # Runde 1: In der ersten Runde soll sich Messana an Rom als Vasall anbieten
    if iGameTurn == 0:
        iCivRome = 0
        iCivCarthage = 1
        iCivMessana = 4
        iCivSyrakus = 12
        if iPlayer == iCivMessana:

            iTeamRome = gc.getPlayer(iCivRome).getTeam()
            iTeamMessana = gc.getPlayer(iCivMessana).getTeam()
            pTeamMessana = gc.getTeam(iTeamMessana)
            if not pTeamMessana.isVassal(iTeamRome):

                iTeamRome = gc.getPlayer(iCivRome).getTeam()
                gc.getTeam(iTeamRome).assignVassal(iTeamMessana, 0)  # Vassal, but no surrender

                # Meldungen an die Spieler
                iRange = gc.getMAX_PLAYERS()
                for iLoopPlayer in range(iRange):
                    pPlayer = gc.getPlayer(iLoopPlayer)
                    if pPlayer.isHuman():
                        # Meldung Karthago Human
                        if iLoopPlayer == iCivCarthage:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_CARTHAGE", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_CARTHAGE", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                        elif iLoopPlayer == iCivRome:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_ALL", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_WAR_PLAYER_ROME", ("",)))
                            popupInfo.addPopup(iLoopPlayer)
                        # Meldung an alle Humans
                        else:
                            popupInfo = CyPopupInfo()
                            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_TEXT)
                            popupInfo.setText(CyTranslator().getText("TXT_KEY_MESSANA_PLAYER_ALL", ("",)))
                            popupInfo.addPopup(iLoopPlayer)


def onCombatResult(pWinner, pLoser):
    if pLoser.getUnitType() == gc.getInfoTypeForString("UNIT_QUADRIREME"):
        if gc.getPlayer(pWinner.getOwner()).getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME"):
            iTech = gc.getInfoTypeForString("TECH_WARSHIPS")
            iTeam = gc.getPlayer(pWinner.getOwner()).getTeam()
            pTeam = gc.getTeam(iTeam)
            if not pTeam.isHasTech(iTech):
                pTeam.setHasTech(iTech, 1, pWinner.getOwner(), 0, 1)


def onCityAcquired(pCity, iNewOwner):
    iCivRome = 0  # Capital: Rome
    iCivCarthage = 1  # Capital: Carthage
    sData = CvUtil.getScriptData(pCity.plot(), ["t"])
    if sData == "Rome" and iNewOwner != iCivRome or sData == "Carthage" and iNewOwner == iCivRome:

        # PAE Movie
        if gc.getPlayer(iNewOwner).isHuman():
            if iNewOwner == iCivRome:
                iMovie = 1
            else:
                iMovie = 2
            popupInfo = CyPopupInfo()
            popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON_SCREEN)
            popupInfo.setData1(iMovie)  # dynamicID in CvWonderMovieScreen
            popupInfo.setData2(0)  # fix pCity.getID()
            popupInfo.setData3(3)  # fix PAE Movie ID for victory movies
            popupInfo.setText(u"showWonderMovie")
            popupInfo.addPopup(iNewOwner)

        gc.getGame().setWinner(gc.getPlayer(iNewOwner).getTeam(), 2)
