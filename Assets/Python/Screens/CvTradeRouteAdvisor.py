## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Created by Pie, Austria
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import PAE_Trade

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

class CvTradeRouteAdvisor:

  def __init__(self):
    self.SCREEN_NAME = "TradeRouteAdvisor"
    self.DEBUG_DROPDOWN_ID =  "TradeRouteAdvisorDropdownWidget"
    self.WIDGET_ID = "TradeRouteAdvisorWidget"
    self.WIDGET_HEADER = "TradeRouteAdvisorWidgetHeader"
    self.EXIT_ID = "TradeRouteAdvisorExitWidget"
    self.BACKGROUND_ID = "TradeRouteAdvisorBackground"
    self.X_SCREEN = 500
    self.Y_SCREEN = 396
    self.W_SCREEN = 1024
    self.H_SCREEN = 768
    self.Y_TITLE = 12
    self.Z_CONTROLS = -2.0

    self.X_EXIT = 994
    self.Y_EXIT = 726

    self.nWidgetCount = 0

    self.iTargetPlayer = -1
    self.iActiveCityID = -1
    self.iSelectedMission = -1

  def getScreen(self):
    return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.TRADEROUTE_ADVISOR)

  def interfaceScreen (self):

    self.iTargetPlayer = -1
    self.iActiveCityID = -1
    self.iSelectedMission = -1
    self.iActivePlayer = CyGame().getActivePlayer()

    screen = self.getScreen()
    if screen.isActive():
      return
    screen.setRenderInterfaceOnly(True);
    screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)

    # Set the background and exit button, and show the screen
    screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

    screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("SCREEN_BG_OPAQUE").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.addPanel( "TechTopPanel", u"", u"", True, False, 0, 0, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_TOPBAR )
    screen.addPanel( "TechBottomPanel", u"", u"", True, False, 0, 713, self.W_SCREEN, 55, PanelStyles.PANEL_STYLE_BOTTOMBAR )

    screen.showWindowBackground(False)
    screen.setText(self.EXIT_ID, "Background", u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>", CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1 )

    # Header...
    screen.setLabel(self.WIDGET_HEADER, "Background", u"<font=4b>" + localText.getText("TXT_KEY_TRADE_ROUTE_ADVISOR_SCREEN", ()).upper() + u"</font>", CvUtil.FONT_CENTER_JUSTIFY, self.X_SCREEN, self.Y_TITLE, self.Z_CONTROLS, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    # draw the contents
    self.drawContents()

    self.refreshScreen()


  def drawContents(self):

    screen = self.getScreen()
    self.deleteAllWidgets()

    # addPanel: Vertical, scrollable, x ,y, width, height

    # +++ 1 +++ PANEL Requests: Trade Requests
    screen.addPanel( "PanelRequests", u"", u"", True, False, 35, 75, 945, 200, PanelStyles.PANEL_STYLE_DAWNTOP )

    BUTTON_SIZE = 48
    iY = 30

    # Cities with Special bonus order
    lCities = PAE_Trade.lCitiesSpecialBonus

    bMessageNoCities = True
    i = 0
    for pCity in lCities:
      i += 1
      if pCity and not pCity.isNone():
       iCityOwner = pCity.getOwner()
       pPlayer = gc.getPlayer(iCityOwner)
       if pPlayer and not pPlayer.isNone():
        pTeam = gc.getTeam(pPlayer.getTeam())
        iPop = pCity.getPopulation()
        iCiv = pPlayer.getCivilizationType()
        iLeader = pPlayer.getLeaderType()
        if pTeam.isHasMet(gc.getPlayer(gc.getGame().getActivePlayer()).getTeam()):
          iBonus = int(CvUtil.getScriptData(pCity, ["tsb"],-1))
          iTurns = int(CvUtil.getScriptData(pCity, ["tst"],-1))
          if iBonus > 0 and iTurns > 0:
            bMessageNoCities = False
            iX = 50
            iY += 60
            # Button Bonus
            screen.setImageButton("Label_1_"+str(i), gc.getBonusInfo(iBonus).getButton(), iX, iY, BUTTON_SIZE, BUTTON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, iBonus, -1)
            iX += 60
            # Text City name
            szText = pCity.getName()
            screen.setLabel("Label_2_"+str(i), "Background", u"<font=4>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+10, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            iX += 220
            # Text Pop
            szText = localText.getText("POP:", ()) + u" %d" %(iPop)
            screen.setLabel("Label_3_"+str(i), "Background", u"<font=4>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+10, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            iX += 90
            # Button Civ
            screen.setImageButton("Label_4_"+str(i), gc.getCivilizationInfo(iCiv).getButton(), iX, iY, BUTTON_SIZE, BUTTON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, iCiv, -1)
            iX += 60
            # Button Leader
            screen.setImageButton("Label_5_"+str(i), gc.getLeaderHeadInfo(iLeader).getButton(), iX, iY, BUTTON_SIZE, BUTTON_SIZE, WidgetTypes.WIDGET_PEDIA_JUMP_TO_LEADER, iLeader, iCiv)
            iX += 60
            # Text Open Borders
            szText = localText.getText("TXT_KEY_MISC_OPEN_BORDERS", ()) + u": "
            if pTeam.isOpenBorders(CyGame().getActiveTeam()):
             szText += localText.getText("TXT_KEY_COLOR_POSITIVE", ()) + localText.getText("TXT_KEY_POPUP_YES", ( )) + localText.getText("TXT_KEY_COLOR_REVERT", ())
            else:
             szText += localText.getText("TXT_KEY_COLOR_NEGATIVE", ()) + localText.getText("TXT_KEY_POPUP_NO", ( )) + localText.getText("TXT_KEY_COLOR_REVERT", ())
            screen.setLabel("Label_6_"+str(i), "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+4, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

            # AI Attitudes - KI Haltung
            iAtt = pPlayer.AI_getAttitude(gc.getGame().getActivePlayer())
            lAttText = ["TXT_KEY_ATTITUDE_FURIOUS","TXT_KEY_ATTITUDE_ANNOYED","TXT_KEY_ATTITUDE_CAUTIOUS","TXT_KEY_ATTITUDE_PLEASED","TXT_KEY_ATTITUDE_FRIENDLY"]
            # Text Attitude
            szText = localText.getText("TXT_KEY_ATTITUDE", ()) + u": %c" %(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 4 + iAtt) + localText.getText(lAttText[iAtt], ())
            screen.setLabel("Label_7_"+str(i), "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+24, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            iX += 200

            # Text Required Bonus
            szText = localText.getText("TXT_KEY_TRADE_ADVISOR_1",()) + u": " + gc.getBonusInfo(iBonus).getDescription()
            screen.setLabel("Label_8_"+str(i), "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+4, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            # Text Remaining Turns
            szText = localText.getText("TXT_KEY_TRADE_ADVISOR_2",()) + u": %d" %(iTurns)
            screen.setLabel("Label_9_"+str(i), "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, iX, iY+24, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    if bMessageNoCities:
      szText = localText.getText("TXT_KEY_TRADE_ADVISOR_INFO", ())
      screen.setLabel("Label1_0", "Background", u"<font=3>" + szText + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, 100, iY+80, 0.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    # +++ 2 +++ PANEL 1-4: Goods (Bonus resources)
    screen.addPanel( "Panel1", u"", u"", True, False,  35, 280, 225, 50, PanelStyles.PANEL_STYLE_DAWNTOP )
    screen.addPanel( "Panel2", u"", u"", True, False, 275, 280, 225, 50, PanelStyles.PANEL_STYLE_DAWNTOP )
    screen.addPanel( "Panel3", u"", u"", True, False, 515, 280, 225, 50, PanelStyles.PANEL_STYLE_DAWNTOP )
    screen.addPanel( "Panel4", u"", u"", True, False, 755, 280, 225, 50, PanelStyles.PANEL_STYLE_DAWNTOP )

    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_TITLE_PANEL1",()).upper() + u"</font>"
    screen.setLabel("TitelPanel1", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 45, 286, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_TITLE_PANEL2",()).upper() + u"</font>"
    screen.setLabel("TitelPanel2", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 285, 286, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_TITLE_PANEL3",()).upper() + u"</font>"
    screen.setLabel("TitelPanel3", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 525, 286, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_TITLE_PANEL4",()).upper() + u"</font>"
    screen.setLabel("TitelPanel4", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 765, 286, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_WERT_PANEL1",()) + u"</font>"
    screen.setLabel("WertPanel1", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 45, 304, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_WERT_PANEL2",()) + u"</font>"
    screen.setLabel("WertPanel2", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 285, 304, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_WERT_PANEL3",()) + u"</font>"
    screen.setLabel("WertPanel3", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 525, 304, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_WERT_PANEL4",()) + u"</font>"
    screen.setLabel("WertPanel4", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 765, 304, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    # Tabellen
    screen.addTableControlGFC("Table1", 1,  40, 340, 215, 310, False, True, 24,24, TableStyles.TABLE_STYLE_STANDARD)
    screen.addTableControlGFC("Table2", 1, 280, 340, 215, 310, False, True, 24,24, TableStyles.TABLE_STYLE_STANDARD)
    screen.addTableControlGFC("Table3", 1, 520, 340, 215, 310, False, True, 24,24, TableStyles.TABLE_STYLE_STANDARD)
    screen.addTableControlGFC("Table4", 1, 760, 340, 215, 310, False, True, 24,24, TableStyles.TABLE_STYLE_STANDARD)

    # Add bonus to tables
    pPlayer = gc.getPlayer(self.iActivePlayer)
    iCol1 = 0
    iCol2 = 0
    iCol3 = 0
    iCol4 = 0
    iNumBonus = gc.getNumBonusInfos()
    for iLoop in range(iNumBonus):
      szName   = gc.getBonusInfo(iLoop).getDescription()
      szButton = gc.getBonusInfo(iLoop).getButton()
      iBonusClassType = gc.getBonusInfo(iLoop).getBonusClassType()
      iBonusTechReveal = gc.getBonusInfo(iLoop).getTechReveal()
      #bShow = False
      #if gc.getTeam(pPlayer.getTeam()).isHasTech(iBonusTechReveal):
      bShow = True

      # BonusclassTypes PAE:
      # 0: BONUSCLASS_GENERAL
      # 1: BONUSCLASS_GRAIN
      # 2: BONUSCLASS_LIVESTOCK
      # 3: BONUSCLASS_MERCENARY
      # 4: BONUSCLASS_LUXURY
      # 5: BONUSCLASS_WONDER
      # 6: BONUSCLASS_MISC
      # 7: BONUSCLASS_RARITY
      # 8: BONUSCLASS_PLANTATION
      if bShow:
       if iBonusClassType == 7:
        screen.appendTableRow("Table1")
        screen.setTableText("Table1", 0, iCol1, szName, szButton, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        iCol1 += 1
       elif iBonusClassType == 4:
        screen.appendTableRow("Table2")
        screen.setTableText("Table2", 0, iCol2, szName, szButton, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        iCol2 += 1
       elif iBonusClassType == 0 or iBonusClassType == 5:
        screen.appendTableRow("Table3")
        screen.setTableText("Table3", 0, iCol3, szName, szButton, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        iCol3 += 1
       elif iBonusClassType == 1 or iBonusClassType == 2 or iBonusClassType == 8:
        screen.appendTableRow("Table4")
        screen.setTableText("Table4", 0, iCol4, szName, szButton, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
        iCol4 += 1


    # +++ 3 +++ PANEL Bottom: Formeln

    screen.addPanel( "PanelBottom", u"", u"", True, False, 40, self.H_SCREEN-110, 935, 50, PanelStyles.PANEL_STYLE_MAIN_BLACK25 )

    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_BOTTOM1",()) + u"</font>"
    screen.setLabel("TextBottom1", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 50, self.H_SCREEN-103, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    szText = u"<font=3>" + localText.getText("TXT_KEY_TRADE_ADVISOR_BOTTOM2",()) + u"</font>"
    screen.setLabel("TextBottom2", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 50, self.H_SCREEN-83, -2.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )


  def refreshScreen(self):

    self.deleteAllWidgets()

    if (self.iTargetPlayer != -1):
      screen = self.getScreen()

    return 0

  # returns a unique ID for a widget in this screen
  def getNextWidgetName(self):
    szName = self.WIDGET_ID + str(self.nWidgetCount)
    self.nWidgetCount += 1
    return szName

  def deleteAllWidgets(self):
    screen = self.getScreen()
    i = self.nWidgetCount - 1
    while (i >= 0):
      self.nWidgetCount = i
      screen.deleteWidget(self.getNextWidgetName())
      i -= 1

    self.nWidgetCount = 0

  # Will handle the input for this screen...
  def handleInput (self, inputClass):
    screen = self.getScreen()
    return 0

  def update(self, fDelta):
    return
