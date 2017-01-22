## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import PyHelpers
import CvUtil
import ScreenInput
import CvScreenEnums

PyPlayer = PyHelpers.PyPlayer

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()

##johny smith start##
class CvReligionScreen:
  "Religion Advisor Screen"

  def __init__(self):

    self.SCREEN_NAME = "ReligionScreen"
    self.BUTTON_NAME = "ReligionScreenButton"
    self.TITLE_TOP_PANEL = "ReligionsTopPanel"
    self.TITLE_BOTTOM_PANEL = "ReligionsBottomPanel"
    self.AREA_NAME = "ReligionsScreenArea"
    self.HELP_IMAGE_NAME = "CivicsScreenCivicOptionImage"
    self.RELIGION_NAME = "ReligionText"
    self.CONVERT_NAME = "ReligionConvertButton"
    self.CANCEL_NAME = "ReligionCancelButton"
    self.CITY_NAME = "ReligionCity"
    self.HEADER_NAME = "ReligionScreenHeader"
    self.DEBUG_DROPDOWN_ID =  "ReligionDropdownWidget"
    self.AREA1_ID =  "ReligionAreaWidget1"
    self.AREA2_ID =  "ReligionAreaWidget2"
    self.BACKGROUND_ID = "ReligionBackground"
    self.RELIGION_PANEL_ID = "ReligionPanel"
    self.RELIGION_ANARCHY_WIDGET = "ReligionAnarchyWidget"

    self.HEADINGS_TOP = 0
    self.HEADINGS_BOTTOM = 220
    self.HEADINGS_LEFT = 0
    self.HEADINGS_RIGHT = 320
    self.HELP_TOP = 20
    self.HELP_BOTTOM = 610
    self.HELP_LEFT = 350
    self.HELP_RIGHT = 950
    self.BUTTON_SIZE = 48
    self.BIG_BUTTON_SIZE = 64
    self.BOTTOM_LINE_TOP = 630
    self.BOTTOM_LINE_HEIGHT = 60
    self.TEXT_MARGIN = 13

    self.BORDER_WIDTH = 2
    self.HIGHLIGHT_EXTRA_SIZE = 4

    self.Z_SCREEN = -6.1

    self.Y_TITLE = 8
    self.Z_TEXT = 0 ##self.Z_SCREEN - 0.2
    self.DZ = -0.2
    self.Z_CONTROLS = self.Z_TEXT

  def setValues(self):
    screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
    resolutionWidth = 1024
    resolutionHeigth = 768

## johny smith
## this sets the resoultion below
#   if (resolutionWidth >= 1440):
#     self.HEADINGS_WIDTH = 204 # original = 199
#     self.X_SCREEN = 718   # original = 500
#     self.X_CANCEL = 717   # original = 552

#   elif (resolutionWidth >= 1280):
#     self.W_SCREEN = 1280
#     self.HEADINGS_WIDTH = 182
#     self.X_SCREEN = 638
#     self.X_CANCEL = 637

#   elif (resolutionWidth >= 1152):
#     self.W_SCREEN = 1152
#     self.HEADINGS_WIDTH = 164
#     self.X_SCREEN = 574
#     self.X_CANCEL = 573

