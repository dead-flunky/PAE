## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Edited by pie (pierre@voak.at), Austria 2011
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvPediaUnit:
        "Civilopedia Screen for Units"

        def __init__(self, main):
                self.iUnit = -1
                self.top = main

                self.X_UNIT_PANE = 10
                self.Y_UNIT_PANE = 57
                self.W_UNIT_PANE = 390 # 360
                self.H_UNIT_PANE = 180 # 165

                self.X_UNIT_ANIMATION = 410 # 386
                self.Y_UNIT_ANIMATION = 65
                self.W_UNIT_ANIMATION = 370 # 388
                self.H_UNIT_ANIMATION = 171 # 156
                self.X_ROTATION_UNIT_ANIMATION = -20
                self.Z_ROTATION_UNIT_ANIMATION = 30
                self.SCALE_ANIMATION = 1.0

                self.X_ICON = 33
                self.Y_ICON = 90
                self.W_ICON = 100
                self.H_ICON = 100
                self.ICON_SIZE = 64

                self.BUTTON_SIZE = 64
                self.PROMOTION_ICON_SIZE = 32

                self.X_STATS_PANE = 150
                self.Y_STATS_PANE = 103
                self.W_STATS_PANE = 250
                self.H_STATS_PANE = 200

                self.X_SPECIAL_PANE = 10
                self.Y_SPECIAL_PANE = 357
                self.W_SPECIAL_PANE = 390 # 360
                self.H_SPECIAL_PANE = 187

                self.X_PREREQ_PANE = 10
                self.Y_PREREQ_PANE = 232
                self.W_PREREQ_PANE = 390 # 360
                self.H_PREREQ_PANE = 115

                self.X_UPGRADES_TO_PANE = 410 # 385
                self.Y_UPGRADES_TO_PANE = 232
                self.W_UPGRADES_TO_PANE = 370 # 390
                self.H_UPGRADES_TO_PANE = 115

                self.X_PROMO_PANE = 10
                self.Y_PROMO_PANE = 553
                self.W_PROMO_PANE = 390 # 360
                self.H_PROMO_PANE = 153

                self.X_HISTORY_PANE = 410 # 385
                self.Y_HISTORY_PANE = 357
                self.W_HISTORY_PANE = 370 # 628
                self.H_HISTORY_PANE = 349


        # Screen construction function
        def interfaceScreen(self, iUnit):

                self.iUnit = iUnit

                self.top.deleteAllWidgets()

                screen = self.top.getScreen()

                bNotActive = (not screen.isActive())
                if bNotActive: # or self.top.iLastScreen != CvScreenEnums.PEDIA_UNIT: # PAE different Link menu height
                        self.top.setPediaCommonWidgets()

                # Header...
                szHeader = u"<font=4b>" + gc.getUnitInfo(self.iUnit).getDescription().upper() + u"</font>"
                screen.setLabel(self.top.getNextWidgetName(), "Background", szHeader, CvUtil.FONT_CENTER_JUSTIFY, self.top.X_SCREEN, self.top.Y_TITLE, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT, iUnit)

                # Top
                screen.setText(self.top.getNextWidgetName(), "Background", self.top.MENU_TEXT, CvUtil.FONT_LEFT_JUSTIFY, self.top.X_MENU, self.top.Y_MENU, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_MAIN, CivilopediaPageTypes.CIVILOPEDIA_PAGE_UNIT, -1)

                if self.top.iLastScreen != CvScreenEnums.PEDIA_UNIT or bNotActive:
                        self.placeLinks(true)
                        self.top.iLastScreen = CvScreenEnums.PEDIA_UNIT
                else:
                        self.placeLinks(false)

                # Icon
                screen.addPanel( self.top.getNextWidgetName(), "", "", False, False,
                    self.X_UNIT_PANE, self.Y_UNIT_PANE, self.W_UNIT_PANE, self.H_UNIT_PANE, PanelStyles.PANEL_STYLE_BLUE50)
                screen.addPanel(self.top.getNextWidgetName(), "", "", false, false,
                    self.X_ICON, self.Y_ICON, self.W_ICON, self.H_ICON, PanelStyles.PANEL_STYLE_MAIN)
                szButton = gc.getUnitInfo(self.iUnit).getButton()
                if self.top.iActivePlayer != -1:
                        szButton = gc.getPlayer(self.top.iActivePlayer).getUnitButton(self.iUnit)
                screen.addDDSGFC(self.top.getNextWidgetName(), szButton,
                    self.X_ICON + self.W_ICON/2 - self.ICON_SIZE/2, self.Y_ICON + self.H_ICON/2 - self.ICON_SIZE/2, self.ICON_SIZE, self.ICON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1 )

                # Unit animation
                screen.addUnitGraphicGFC(self.top.getNextWidgetName(), self.iUnit, self.X_UNIT_ANIMATION, self.Y_UNIT_ANIMATION, self.W_UNIT_ANIMATION, self.H_UNIT_ANIMATION, WidgetTypes.WIDGET_GENERAL, -1, -1, self.X_ROTATION_UNIT_ANIMATION, self.Z_ROTATION_UNIT_ANIMATION, self.SCALE_ANIMATION, True)

                self.placeStats()

                self.placeUpgradesTo()

                self.placeRequires()

                self.placeSpecial()

                self.placePromotions()

                self.placeHistory()

        # Place strength/movement
        def placeStats(self):

                screen = self.top.getScreen()

                panelName = self.top.getNextWidgetName()

                # PAE: Unit class
                iUnitClass = gc.getUnitInfo(self.iUnit).getUnitClassType()

                # Unit combat group
                iCombatType = gc.getUnitInfo(self.iUnit).getUnitCombatType()
                if (iCombatType != -1):
                        screen.setImageButton(self.top.getNextWidgetName(), gc.getUnitCombatInfo(iCombatType).getButton(), self.X_STATS_PANE + 7, self.Y_STATS_PANE - 36, 32, 32, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)
                        screen.setText(self.top.getNextWidgetName(), "", u"<font=4>" + gc.getUnitCombatInfo(iCombatType).getDescription() + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, self.X_STATS_PANE + 45, self.Y_STATS_PANE - 31, 0, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iCombatType, 0)

                screen.addListBoxGFC(panelName, "", self.X_STATS_PANE, self.Y_STATS_PANE, self.W_STATS_PANE, self.H_STATS_PANE, TableStyles.TABLE_STYLE_EMPTY)
                screen.enableSelect(panelName, False)

                if (gc.getUnitInfo(self.iUnit).getAirCombat() > 0 and gc.getUnitInfo(self.iUnit).getCombat() == 0):
                        iStrength = gc.getUnitInfo(self.iUnit).getAirCombat()
                else:
                        iStrength = gc.getUnitInfo(self.iUnit).getCombat()

                szName = self.top.getNextWidgetName()
                szStrength = localText.getText("TXT_KEY_PEDIA_STRENGTH", ( iStrength, ) )
                screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szStrength.upper() + u"%c" % CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                szName = self.top.getNextWidgetName()
                szMovement = localText.getText("TXT_KEY_PEDIA_MOVEMENT", ( gc.getUnitInfo(self.iUnit).getMoves(), ) )
                screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szMovement.upper() + u"%c" % CyGame().getSymbolID(FontSymbols.MOVES_CHAR) + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                if (gc.getUnitInfo(self.iUnit).getProductionCost() >= 0 and not gc.getUnitInfo(self.iUnit).isFound()):
                        szName = self.top.getNextWidgetName()
                        if self.top.iActivePlayer == -1:
                                szCost = localText.getText("TXT_KEY_PEDIA_COST", ((gc.getUnitInfo(self.iUnit).getProductionCost() * gc.getDefineINT("UNIT_PRODUCTION_PERCENT"))/100,))
                        else:
                                szCost = localText.getText("TXT_KEY_PEDIA_COST", ( gc.getActivePlayer().getUnitProductionNeeded(self.iUnit), ) )
                        screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szCost.upper() + u"%c" % gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                if (gc.getUnitInfo(self.iUnit).getAirRange() > 0):
                        szName = self.top.getNextWidgetName()
                        szRange = localText.getText("TXT_KEY_PEDIA_RANGE", ( gc.getUnitInfo(self.iUnit).getAirRange(), ) )
                        screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szRange.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                # PAE more infos
                if gc.getUnitClassInfo(iUnitClass).getMaxPlayerInstances() != -1:
                        szName = self.top.getNextWidgetName()
                        szText = localText.getText("TXT_KEY_PEDIA_MAX_PLAYER", ( gc.getUnitClassInfo(iUnitClass).getMaxPlayerInstances(), ) )
                        screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                if gc.getUnitClassInfo(iUnitClass).getMaxGlobalInstances() != -1:
                        szName = self.top.getNextWidgetName()
                        szText = localText.getText("TXT_KEY_PEDIA_MAX_GLOBAL", ( gc.getUnitClassInfo(iUnitClass).getMaxGlobalInstances(), ) )
                        screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)

                if (gc.getUnitInfo(self.iUnit).getExtraCost() > 0):
                        szName = self.top.getNextWidgetName()
                        szText = localText.getText("TXT_KEY_UNIT_EXTRA_COST", ( gc.getUnitInfo(self.iUnit).getExtraCost(), ) )
                        screen.appendListBoxStringNoUpdate(panelName, u"<font=3>" + szText.upper() + u"</font>", WidgetTypes.WIDGET_GENERAL, 0, 0, CvUtil.FONT_LEFT_JUSTIFY)


                screen.updateListBox(panelName)

        # Place prereqs (techs, resources)
        def placeRequires(self):

                screen = self.top.getScreen()

                panelName = self.top.getNextWidgetName()
                screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_REQUIRES", ()), "", false, true, self.X_PREREQ_PANE, self.Y_PREREQ_PANE, self.W_PREREQ_PANE, self.H_PREREQ_PANE, PanelStyles.PANEL_STYLE_BLUE50 )

                screen.attachLabel(panelName, "", "  ")

                # BTS was: Tech | Bonus | Religion | Building | Coorp
                # PAE swaps displayed requirements: Tech | Religion | Building | Coorp | Bonus (Bonus at last because of AND and OR)

                # add tech buttons
                iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTech()
                if (iPrereq >= 0):
                        screen.attachImageButton( panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, 1, False )

                for j in range(gc.getDefineINT("NUM_UNIT_AND_TECH_PREREQS")):
                        iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndTechs(j)
                        if (iPrereq >= 0):
                                screen.attachImageButton( panelName, "", gc.getTechInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iPrereq, -1, False )

                # add religion buttons
                iPrereq = gc.getUnitInfo(self.iUnit).getPrereqReligion()
                if (iPrereq >= 0):
                        screen.attachImageButton( panelName, "", gc.getReligionInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_RELIGION, iPrereq, -1, False )

                # add building buttons
                iPrereq = gc.getUnitInfo(self.iUnit).getPrereqBuilding()
                if (iPrereq >= 0):
                        screen.attachImageButton( panelName, "", gc.getBuildingInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BUILDING, iPrereq, -1, False )

                # PAE - add corporation button
                iPrereq = gc.getUnitInfo(self.iUnit).getPrereqCorporation()
                if (iPrereq >= 0):
                        screen.attachImageButton( panelName, "", gc.getCorporationInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CORPORATION, iPrereq, -1, False )

                # add resource buttons
                bFirst = True
                iPrereq = gc.getUnitInfo(self.iUnit).getPrereqAndBonus()
                if (iPrereq >= 0):
                        bFirst = False
                        screen.attachImageButton( panelName, "", gc.getBonusInfo(iPrereq).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iPrereq, -1, False )

                # count the number of OR resources
                nOr = 0
                for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
                        if (gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j) > -1):
                                nOr += 1

                szLeftDelimeter = ""
                szRightDelimeter = ""
                #  Display a bracket if we have more than one OR resource and an AND resource
                if (not bFirst):
                        if (nOr > 1):
                                szLeftDelimeter = localText.getText("TXT_KEY_AND", ()) + "( "
                                szRightDelimeter = " ) "
                        elif (nOr > 0):
                                szLeftDelimeter = localText.getText("TXT_KEY_AND", ())

                if len(szLeftDelimeter) > 0:
                        screen.attachLabel(panelName, "", szLeftDelimeter)

                bFirst = True
                for j in range(gc.getNUM_UNIT_PREREQ_OR_BONUSES()):
                        eBonus = gc.getUnitInfo(self.iUnit).getPrereqOrBonuses(j)
                        if (eBonus > -1):
                                if (not bFirst):
                                        screen.attachLabel(panelName, "", localText.getText("TXT_KEY_OR", ()))
                                else:
                                        bFirst = False
                                screen.attachImageButton( panelName, "", gc.getBonusInfo(eBonus).getButton(), GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, eBonus, -1, False )

                if len(szRightDelimeter) > 0:
                        screen.attachLabel(panelName, "", szRightDelimeter)


        # Place upgrades
        def placeUpgradesTo(self):

                screen = self.top.getScreen()

                panelName = self.top.getNextWidgetName()
                screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_UPGRADES_TO", ()), "", false, true, self.X_UPGRADES_TO_PANE, self.Y_UPGRADES_TO_PANE, self.W_UPGRADES_TO_PANE, self.H_UPGRADES_TO_PANE, PanelStyles.PANEL_STYLE_BLUE50)

                screen.attachLabel(panelName, "", "  ")

                for k in range(gc.getNumUnitClassInfos()):
                        if self.top.iActivePlayer == -1:
                                eLoopUnit = gc.getUnitClassInfo(k).getDefaultUnitIndex()
                        else:
                                eLoopUnit = gc.getCivilizationInfo(gc.getGame().getActiveCivilizationType()).getCivilizationUnits(k)

                        if (eLoopUnit >= 0 and gc.getUnitInfo(self.iUnit).getUpgradeUnitClass(k)):
                                szButton = gc.getUnitInfo(eLoopUnit).getButton()
                                if self.top.iActivePlayer != -1:
                                        szButton = gc.getPlayer(self.top.iActivePlayer).getUnitButton(eLoopUnit)
                                screen.attachImageButton( panelName, "", szButton, GenericButtonSizes.BUTTON_SIZE_CUSTOM, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, eLoopUnit, 1, False )

        # Place Special abilities
        def placeSpecial(self):

                screen = self.top.getScreen()

                panelName = self.top.getNextWidgetName()
                screen.addPanel( panelName, localText.getText("TXT_KEY_PEDIA_SPECIAL_ABILITIES", ()), "", true, false,
                                 self.X_SPECIAL_PANE, self.Y_SPECIAL_PANE, self.W_SPECIAL_PANE, self.H_SPECIAL_PANE, PanelStyles.PANEL_STYLE_BLUE50 )

                listName = self.top.getNextWidgetName()

                szSpecialText = CyGameTextMgr().getUnitHelp( self.iUnit, True, False, False, None )[1:]
                screen.addMultilineText(listName, szSpecialText, self.X_SPECIAL_PANE+5, self.Y_SPECIAL_PANE+30, self.W_SPECIAL_PANE-10, self.H_SPECIAL_PANE-35, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

        def placeHistory(self):

                screen = self.top.getScreen()

                panelName = self.top.getNextWidgetName()
                screen.addPanel( panelName, localText.getText("TXT_KEY_CIVILOPEDIA_HISTORY", ()), "", True, True,
                                                self.X_HISTORY_PANE, self.Y_HISTORY_PANE,
                                                self.W_HISTORY_PANE, self.H_HISTORY_PANE,
                                                PanelStyles.PANEL_STYLE_BLUE50 )

                textName = self.top.getNextWidgetName()
                szText = u""
                if len(gc.getUnitInfo(self.iUnit).getStrategy()) > 0:
                        szText += localText.getText("TXT_KEY_CIVILOPEDIA_STRATEGY", ())
                        szText += gc.getUnitInfo(self.iUnit).getStrategy()
                        szText += u"\n\n"
                szText += localText.getText("TXT_KEY_CIVILOPEDIA_BACKGROUND", ())
                szText += gc.getUnitInfo(self.iUnit).getCivilopedia()
                screen.addMultilineText( textName, szText, self.X_HISTORY_PANE + 15, self.Y_HISTORY_PANE + 40,
                    self.W_HISTORY_PANE - (15 * 2), self.H_HISTORY_PANE - (15 * 2) - 25, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

        def placePromotions(self):
                screen = self.top.getScreen()

                # add pane and text
                panelName = self.top.getNextWidgetName()
                screen.addPanel(panelName, localText.getText("TXT_KEY_PEDIA_CATEGORY_PROMOTION", ()), "", true, true, self.X_PROMO_PANE, self.Y_PROMO_PANE, self.W_PROMO_PANE, self.H_PROMO_PANE, PanelStyles.PANEL_STYLE_BLUE50 )

                # add promotion buttons
                rowListName = self.top.getNextWidgetName()
                screen.addMultiListControlGFC(rowListName, "", self.X_PROMO_PANE+15, self.Y_PROMO_PANE+40, self.W_PROMO_PANE-20, self.H_PROMO_PANE-40, 1, self.PROMOTION_ICON_SIZE, self.PROMOTION_ICON_SIZE, TableStyles.TABLE_STYLE_STANDARD)

                for k in range(gc.getNumPromotionInfos()):
                        if (isPromotionValid(k, self.iUnit, false) and not gc.getPromotionInfo(k).isGraphicalOnly()):
                                screen.appendMultiListButton( rowListName, gc.getPromotionInfo(k).getButton(), 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, k, -1, false )

        def placeLinks(self, bRedraw):

                screen = self.top.getScreen()

                if bRedraw:
                        screen.clearListBoxGFC(self.top.LIST_ID)

                # sort Units alphabetically
                #unitsList=[(0,0)]*gc.getNumUnitInfos()
                #for j in range(gc.getNumUnitInfos()):
                #        unitsList[j] = (gc.getUnitInfo(j).getDescription(), j)
                #unitsList.sort()

                unitsList = self.getUnitSortedList(self.getUnitType(self.iUnit))

                i = 0
                iSelected = 0
                #for iI in range(gc.getNumUnitInfos()):
                for iI in range(len(unitsList)):
                        if (not gc.getUnitInfo(unitsList[iI][1]).isGraphicalOnly()):
                                if (not gc.getDefineINT("CIVILOPEDIA_SHOW_ACTIVE_CIVS_ONLY") or not gc.getGame().isFinalInitialized() or gc.getGame().isUnitEverActive(unitsList[iI][1])):
                                        if bRedraw:
                                                screen.appendListBoxStringNoUpdate( self.top.LIST_ID, unitsList[iI][0], WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT, unitsList[iI][1], 0, CvUtil.FONT_LEFT_JUSTIFY )
                                        if unitsList[iI][1] == self.iUnit:
                                                iSelected = i
                                        i += 1

                if bRedraw:
                        screen.updateListBox(self.top.LIST_ID)

                screen.setSelectedListBoxStringGFC(self.top.LIST_ID, iSelected)

        # PAE add on : normal units / special units ------------------

        def getStandardUnits(self):
            list = []
            for i in range(gc.getNumUnitClassInfos()):
                iUnit = gc.getUnitClassInfo(i).getDefaultUnitIndex()
                if iUnit != -1 and gc.getUnitInfo(iUnit).getProductionCost() > 0:
                   #and gc.getUnitClassInfo(i).getMaxPlayerInstances() == -1 \
                   #and gc.getUnitClassInfo(i).getMaxGlobalInstances() == -1 \
                   #and gc.getUnitClassInfo(i).getMaxTeamInstances() == -1:
                   list.append(iUnit)
            return list

        def getUnitType(self, iUnit):

            lUnitClasses = self.getStandardUnits()

            #if iUnit not in lUnitClasses: return 1
            if iUnit not in lUnitClasses: return 1
            # Regular unit
            return 0

        # iType
        # 0: normal
        # 1: Special
        def getUnitSortedList(self, iType):
                listUnits = []
                iCount = 0

                lStandardUnits = self.getStandardUnits()

                for iUnit in range(gc.getNumUnitInfos()):
                    if iType == 1 and iUnit not in lStandardUnits:
                       listUnits.append(iUnit)
                       iCount += 1
                    elif iType == 0 and iUnit in lStandardUnits:
                       listUnits.append(iUnit)
                       iCount += 1

                listSorted = [(0,0)] * iCount
                iI = 0
                for iUnit in listUnits:
                        listSorted[iI] = (gc.getUnitInfo(iUnit).getDescription(), iUnit)
                        iI += 1
                listSorted.sort()
                return listSorted

        # Will handle the input for this screen...
        def handleInput (self, inputClass):
                return 0