#   elif (resolutionWidth >= 1024):
#     self.W_SCREEN = 1024
#     self.HEADINGS_WIDTH = 146
#     self.X_SCREEN = 510
#     self.X_CANCEL = 509

    self.W_SCREEN = resolutionWidth
    self.H_SCREEN = resolutionHeigth

    self.X_CANCEL = 20
    self.X_POSITION = 0
    self.Y_POSITION = 0
    self.PANEL_HEIGHT = 55
    self.PANEL_WIDTH = 0
    self.INITIAL_SPACING = 30
    self.HEADINGS_WIDTH = 340
    self.HEADINGS_HEIGHT = 64
    self.BOTTOM_LINE_HEIGHT = 60
    self.RIGHT_LINE_WIDTH = 0
    self.SCROLL_BAR_SPACING = 40
    self.BOTTOM_LINE_TEXT_SPACING = 150

    self.X_EXIT = self.W_SCREEN - 30
    self.Y_EXIT = self.H_SCREEN - 40

    self.X_CANCEL = 552
    self.X_SCREEN = self.W_SCREEN / 2
    self.Y_SCREEN = 396
    self.Y_CANCEL = self.H_SCREEN - 40
    self.Y_EXIT = self.H_SCREEN - 40
    self.HELP_BOTTOM = self.H_SCREEN - 2 * self.PANEL_HEIGHT - self.BOTTOM_LINE_HEIGHT

    self.BOTTOM_LINE_WIDTH = self.W_SCREEN
    self.BOTTOM_LINE_TOP = self.H_SCREEN - self.PANEL_HEIGHT - 70
    self.X_EXIT = self.W_SCREEN - 30
    self.X_ANARCHY = 21
    self.Y_ANARCHY = 726

    self.LEFT_EDGE_TEXT = 10
    self.X_RELIGION_START = 154
    self.Y_RELIGION_START = 154
    self.DX_RELIGION = 116
    self.DY_RELIGION = 116
    self.DX_RELIGION_OFFSET = self.DX_RELIGION
    self.X_RELIGION = 0
    self.Y_RELIGION = 35
    self.Y_FOUNDED = 90
    self.Y_HOLY_CITY = 115
    self.Y_INFLUENCE = 140
    self.Y_RELIGION_NAME = 70
    self.X_RELIGION_DIFF = self.X_RELIGION_START - self.X_RELIGION
    self.X_RELIGION_AREA = 0
    self.Y_RELIGION_AREA = 0
    self.W_RELIGION_AREA = 1008 + self.BUTTON_SIZE
    self.H_RELIGION_AREA = 180

    self.X_CITY1_AREA = 45
    self.X_CITY2_AREA = 522
    self.Y_CITY_AREA = 250
    self.W_CITY_AREA = 457
    self.H_CITY_AREA = 460

    self.X_CITY = 10
    self.DY_CITY = 38

    self.iReligionExamined = -1
    self.iReligionSelected = -1
    self.iReligionOriginal = -1
    self.iActivePlayer = -1

    self.bScreenUp = False

    self.ReligionScreenInputMap = {
      self.RELIGION_NAME    : self.ReligionScreenButton,
      self.BUTTON_NAME    : self.ReligionScreenButton,
      self.CONVERT_NAME   : self.ReligionConvert,
      self.CANCEL_NAME    : self.ReligionCancel,
      }

  def getScreen(self):
    return CyGInterfaceScreen(self.SCREEN_NAME, CvScreenEnums.RELIGION_SCREEN)

  def setActivePlayer(self, iPlayer):

    self.iActivePlayer = iPlayer
    activePlayer = gc.getPlayer(iPlayer)

    self.m_paeCurrentReligions = []
    self.m_paeDisplayReligions = []
    self.m_paeOriginalReligions = []
    for i in range (gc.getNumReligionInfos()):
      self.m_paeCurrentReligions.append(activePlayer.getReligions(i));
      self.m_paeDisplayReligions.append(activePlayer.getReligions(i));
      self.m_paeOriginalReligions.append(activePlayer.getReligions(i));

  def interfaceScreen (self):

    # johny smith ScreenTweaks LINE:
    self.setValues()
    screen = self.getScreen()
    if screen.isActive():
      return
    screen.setRenderInterfaceOnly(True);
    screen.showScreen( PopupStates.POPUPSTATE_IMMEDIATE, False)
    screen.setDimensions(self.X_POSITION, self.Y_POSITION, self.W_SCREEN, self.H_SCREEN)
    screen.addDDSGFC(self.BACKGROUND_ID, ArtFileMgr.getInterfaceArtInfo("MAINMENU_SLIDESHOW_LOAD").getPath(), 0, 0, self.W_SCREEN, self.H_SCREEN, WidgetTypes.WIDGET_GENERAL, -1, -1 )

    ## Panels on the Top(name of screen) and bottom(Cancel, Exit, Revolution buttons)
    screen.addPanel( self.TITLE_TOP_PANEL, u"", u"", True, False, 0, 0, self.W_SCREEN, self.PANEL_HEIGHT, PanelStyles.PANEL_STYLE_TOPBAR )
    screen.addPanel( self.TITLE_BOTTOM_PANEL, u"", u"", True, False, 0, self.H_SCREEN - self.PANEL_HEIGHT, self.W_SCREEN, self.PANEL_HEIGHT, PanelStyles.PANEL_STYLE_BOTTOMBAR )
    screen.addPanel(self.RELIGION_PANEL_ID, "", "", False, True, -10, 50, self.W_SCREEN + 20, self.H_RELIGION_AREA, PanelStyles.PANEL_STYLE_MAIN)
    screen.showWindowBackground(False)

    # Set the background and exit button, and show the screen
    screen.setDimensions(screen.centerX(0), screen.centerY(0), self.W_SCREEN, self.H_SCREEN)

    self.SCREEN_ART = ArtFileMgr.getInterfaceArtInfo("TECH_BG").getPath()
    self.NO_STATE_BUTTON_ART = ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").getPath()
    self.EXIT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() + "</font>"
    self.CONVERT_TEXT = u"<font=4>" + localText.getText("TXT_KEY_RELIGION_CONVERT", ()).upper() + "</font>"
    self.CANCEL_TEXT = u"<font=4>" + localText.getText("TXT_KEY_SCREEN_CANCEL", ()).upper() + "</font>"
    screen.setText(self.CANCEL_NAME, "Background", self.CANCEL_TEXT, CvUtil.FONT_CENTER_JUSTIFY, self.X_CANCEL, self.Y_CANCEL, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0)

    self.iActivePlayer = gc.getGame().getActivePlayer()

    self.bScreenUp = True

    screen.showWindowBackground(False)

    # Make the scrollable areas for the city list...

    if (CyGame().isDebugMode()):
      self.szDropdownName = self.DEBUG_DROPDOWN_ID
      screen.addDropDownBoxGFC(self.szDropdownName, 22, 12, 300, WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
      for j in range(gc.getMAX_PLAYERS()):
        if (gc.getPlayer(j).isAlive()):
          screen.addPullDownString(self.szDropdownName, gc.getPlayer(j).getName(), j, j, False )

    # Make the scrollable area for the civics list...
    screen.addScrollPanel( "CivicList", u"", self.PANEL_WIDTH/8 * 7, self.PANEL_HEIGHT/8 * 7, self.W_SCREEN, self.Y_RELIGION_AREA + self.H_RELIGION_AREA + 5, PanelStyles.PANEL_STYLE_EXTERNAL )
    screen.setActivation( "CivicList", ActivationTypes.ACTIVATE_NORMAL )

    # Draw Religion info
    self.drawReligionInfo()

    self.drawHelpInfo()

    self.drawCityInfo(self.iReligionSelected)

  # Draws the Religion buttons and information
  def drawReligionInfo(self):

    for i in range(gc.getNumReligionInfos()):

      screen = self.getScreen()

      ## johny smith
      ## This draws the symbols
      ## Puts the symbols in a loop
      ## Attachs the symbols so they will scroll
      xLoop = self.X_RELIGION_START
      for i in range(gc.getNumReligionInfos()):
        if gc.getGame().getReligionGameTurnFounded(i) >= 0:
          screen.addCheckBoxGFCAt("CivicList", self.getReligionButtonName(i), gc.getReligionInfo(i).getButton(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_RELIGION_AREA + xLoop - 25, self.Y_RELIGION_AREA + 10, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)
          #else:
          #szHelpImageID = self.HELP_IMAGE_NAME + str(i)
          #screen.setImageButtonAt(szHelpImageID, "CivicList", gc.getReligionInfo(i).getButtonDisabled(), self.X_RELIGION_AREA + xLoop - 25, self.Y_RELIGION_AREA + 10, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1,)
          szName = self.getReligionTextName(i)
          szLabel = gc.getReligionInfo(i).getDescription()
          #if (self.iReligionSelected == i):
          #szLabel = localText.changeTextColor(szLabel, gc.getInfoTypeForString("COLOR_YELLOW"))
          screen.setLabelAt(szName, "CivicList", szLabel, CvUtil.FONT_CENTER_JUSTIFY, self.X_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
          xLoop += self.DX_RELIGION

      szButtonName = self.getReligionButtonName(gc.getNumReligionInfos())
      screen.addCheckBoxGFCAt("CivicList", szButtonName, self.NO_STATE_BUTTON_ART, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), self.X_RELIGION_AREA + xLoop - 25, self.Y_RELIGION_AREA + 10, self.BUTTON_SIZE, self.BUTTON_SIZE, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_LABEL, False)


      szName = self.getReligionTextName(gc.getNumReligionInfos())
      szLabel = localText.getText("TXT_KEY_RELIGION_SCREEN_NO_STATE", ())
#     if (self.iReligionSelected == gc.getNumReligionInfos()):
#       szLabel = localText.changeTextColor(szLabel, gc.getInfoTypeForString("COLOR_YELLOW"))
      screen.setLabelAt(szName, "CivicList", szLabel, CvUtil.FONT_CENTER_JUSTIFY,  self.X_RELIGION_AREA + xLoop, self.Y_RELIGION_NAME, self.DZ, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)


    self.iReligionSelected = gc.getPlayer(self.iActivePlayer).getStateReligion()
    if (self.iReligionSelected == -1):
      self.iReligionSelected = gc.getNumReligionInfos()
    self.iReligionExamined = self.iReligionSelected
    self.iReligionOriginal = self.iReligionSelected


  def drawHelpInfo(self):

    screen = self.getScreen()

    ## johny smith
    ## This attaches the text to the panel
    ## This is for every line of font
    # Founded...
    screen.setLabelAt("", "CivicList", localText.getText("TXT_KEY_RELIGION_SCREEN_DATE_FOUNDED", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    # Date Founded:
    xLoop = self.X_RELIGION_START
    for i in range(gc.getNumReligionInfos()):
      if gc.getGame().getReligionGameTurnFounded(i) >= 0:
        szFounded = CyGameTextMgr().getTimeStr(gc.getGame().getReligionGameTurnFounded(i), false)
        screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, self.X_RELIGION_AREA + xLoop, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        xLoop += self.DX_RELIGION

    screen.setLabelAt("", "CivicList", "", CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_FOUNDED, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    # Holy City...
    screen.setLabelAt("", "CivicList", localText.getText("TXT_KEY_RELIGION_SCREEN_HOLY_CITY", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    xLoop = self.X_RELIGION_START
    for i in range(gc.getNumReligionInfos()):
      pHolyCity = gc.getGame().getHolyCity(i)
      if gc.getGame().getReligionGameTurnFounded(i) >= 0:
                                if not pHolyCity.isRevealed(gc.getPlayer(self.iActivePlayer).getTeam(), False):
                                        szFounded = localText.getText("TXT_KEY_UNKNOWN", ())
                                        screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                                        xLoop += self.DX_RELIGION
                                else:
                                        szFounded = pHolyCity.getName()
                                        screen.setLabelAt("", "CivicList", "(%s)" % gc.getPlayer(pHolyCity.getOwner()).getCivilizationAdjective(0), CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY+8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                                        screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY-8, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
                                        xLoop += self.DX_RELIGION

    szFounded = "-"
    screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_HOLY_CITY, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    # Influence...
    screen.setLabelAt("", "CivicList", localText.getText("TXT_KEY_RELIGION_SCREEN_INFLUENCE", ()), CvUtil.FONT_LEFT_JUSTIFY, self.LEFT_EDGE_TEXT, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    xLoop = self.X_RELIGION_START
    for i in range(gc.getNumReligionInfos()):
      if gc.getGame().getReligionGameTurnFounded(i) >= 0:
        szFounded = str(gc.getGame().calculateReligionPercent(i)) + "%"
        screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        xLoop += self.DX_RELIGION

    szFounded = "-"
    screen.setLabelAt("", "CivicList", szFounded, CvUtil.FONT_CENTER_JUSTIFY, xLoop, self.Y_INFLUENCE, self.DZ, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

    self.iReligionSelected = gc.getPlayer(self.iActivePlayer).getStateReligion()
    if (self.iReligionSelected == -1):
      self.iReligionSelected = gc.getNumReligionInfos()
    self.iReligionExamined = self.iReligionSelected
    self.iReligionOriginal = self.iReligionSelected

##johny smith end##
  # Draws the city list
  def drawCityInfo(self, iReligion):

    if (not self.bScreenUp):
      return

    screen = self.getScreen()

    if (iReligion == gc.getNumReligionInfos()):
      iLinkReligion = -1
    else:
      iLinkReligion = iReligion

    szArea1 = self.AREA1_ID
    screen.addPanel(self.AREA1_ID, "", "", True, True, self.X_CITY1_AREA, self.Y_CITY_AREA, self.W_CITY_AREA, self.H_CITY_AREA, PanelStyles.PANEL_STYLE_MAIN)

    szArea2 = self.AREA2_ID
    screen.addPanel(self.AREA2_ID, "", "", True, True, self.X_CITY2_AREA, self.Y_CITY_AREA, self.W_CITY_AREA, self.H_CITY_AREA, PanelStyles.PANEL_STYLE_MAIN)


    szArea = self.RELIGION_PANEL_ID
    for i in range(gc.getNumReligionInfos()):
      if (self.iReligionSelected == i):
        screen.setState(self.getReligionButtonName(i), True)
      else:
        screen.setState(self.getReligionButtonName(i), False)

    if (self.iReligionSelected == gc.getNumReligionInfos()):
      screen.setState(self.getReligionButtonName(gc.getNumReligionInfos()), True)
    else:
      screen.setState(self.getReligionButtonName(gc.getNumReligionInfos()), False)

    iPlayer = PyPlayer(self.iActivePlayer)

    cityList = iPlayer.getCityList()

    # Loop through the cities
    szLeftCities = u""
    szRightCities = u""
    for i in range(len(cityList)):

      bFirstColumn = (i % 2 == 0)

      pLoopCity = cityList[i]

      # Constructing the City name...
      szCityName = u""
      if pLoopCity.isCapital():
        szCityName += u"%c" % CyGame().getSymbolID(FontSymbols.STAR_CHAR)

      lHolyCity = pLoopCity.getHolyCity()
      if lHolyCity:
        for iI in range(len(lHolyCity)):
          szCityName += u"%c" %(gc.getReligionInfo(lHolyCity[iI]).getHolyCityChar())

      lReligions = pLoopCity.getReligions()
      if lReligions:
        for iI in range(len(lReligions)):
          if lReligions[iI] not in lHolyCity:
            szCityName += u"%c" %(gc.getReligionInfo(lReligions[iI]).getChar())

      szCityName += pLoopCity.getName()[0:17] + "  "

      if (iLinkReligion == -1):
        bFirst = True
        for iI in range(len(lReligions)):
          szTempBuffer = CyGameTextMgr().getReligionHelpCity(lReligions[iI], pLoopCity.GetCy(), False, False, False, True)
          if (szTempBuffer):
            if (not bFirst):
              szCityName += u", "
            szCityName += szTempBuffer
            bFirst = False
      else:
        szCityName += CyGameTextMgr().getReligionHelpCity(iLinkReligion, pLoopCity.GetCy(), False, False, True, False)

      if bFirstColumn:
        szLeftCities += u"<font=3>" + szCityName + u"</font>\n"
      else:
        szRightCities += u"<font=3>" + szCityName + u"</font>\n"

    screen.addMultilineText("Child" + self.AREA1_ID, szLeftCities, self.X_CITY1_AREA+5, self.Y_CITY_AREA+5, self.W_CITY_AREA-10, self.H_CITY_AREA-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)
    screen.addMultilineText("Child" + self.AREA2_ID, szRightCities, self.X_CITY2_AREA+5, self.Y_CITY_AREA+5, self.W_CITY_AREA-10, self.H_CITY_AREA-10, WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

    # Convert Button....
    iLink = 0
    if (gc.getPlayer(self.iActivePlayer).canChangeReligion()):
      iLink = 1

    if (not self.canConvert(iLinkReligion) or iLinkReligion == self.iReligionOriginal):
      screen.setText(self.CONVERT_NAME, "Background", self.EXIT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_GENERAL, 1, 0)
      screen.hide(self.CANCEL_NAME)
      szAnarchyTime = CyGameTextMgr().setConvertHelp(self.iActivePlayer, iLinkReligion)
    else:
      screen.setText(self.CONVERT_NAME, "Background", self.CONVERT_TEXT, CvUtil.FONT_RIGHT_JUSTIFY, self.X_EXIT, self.Y_EXIT, self.Z_TEXT, FontTypes.TITLE_FONT, WidgetTypes.WIDGET_CONVERT, iLinkReligion, 1)
      screen.show(self.CANCEL_NAME)
      szAnarchyTime = localText.getText("TXT_KEY_ANARCHY_TURNS", (gc.getPlayer(self.iActivePlayer).getReligionAnarchyLength(), ))

    # Turns of Anarchy Text...
    screen.setLabel(self.RELIGION_ANARCHY_WIDGET, "Background", u"<font=3>" + szAnarchyTime + u"</font>", CvUtil.FONT_LEFT_JUSTIFY, self.X_ANARCHY, self.Y_ANARCHY, self.Z_TEXT, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

  def getReligionButtonName(self, iReligion):
    szName = self.BUTTON_NAME + str(iReligion)
    return szName

  def getReligionTextName(self, iReligion):
    szName = self.RELIGION_NAME + str(iReligion)
    return szName

  def canConvert(self, iReligion):
    iCurrentReligion = gc.getPlayer(self.iActivePlayer).getStateReligion()
    if (iReligion == gc.getNumReligionInfos()):
      iConvertReligion = -1
    else:
      iConvertReligion = iReligion

    return (iConvertReligion != iCurrentReligion and gc.getPlayer(self.iActivePlayer).canConvert(iConvertReligion))

  # Will handle the input for this screen...
  def handleInput (self, inputClass):
    if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_LISTBOX_ITEM_SELECTED):
      screen = self.getScreen()
      iIndex = screen.getSelectedPullDownID(self.DEBUG_DROPDOWN_ID)
      self.iActivePlayer = screen.getPullDownData(self.DEBUG_DROPDOWN_ID, iIndex)
      self.drawReligionInfo()
      self.drawCityInfo(self.iReligionSelected)
      return 1
    elif (self.ReligionScreenInputMap.has_key(inputClass.getFunctionName())):
      'Calls function mapped in ReligionScreenInputMap'
      # only get from the map if it has the key

      # get bound function from map and call it
      self.ReligionScreenInputMap.get(inputClass.getFunctionName())(inputClass)
      return 1
    return 0

  def update(self, fDelta):
    return

  # Religion Button
  def ReligionScreenButton( self, inputClass ):
    if ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED ) :
      if (inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0) :
        self.iReligionSelected = inputClass.getID()
        self.iReligionExamined = self.iReligionSelected
        self.drawCityInfo(self.iReligionSelected)
    elif ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_ON ) :
      if ( inputClass.getID() == gc.getNumReligionInfos() or gc.getGame().getReligionGameTurnFounded(inputClass.getID()) >= 0) :
        self.iReligionExamined = inputClass.getID()
        self.drawCityInfo(self.iReligionExamined)
    elif ( inputClass.getNotifyCode() == NotifyCode.NOTIFY_CURSOR_MOVE_OFF ) :
      self.iReligionExamined = self.iReligionSelected
      self.drawCityInfo(self.iReligionSelected)
    return 0

  def ReligionConvert(self, inputClass):
    screen = self.getScreen()
    if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
      screen.hideScreen()

  def ReligionCancel(self, inputClass):
    screen = self.getScreen()
    if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED) :
      self.iReligionSelected = self.iReligionOriginal
      if (-1 == self.iReligionSelected):
        self.iReligionSelected = gc.getNumReligionInfos()
      self.drawCityInfo(self.iReligionSelected)




