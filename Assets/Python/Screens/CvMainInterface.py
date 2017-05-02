## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
## Edited by Pie, Austria
from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import CvEventInterface
import time
import PyHelpers

import PAE_Trade
import PAE_Unit

# globals
gc = CyGlobalContext()
ArtFileMgr = CyArtFileMgr()
localText = CyTranslator()
PyInfo = PyHelpers.PyInfo

g_NumEmphasizeInfos = 0
g_NumCityTabTypes = 0
g_NumHurryInfos = 0
g_NumUnitClassInfos = 0
g_NumBuildingClassInfos = 0
g_NumProjectInfos = 0
g_NumProcessInfos = 0
g_NumActionInfos = 0
g_eEndTurnButtonState = -1

MAX_SELECTED_TEXT = 5
MAX_DISPLAYABLE_BUILDINGS = 15
MAX_DISPLAYABLE_TRADE_ROUTES = 4
MAX_BONUS_ROWS = 10

# BUG - field of view slider - start
DEFAULT_FIELD_OF_VIEW = 44
bFieldOfView = False # PAE (False for better ingame python programming)
# BUG - field of view slider - end

# SPECIALIST STACKER        05/02/07      JOHNY
MAX_CITIZEN_BUTTONS = 20

# <STACKER START>
# Modify this if you want to change the distance between the stacked specialists.
# Default value is 9
SPECIALIST_STACK_WIDTH = 9

# Set this to False if you don't want to have the yellow highlight displayed when
# citizens are forced to be specialized. Default value is True
g_bHighlightForcedSpecialists = True

# Set this to True if you want to stack the super specialists. Default value is False
g_bStackSuperSpecialists = True

# Change this if you want to display a different number of super specialists when
# g_bStackSuperSpecialists is set to False. Default value is 6
MAX_SUPER_SPECIALIST_BUTTONS = 6

# Modify this if you want to change the distance between the stacked super specialists
# Default value is 15
SUPER_SPECIALIST_STACK_WIDTH = 15

# Set this to False if you want to show every super specialist in the city. This
# feature will only work if g_bStackSuperSpecialists is set to True and works best of
# you have set g_bDynamicSuperSpecialistsSpacing to True. Default value is True.
g_bDisplayUniqueSuperSpecialistsOnly = False

# If this is set to True then the SUPER_SPECIALIST_STACK_WIDTH set value will not
# be used. Default value is True
g_bDynamicSuperSpecialistsSpacing = True

# Set this to True if you want to stack the angry citizens. Default value is False
g_bStackAngryCitizens = False

# Change this if you want to display a different number of angry citizens when
# g_bStackAngryCitizens is set to False. Default value is 6
MAX_ANGRY_CITIZEN_BUTTONS = 6

# Modify this if you want to change the distance between the stacked angry citizens.
# Default value is 15
ANGRY_CITIZEN_STACK_WIDTH = 15

# If this is set to True then the ANGRY_CITIZEN_STACK_WIDTH set value will not
# be used. Default value is True
g_bDynamicAngryCitizensSpacing = True

# Do not edit g_SuperSpecialistCount or g_iAngryCitizensCount, otherwise really bad
# things could happen.
g_iSuperSpecialistCount = 0
g_iAngryCitizensCount = 0

# SPECIALIST STACKER        END

SELECTION_BUTTON_COLUMNS = 8
SELECTION_BUTTON_ROWS = 2
NUM_SELECTION_BUTTONS = SELECTION_BUTTON_ROWS * SELECTION_BUTTON_COLUMNS

g_iNumBuildingWidgets = MAX_DISPLAYABLE_BUILDINGS
g_iNumTradeRouteWidgets = MAX_DISPLAYABLE_TRADE_ROUTES

# END OF TURN BUTTON POSITIONS
######################
iEndOfTurnButtonSize = 32
iEndOfTurnPosX = 296 # distance from right
iEndOfTurnPosY = 147 # distance from bottom

# MINIMAP BUTTON POSITIONS
######################
iMinimapButtonsExtent = 228
iMinimapButtonsX = 227
iMinimapButtonsY_Regular = 160
iMinimapButtonsY_Minimal = 32
iMinimapButtonWidth = 24
iMinimapButtonHeight = 24

# Globe button
iGlobeButtonX = 48
iGlobeButtonY_Regular = 168
iGlobeButtonY_Minimal = 40
iGlobeToggleWidth = 48
iGlobeToggleHeight = 48

# GLOBE LAYER OPTION POSITIONING
######################
iGlobeLayerOptionsX  = 235
iGlobeLayerOptionsY_Regular  = 170 # distance from bottom edge
iGlobeLayerOptionsY_Minimal  = 38  # distance from bottom edge
iGlobeLayerOptionsWidth = 400
iGlobeLayerOptionHeight = 24

# STACK BAR
#####################
iStackBarHeight = 27


# MULTI LIST
#####################
iMultiListXL = 318
iMultiListXR = 332


# TOP CENTER TITLE
#####################
iCityCenterRow1X = 398
iCityCenterRow1Y = 78
iCityCenterRow2X = 398
iCityCenterRow2Y = 104

iCityCenterRow1Xa = 347
iCityCenterRow2Xa = 482


g_iNumTradeRoutes = 0
g_iNumBuildings = 0
g_iNumLeftBonus = 0
g_iNumCenterBonus = 0
g_iNumRightBonus = 0

g_szTimeText = ""
g_iTimeTextCounter = 0

g_pSelectedUnit = 0

m_iNumPlotListButtons = 0


class CvMainInterface:
  "Main Interface Screen"

  def __init__(self):
# Platy ScoreBoard adapted and changed by Pie
    self.iScoreRows = 0
    self.iScoreWidth = 150
    self.iScoreHidePoints = False # PAE
# Platy ScoreBoard end
# BUG - field of view slider - start
    self.szSliderTextId = "FieldOfViewSliderText"
    self.sFieldOfView_Text = ""
    self.szSliderId = "FieldOfViewSlider"
    self.iField_View_Prev = -1
# BUG - field of view slider - end

# Ramk - City Widgets
    self.buildWidges = [
        WidgetTypes.WIDGET_TRAIN,
        WidgetTypes.WIDGET_CONSTRUCT,
        WidgetTypes.WIDGET_CREATE,
        WidgetTypes.WIDGET_MAINTAIN
    ]

  def numPlotListButtons(self):
    return self.m_iNumPlotListButtons

  def initState (self, screen=None):
    if screen is None:
       screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    self.xResolution = screen.getXResolution()
    self.yResolution = screen.getYResolution()
# BUG - field of view slider - start
    iBtnY = 27
    self.iX_FoVSlider = self.xResolution - 120
    self.iY_FoVSlider = iBtnY + 30
    self.sFieldOfView_Text = localText.getText("TXT_KEY_MAININTERFACE_FIELDOFVIEW_TEXT", ())
    self.iField_View = DEFAULT_FIELD_OF_VIEW
# BUG - field of view slider - end

  def interfaceScreen (self):

    # Global variables being set here
    global g_NumEmphasizeInfos
    global g_NumCityTabTypes
    global g_NumHurryInfos
    global g_NumUnitClassInfos
    global g_NumBuildingClassInfos
    global g_NumProjectInfos
    global g_NumProcessInfos
    global g_NumActionInfos

    global MAX_SELECTED_TEXT
    global MAX_DISPLAYABLE_BUILDINGS
    global MAX_DISPLAYABLE_TRADE_ROUTES
    global MAX_BONUS_ROWS
    global MAX_CITIZEN_BUTTONS

    # SPECIALIST STACKER        05/02/07      JOHNY
    global g_iSuperSpecialistCount
    global g_iAngryCitizensCount

    global SPECIALIST_STACK_WIDTH
    global g_bHighlightForcedSpecialists
    global g_bStackSuperSpecialists
    global MAX_SUPER_SPECIALIST_BUTTONS
    global SUPER_SPECIALIST_STACK_WIDTH
    global g_bDisplayUniqueSuperSpecialistsOnly
    global g_bDynamicSuperSpecialistsSpacing
    global g_bStackAngryCitizens
    global MAX_ANGRY_CITIZEN_BUTTONS
    global ANGRY_CITIZEN_STACK_WIDTH
    global g_bDynamicAngryCitizensSpacing

    # SPECIALIST STACKER        END

    # BUG - field of view
    # This is the main interface screen, create it as such
    screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
    self.initState(screen)
    screen.setForcedRedraw(True)
    screen.setDimensions(0, 0, self.xResolution, self.yResolution)

    # to avoid changing all the code below
    xResolution = self.xResolution
    yResolution = self.yResolution
    # BUG - field of view end

    if ( CyGame().isPitbossHost() ):
      return

    # This is the main interface screen, create it as such
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    screen.setForcedRedraw(True)

    # Find out our resolution
    self.m_iNumPlotListButtons = (xResolution - (iMultiListXL+iMultiListXR) - 68) / 34
    self.m_iNumMenuButtons = (xResolution - (iMultiListXL+iMultiListXR) - 18) / 50 # PAE, Ramk 34=>50

    # To decide if mouse clicked on first or second row of the menu.
    self.secondRowBorder  = yResolution-113+50
    self.ySecondRow = 0

    screen.setDimensions(0, 0, xResolution, yResolution)

    # Set up our global variables...
    g_NumEmphasizeInfos = gc.getNumEmphasizeInfos()
    g_NumCityTabTypes = CityTabTypes.NUM_CITYTAB_TYPES
    g_NumHurryInfos = gc.getNumHurryInfos()
    g_NumUnitClassInfos = gc.getNumUnitClassInfos()
    g_NumBuildingClassInfos = gc.getNumBuildingClassInfos()
    g_NumProjectInfos = gc.getNumProjectInfos()
    g_NumProcessInfos = gc.getNumProcessInfos()
    g_NumActionInfos = gc.getNumActionInfos()

    # Help Text Area
    screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 172, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )

    # Center Left
    screen.addPanel( "InterfaceCenterLeftBackgroundWidget", u"", u"", True, False, 0, 0, 258, yResolution-149, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "InterfaceCenterLeftBackgroundWidget", "Panel_City_Left_Style" )
    screen.hide( "InterfaceCenterLeftBackgroundWidget" )

    # Top Left
    screen.addPanel( "InterfaceTopLeftBackgroundWidget", u"", u"", True, False, 258, 0, xResolution - 516, yResolution-149, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "InterfaceTopLeftBackgroundWidget", "Panel_City_Top_Style" )
    screen.hide( "InterfaceTopLeftBackgroundWidget" )

    # Center Right
    screen.addPanel( "InterfaceCenterRightBackgroundWidget", u"", u"", True, False, xResolution - 258, 0, 258, yResolution-149, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "InterfaceCenterRightBackgroundWidget", "Panel_City_Right_Style" )
    screen.hide( "InterfaceCenterRightBackgroundWidget" )

    screen.addPanel( "CityScreenAdjustPanel", u"", u"", True, False, 10, 44, 238, 105, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "CityScreenAdjustPanel", "Panel_City_Info_Style" )
    screen.hide( "CityScreenAdjustPanel" )

    screen.addPanel( "TopCityPanelLeft", u"", u"", True, False, 260, 70, xResolution/2-260, 60, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "TopCityPanelLeft", "Panel_City_TanTL_Style" )
    screen.hide( "TopCityPanelLeft" )

    screen.addPanel( "TopCityPanelRight", u"", u"", True, False, xResolution/2, 70, xResolution/2-260, 60, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "TopCityPanelRight", "Panel_City_TanTR_Style" )
    screen.hide( "TopCityPanelRight" )

    # Top Bar

    # SF CHANGE
    screen.addPanel( "CityScreenTopWidget", u"", u"", True, False, 0, -2, xResolution, 41, PanelStyles.PANEL_STYLE_STANDARD )

    screen.setStyle( "CityScreenTopWidget", "Panel_TopBar_Style" )
    screen.hide( "CityScreenTopWidget" )

    # Top Center Title
    screen.addPanel( "CityNameBackground", u"", u"", True, False, 260, 31, xResolution - (260*2), 38, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "CityNameBackground", "Panel_City_Title_Style" )
    screen.hide( "CityNameBackground" )

    # Left Background Widget
    screen.addDDSGFC( "InterfaceLeftBackgroundWidget", ArtFileMgr.getInterfaceArtInfo("INTERFACE_BOTTOM_LEFT").getPath(), 0, yResolution - 164, 304, 164, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "InterfaceLeftBackgroundWidget" )

    # Center Background Widget
    screen.addPanel( "InterfaceCenterBackgroundWidget", u"", u"", True, False, 296, yResolution - 133, xResolution - (296*2), 133, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceCenterBackgroundWidget", "Panel_Game_HudBC_Style" )
    screen.hide( "InterfaceCenterBackgroundWidget" )

    # Left Background Widget
    screen.addPanel( "InterfaceLeftBackgroundWidget", u"", u"", True, False, 0, yResolution - 168, 304, 168, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceLeftBackgroundWidget", "Panel_Game_HudBL_Style" )
    screen.hide( "InterfaceLeftBackgroundWidget" )

    # Right Background Widget
    screen.addPanel( "InterfaceRightBackgroundWidget", u"", u"", True, False, xResolution - 304, yResolution - 168, 304, 168, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceRightBackgroundWidget", "Panel_Game_HudBR_Style" )
    screen.hide( "InterfaceRightBackgroundWidget" )

    # Top Center Background
    screen.addPanel( "InterfaceTopCenter", u"", u"", True, False, 257, -2, xResolution-(257*2), 48, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceTopCenter", "Panel_Game_HudTC_Style" )
    screen.hide( "InterfaceTopCenter" )

    # Top Left Background
    screen.addPanel( "InterfaceTopLeft", u"", u"", True, False, 0, -2, 267, 60, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceTopLeft", "Panel_Game_HudTL_Style" )
    screen.hide( "InterfaceTopLeft" )

    # Top Right Background
    screen.addPanel( "InterfaceTopRight", u"", u"", True, False, xResolution - 267, -2, 267, 60, PanelStyles.PANEL_STYLE_STANDARD)
    screen.setStyle( "InterfaceTopRight", "Panel_Game_HudTR_Style" )
    screen.hide( "InterfaceTopRight" )

    iBtnWidth = 28
    iBtnAdvance = 28
    iBtnY = 27
    iBtnX = 37

    # Turn log Button
    screen.setImageButton( "TurnLogButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_TURN_LOG).getActionInfoIndex(), -1 )
    screen.setStyle( "TurnLogButton", "Button_HUDLog_Style" )
    screen.hide( "TurnLogButton" )

    iBtnX += iBtnAdvance + 20
    screen.setImageButton( "VictoryAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_VICTORY_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "VictoryAdvisorButton", "Button_HUDAdvisorVictory_Style" )
    screen.hide( "VictoryAdvisorButton" )

    iBtnX += iBtnAdvance + 5
    screen.setImageButton( "InfoAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_INFO).getActionInfoIndex(), -1 )
    screen.setStyle( "InfoAdvisorButton", "Button_HUDAdvisorRecord_Style" )
    screen.hide( "InfoAdvisorButton" )

    iBtnX += iBtnAdvance + 5
    screen.setImageButton( "EspionageAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_ESPIONAGE_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "EspionageAdvisorButton", "Button_HUDAdvisorEspionage_Style" )
    screen.hide( "EspionageAdvisorButton" )

    # PAE TradeRouteAdvisor
    iBtnX += iBtnAdvance + 5
    screen.setImageButton( "TradeRouteAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_GENERAL, 10000, 1 )
    # screen.setImageButton( "TradeRouteAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, -1, 1 )
    screen.setStyle( "TradeRouteAdvisorButton", "Button_HUDAdvisorTradeRoute_Style" )
    screen.hide( "TradeRouteAdvisorButton" )
    iBtnX += iBtnAdvance + 5
    screen.setImageButton( "TradeRouteAdvisorButton2", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_GENERAL, 10000, 2 )
    # screen.setImageButton( "TradeRouteAdvisorButton2", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, -1, 2 )
    screen.setStyle( "TradeRouteAdvisorButton2", "Button_HUDAdvisorTradeRoute2_Style" )
    screen.hide( "TradeRouteAdvisorButton2" )

    iBtnX = xResolution - 247

    # Advisor Buttons...
    screen.setImageButton( "DomesticAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_DOMESTIC_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "DomesticAdvisorButton", "Button_HUDAdvisorDomestic_Style" )
    screen.hide( "DomesticAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "FinanceAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_FINANCIAL_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "FinanceAdvisorButton", "Button_HUDAdvisorFinance_Style" )
    screen.hide( "FinanceAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "CivicsAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_CIVICS_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "CivicsAdvisorButton", "Button_HUDAdvisorCivics_Style" )
    screen.hide( "CivicsAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "ForeignAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_FOREIGN_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "ForeignAdvisorButton", "Button_HUDAdvisorForeign_Style" )
    screen.hide( "ForeignAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "MilitaryAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_MILITARY_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "MilitaryAdvisorButton", "Button_HUDAdvisorMilitary_Style" )
    screen.hide( "MilitaryAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "TechAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_TECH_CHOOSER).getActionInfoIndex(), -1 )
    screen.setStyle( "TechAdvisorButton", "Button_HUDAdvisorTechnology_Style" )
    screen.hide( "TechAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "ReligiousAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_RELIGION_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "ReligiousAdvisorButton", "Button_HUDAdvisorReligious_Style" )
    screen.hide( "ReligiousAdvisorButton" )

    iBtnX += iBtnAdvance
    screen.setImageButton( "CorporationAdvisorButton", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_CORPORATION_SCREEN).getActionInfoIndex(), -1 )
    screen.setStyle( "CorporationAdvisorButton", "Button_HUDAdvisorCorporation_Style" )
    screen.hide( "CorporationAdvisorButton" )

    # Field of View slider
    if bFieldOfView:
      self.setFieldofView_Text(screen)
      iW = 100
      iH = 15
      screen.addSlider(self.szSliderId, self.iX_FoVSlider + 5, self.iY_FoVSlider, iW, iH, self.iField_View - 1, 0, 99, WidgetTypes.WIDGET_GENERAL, -1, -1, False)
      screen.hide(self.szSliderTextId)
      screen.hide(self.szSliderId)

    # City Tabs
    self.cityTabsJumpmarks = [0,1,2]
    self.updateCityTabs(screen)
    screen.hide( "CityTab0" )
    screen.hide( "CityTab1" )
    screen.hide( "CityTab2" )

    # Minimap initialization
    screen.setMainInterface(True)

    screen.addPanel( "MiniMapPanel", u"", u"", True, False, xResolution - 214, yResolution - 151, 208, 151, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "MiniMapPanel", "Panel_Game_HudMap_Style" )
    screen.hide( "MiniMapPanel" )

    screen.initMinimap( xResolution - 210, xResolution - 9, yResolution - 131, yResolution - 9, -0.1 )
    gc.getMap().updateMinimapColor()

    self.createMinimapButtons()

    # Help button (always visible)
    screen.setImageButton( "InterfaceHelpButton", ArtFileMgr.getInterfaceArtInfo("INTERFACE_GENERAL_CIVILOPEDIA_ICON").getPath(), xResolution - 28, 2, 24, 24, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_CIVILOPEDIA).getActionInfoIndex(), -1 )
    screen.hide( "InterfaceHelpButton" )

    screen.setImageButton( "MainMenuButton", ArtFileMgr.getInterfaceArtInfo("INTERFACE_GENERAL_MENU_ICON").getPath(), xResolution - 54, 2, 24, 24, WidgetTypes.WIDGET_MENU_ICON, -1, -1 )
    screen.hide( "MainMenuButton" )

    # Globeview buttons
    self.createGlobeviewButtons( )

    screen.addMultiListControlGFC( "BottomButtonContainer", u"", iMultiListXL, yResolution - 113, xResolution - (iMultiListXL+iMultiListXR), 100, 4, 48, 48, TableStyles.TABLE_STYLE_STANDARD )
    screen.hide( "BottomButtonContainer" )

    # *********************************************************************************
    # PLOT LIST BUTTONS
    # *********************************************************************************

    for j in range(gc.getMAX_PLOT_LIST_ROWS()):
      yRow = (j - gc.getMAX_PLOT_LIST_ROWS() + 1) * 34
      yPixel = yResolution - 169 + yRow - 3
      xPixel = 315 - 3
      xWidth = self.numPlotListButtons() * 34 + 3
      yHeight = 32 + 3

      szStringPanel = "PlotListPanel" + str(j)
      screen.addPanel(szStringPanel, u"", u"", True, False, xPixel, yPixel, xWidth, yHeight, PanelStyles.PANEL_STYLE_EMPTY)

      for i in range(self.numPlotListButtons()):
        k = j*self.numPlotListButtons()+i

        xOffset = i * 34

        szString = "PlotListButton" + str(k)
        screen.addCheckBoxGFCAt(szStringPanel, szString, ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_GOVERNOR").getPath(), ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), xOffset + 3, 3, 32, 32, WidgetTypes.WIDGET_PLOT_LIST, k, -1, ButtonStyles.BUTTON_STYLE_LABEL, True )
        screen.hide( szString )

        szStringHealth = szString + "Health"
        screen.addStackedBarGFCAt( szStringHealth, szStringPanel, xOffset + 3, 26, 32, 11, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, k, -1 )
        screen.hide( szStringHealth )

        szStringIcon = szString + "Icon"
        szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_MOVE").getPath()
        screen.addDDSGFCAt( szStringIcon, szStringPanel, szFileName, xOffset, 0, 12, 12, WidgetTypes.WIDGET_PLOT_LIST, k, -1, False )
        screen.hide( szStringIcon )

        # PAE Extra Overlay for Leaders, Heroes and PromotionReadyUnits
        szStringIcon = szString + "Icon2"
        szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_MOVE").getPath()
        screen.addDDSGFCAt( szStringIcon, szStringPanel, szFileName, xOffset + 22, 0, 14, 14, WidgetTypes.WIDGET_PLOT_LIST, k, -1, False )
        screen.hide( szStringIcon )
        szStringIcon = szString + "Icon3"
        szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_MOVE").getPath()
        screen.addDDSGFCAt( szStringIcon, szStringPanel, szFileName, xOffset + 4, 16, 14, 14, WidgetTypes.WIDGET_PLOT_LIST, k, -1, False )
        screen.hide( szStringIcon )
        # ------------------

    # End Turn Text
    screen.setLabel( "EndTurnText", "Background", u"", CvUtil.FONT_CENTER_JUSTIFY, 0, yResolution - 188, -0.1, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.setHitTest( "EndTurnText", HitTestTypes.HITTEST_NOHIT )

    # Three states for end turn button...
    screen.setImageButton( "EndTurnButton", "", xResolution - (iEndOfTurnButtonSize/2) - iEndOfTurnPosX, yResolution - (iEndOfTurnButtonSize/2) - iEndOfTurnPosY, iEndOfTurnButtonSize, iEndOfTurnButtonSize, WidgetTypes.WIDGET_END_TURN, -1, -1 )
    screen.setStyle( "EndTurnButton", "Button_HUDEndTurn_Style" )
    screen.setEndTurnState( "EndTurnButton", "Red" )
    screen.hide( "EndTurnButton" )

    # *********************************************************************************
    # RESEARCH BUTTONS
    # *********************************************************************************

    i = 0
    for i in range( gc.getNumTechInfos() ):
      szName = "ResearchButton" + str(i)
      screen.setImageButton( szName, gc.getTechInfo(i).getButton(), 0, 0, 32, 32, WidgetTypes.WIDGET_RESEARCH, i, -1 )
      screen.hide( szName )

    i = 0
    for i in range(gc.getNumReligionInfos()):
      szName = "ReligionButton" + str(i)
      if gc.getGame().isOption(GameOptionTypes.GAMEOPTION_PICK_RELIGION):
        szButton = gc.getReligionInfo(i).getGenericTechButton()
      else:
        szButton = gc.getReligionInfo(i).getTechButton()
      screen.setImageButton( szName, szButton, 0, 0, 32, 32, WidgetTypes.WIDGET_RESEARCH, gc.getReligionInfo(i).getTechPrereq(), -1 )
      screen.hide( szName )

    # *********************************************************************************
    # CITIZEN BUTTONS
    # *********************************************************************************

    # SPECIALIST STACKER        05/02/07      JOHNY
    szHideCitizenList = []

    # Angry Citizens
    i = 0
    for i in range(MAX_ANGRY_CITIZEN_BUTTONS):
      szName = "AngryCitizen" + str(i)
      screen.setImageButton( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_ANGRYCITIZEN_TEXTURE").getPath(), xResolution - 74 - (34 * i), yResolution - 241, 30, 30, WidgetTypes.WIDGET_ANGRY_CITIZEN, -1, -1 )
      screen.hide( szName )
    g_iAngryCitizensCount = MAX_ANGRY_CITIZEN_BUTTONS

    iCount = 0

    # Increase Specialists...
    i = 0
    iXShiftVal = 0
    iYShiftVal = 0

    for i in range( gc.getNumSpecialistInfos() ):
      if( i > 5 ):
        iXShiftVal = 110
        iYShiftVal = (i % 5)-1
      else:
        iYShiftVal = i
      if (gc.getSpecialistInfo(i).isVisible()):
        szName = "IncreaseSpecialist" + str(i)
        screen.setButtonGFC( szName, u"", "", xResolution - (38+iXShiftVal), (yResolution - 258 - (30 * iYShiftVal)), 19, 19, WidgetTypes.WIDGET_CHANGE_SPECIALIST, i, 1, ButtonStyles.BUTTON_STYLE_CITY_PLUS )
        screen.hide( szName )

        iCount = iCount + 1

    iCount = 0

    # Decrease specialists
    i = 0
    iXShiftVal = 0
    iYShiftVal = 0

    for i in range( gc.getNumSpecialistInfos() ):
      if( i > 5 ):
        iXShiftVal = 110
        iYShiftVal = (i % 5)-1
      else:
        iYShiftVal = i

      if (gc.getSpecialistInfo(i).isVisible()):
        szName = "DecreaseSpecialist" + str(i)
        screen.setButtonGFC( szName, u"", "", xResolution - (38+iXShiftVal), (yResolution - 243 - (30 * iYShiftVal)), 19, 19, WidgetTypes.WIDGET_CHANGE_SPECIALIST, i, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS )
        screen.hide( szName )

        iCount = iCount + 1

    iCount = 0

    # Citizen Buttons
    i = 0
    iXShiftVal = 0
    iYShiftVal = 0
    iCount = 0

    for i in range( gc.getNumSpecialistInfos() ):
      if( iCount > 5 ):
        iXShiftVal = 110
        iYShiftVal = (iCount % 5) - 1
      else:
        iYShiftVal = iCount

      if (gc.getSpecialistInfo(i).isVisible()):

        szName = "CitizenDisabledButton" + str(i)
        screen.setImageButton( szName, gc.getSpecialistInfo(i).getTexture(), xResolution + 5 - (74+iXShiftVal), (yResolution - 253 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_DISABLED_CITIZEN, i, -1 )
        screen.enable( szName, False )
        screen.hide( szName )

        for j in range(MAX_CITIZEN_BUTTONS):
          szName = "CitizenButton" + str((i * 100) + j)
          screen.addCheckBoxGFC( szName, gc.getSpecialistInfo(i).getTexture(), "", xResolution + 5 - (74+iXShiftVal) - (SPECIALIST_STACK_WIDTH * j), (yResolution - 253 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j, ButtonStyles.BUTTON_STYLE_LABEL )
          screen.hide( szName )
        iCount = iCount + 1

      screen.addPanel( "SpecialistBackground", u"", u"", True, False, xResolution - 243, yResolution-455, 230, 30, PanelStyles.PANEL_STYLE_STANDARD )
      screen.setStyle( "SpecialistBackground", "Panel_City_Header_Style" )
      screen.hide( "SpecialistBackground" )
      screen.setLabel( "SpecialistLabel", "Background", localText.getText("TXT_KEY_LABEL_SPECIALISTS", ()), CvUtil.FONT_CENTER_JUSTIFY, xResolution - 128, yResolution-447, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.hide( "SpecialistLabel" )

    # SPECIALIST STACKER        END

    # **********************************************************
    # GAME DATA STRINGS
    # **********************************************************

    szGameDataList = []

    # Original:
    # xCoord = 268 + ((xResolution - 1024) / 2)
    # width = 487
    if (xResolution >= 1280):
      xCoord = 405 # 268 + 137 (Left Side + GG Bar)
      RBwidth = xResolution - 880 # (268 * 2) - 137 - 200 / Both Sides - GG Bar - GP Bar
    else:
      xCoord = 268
      RBwidth = xResolution - 538 # (Both Sides: 268 * 2)


    screen.addStackedBarGFC( "ResearchBar", xCoord, 2, RBwidth, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_RESEARCH, -1, -1 )
    screen.setStackedBarColors( "ResearchBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_RESEARCH_STORED") )
    screen.setStackedBarColors( "ResearchBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_RESEARCH_RATE") )
    screen.setStackedBarColors( "ResearchBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "ResearchBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "ResearchBar" )

# PAE (meets BUG) - Great General Bar - start
    if (xResolution >= 1280):
      xCoord = 268
      yCoord = 2
    else:
      xCoord = 308
      yCoord = 27
    screen.addStackedBarGFC( "GreatGeneralBar", xCoord, yCoord, 130, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1 )
    screen.setStackedBarColors( "GreatGeneralBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_NEGATIVE_RATE") )
    screen.setStackedBarColors( "GreatGeneralBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "GreatGeneralBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "GreatGeneralBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "GreatGeneralBar" )
# PAE - Great General Bar - end
# PAE (meets BUG) - Great Person Bar - start // >=1440
    if (xResolution >= 1280):
      xCoord = xResolution - 470
      yCoord = 2
    else:
      xCoord = xResolution - 510
      yCoord = 27
    screen.addStackedBarGFC( "GreatPersonBar", xCoord, yCoord, 200, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_GREAT_PEOPLE, -1, -1 )
    screen.setStackedBarColors( "GreatPersonBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_STORED") )
    screen.setStackedBarColors( "GreatPersonBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_RATE") )
    screen.setStackedBarColors( "GreatPersonBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "GreatPersonBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "GreatPersonBar" )
# PAE - Great Person Bar - end
# PAE - Unit Info Bar (Unit ScriptData) Bar
    xCoord = xResolution - 250
    yCoord = 90
    screen.addStackedBarGFC( "UnitInfoBar", xCoord, yCoord, 230, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.setStackedBarColors( "UnitInfoBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_EMPTY") )
    #screen.setStackedBarColors( "UnitInfoBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_CULTURE_RATE") )
    #screen.setStackedBarColors( "UnitInfoBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "UnitInfoBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "UnitInfoBar" )
# PAE - UnitInfoBar - end

    # *********************************************************************************
    # SELECTION DATA BUTTONS/STRINGS
    # *********************************************************************************

    szHideSelectionDataList = []

    screen.addStackedBarGFC( "PopulationBar", iCityCenterRow1X, iCityCenterRow1Y-4, xResolution - (iCityCenterRow1X*2), iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_POPULATION, -1, -1 )
    screen.setStackedBarColors( "PopulationBar", InfoBarTypes.INFOBAR_STORED, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getColorType() )
    screen.setStackedBarColorsAlpha( "PopulationBar", InfoBarTypes.INFOBAR_RATE, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getColorType(), 0.8 )
    screen.setStackedBarColors( "PopulationBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_NEGATIVE_RATE") )
    screen.setStackedBarColors( "PopulationBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "PopulationBar" )

    screen.addStackedBarGFC( "ProductionBar", iCityCenterRow2X, iCityCenterRow2Y-4, xResolution - (iCityCenterRow2X*2), iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_PRODUCTION, -1, -1 )
    screen.setStackedBarColors( "ProductionBar", InfoBarTypes.INFOBAR_STORED, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getColorType() )
    screen.setStackedBarColorsAlpha( "ProductionBar", InfoBarTypes.INFOBAR_RATE, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getColorType(), 0.8 )
    screen.setStackedBarColors( "ProductionBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getColorType() )
    screen.setStackedBarColors( "ProductionBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "ProductionBar" )

    screen.addStackedBarGFC( "GreatPeopleBar", xResolution - 246, yResolution - 180, 194, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_GREAT_PEOPLE, -1, -1 )
    screen.setStackedBarColors( "GreatPeopleBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_STORED") )
    screen.setStackedBarColors( "GreatPeopleBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_GREAT_PEOPLE_RATE") )
    screen.setStackedBarColors( "GreatPeopleBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "GreatPeopleBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "GreatPeopleBar" )

    screen.addStackedBarGFC( "CultureBar", 16, yResolution - 186, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_CULTURE, -1, -1 )
    screen.setStackedBarColors( "CultureBar", InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_CULTURE_STORED") )
    screen.setStackedBarColors( "CultureBar", InfoBarTypes.INFOBAR_RATE, gc.getInfoTypeForString("COLOR_CULTURE_RATE") )
    screen.setStackedBarColors( "CultureBar", InfoBarTypes.INFOBAR_RATE_EXTRA, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.setStackedBarColors( "CultureBar", InfoBarTypes.INFOBAR_EMPTY, gc.getInfoTypeForString("COLOR_EMPTY") )
    screen.hide( "CultureBar" )

    # Holy City Overlay
#    for i in range( gc.getNumReligionInfos() ):
#      xCoord = xResolution - 244 + (i * 30)
#      yCoord = 42
#      szName = "ReligionHolyCityDDS" + str(i)
#      screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_HOLYCITY_OVERLAY").getPath(), xCoord, yCoord, 24, 24, WidgetTypes.WIDGET_HELP_RELIGION_CITY, i, -1 )
#      screen.hide( szName )

#    for i in range( gc.getNumCorporationInfos() ):
#      xCoord = xResolution - 244 + (i * 30)
#      yCoord = 66
#      szName = "CorporationHeadquarterDDS" + str(i)
#      screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_HOLYCITY_OVERLAY").getPath(), xCoord, yCoord, 24, 24, WidgetTypes.WIDGET_HELP_CORPORATION_CITY, i, -1 )
#      screen.hide( szName )

#    screen.addStackedBarGFC( "PAE_RebellionBar", 16, yResolution - 292, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#    screen.hide( "PAE_RebellionBar" )

    screen.addStackedBarGFC( "PAE_RevoltBar", 16, yResolution - 332, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "PAE_RevoltBar" )
    screen.addStackedBarGFC( "PAE_EmigrationBar", 16, yResolution - 308, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "PAE_EmigrationBar" )
    screen.addStackedBarGFC( "PAE_SupplyBar", 16, yResolution - 284, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "PAE_SupplyBar" )
    screen.addStackedBarGFC( "PAE_SlavesBar", 16, yResolution - 260, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "PAE_SlavesBar" )
    screen.addStackedBarGFC( "PAE_Rebellion2Bar", 16, yResolution - 236, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "PAE_Rebellion2Bar" )

    screen.addStackedBarGFC( "NationalityBar", 16, yResolution - 210, 220, iStackBarHeight, InfoBarTypes.NUM_INFOBAR_TYPES, WidgetTypes.WIDGET_HELP_NATIONALITY, -1, -1 )
    screen.hide( "NationalityBar" )

    screen.setButtonGFC( "CityScrollMinus", u"", "", 274, 32, 32, 32, WidgetTypes.WIDGET_CITY_SCROLL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_LEFT )
    screen.hide( "CityScrollMinus" )

    screen.setButtonGFC( "CityScrollPlus", u"", "", 288, 32, 32, 32, WidgetTypes.WIDGET_CITY_SCROLL, 1, -1, ButtonStyles.BUTTON_STYLE_ARROW_RIGHT )
    screen.hide( "CityScrollPlus" )

    screen.setButtonGFC( "PlotListMinus", u"", "", 315 + ( xResolution - (iMultiListXL+iMultiListXR) - 68 ), yResolution - 171, 32, 32, WidgetTypes.WIDGET_PLOT_LIST_SHIFT, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_LEFT )
    screen.hide( "PlotListMinus" )

    screen.setButtonGFC( "PlotListPlus", u"", "", 298 + ( xResolution - (iMultiListXL+iMultiListXR) - 34 ), yResolution - 171, 32, 32, WidgetTypes.WIDGET_PLOT_LIST_SHIFT, 1, -1, ButtonStyles.BUTTON_STYLE_ARROW_RIGHT )
    screen.hide( "PlotListPlus" )

    screen.addPanel( "TradeRouteListBackground", u"", u"", True, False, 10, 157, 238, 30, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "TradeRouteListBackground", "Panel_City_Header_Style" )
    screen.hide( "TradeRouteListBackground" )

    screen.setLabel( "TradeRouteListLabel", "Background", localText.getText("TXT_KEY_HEADING_TRADEROUTE_LIST", ()), CvUtil.FONT_CENTER_JUSTIFY, 129, 165, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "TradeRouteListLabel" )

    screen.addPanel( "BuildingListBackground", u"", u"", True, False, 10, 287, 238, 30, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "BuildingListBackground", "Panel_City_Header_Style" )
    screen.hide( "BuildingListBackground" )

    screen.setLabel( "BuildingListLabel", "Background", localText.getText("TXT_KEY_CONCEPT_BUILDINGS", ()), CvUtil.FONT_CENTER_JUSTIFY, 129, 295, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
    screen.hide( "BuildingListLabel" )

    # *********************************************************************************
    # UNIT INFO ELEMENTS
    # *********************************************************************************

    i = 0
    for i in range(gc.getNumPromotionInfos()):
      szName = "PromotionButton" + str(i)
      # PAE: Widget changed to HELP Promotion
      screen.addDDSGFC( szName, gc.getPromotionInfo(i).getButton(), 180, yResolution - 18, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, i, -1 )
      screen.hide( szName )
# BUG - Stack Promotions - start
      szName = "PromotionButtonCircle" + str(i)
      x, y = self.calculatePromotionButtonPosition(screen, i)
      screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("WHITE_CIRCLE_40").getPath(), x + 11, y + 9, 16, 16, WidgetTypes.WIDGET_HELP_PROMOTION, i, -1 )
      screen.hide( szName )
# BUG - Stack Promotions - end

    # *********************************************************************************
    # SCORES
    # *********************************************************************************

    screen.addPanel( "ScoreBackground", u"", u"", True, False, 0, 0, 0, 0, PanelStyles.PANEL_STYLE_HUD_HELP )
    screen.hide( "ScoreBackground" )

    for i in range( gc.getMAX_PLAYERS() ):
      szName = "ScoreText" + str(i)
      screen.setText( szName, "Background", u"", CvUtil.FONT_RIGHT_JUSTIFY, 996, 622, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_CONTACT_CIV, i, -1 )
      screen.hide( szName )

    # This should be a forced redraw screen
    screen.setForcedRedraw( True )

    # This should show the screen immidiately and pass input to the game
    screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, True)

    szHideList = []

    szHideList.append( "CreateGroup" )
    szHideList.append( "DeleteGroup" )

    # City Tabs
    for i in range( g_NumCityTabTypes ):
      szButtonID = "CityTab" + str(i)
      szHideList.append( szButtonID )

    for i in range( g_NumHurryInfos ):
      szButtonID = "Hurry" + str(i)
      szHideList.append( szButtonID )

    szHideList.append( "Hurry0" )
    szHideList.append( "Hurry1" )

    screen.registerHideList( szHideList, len(szHideList), 0 )

    return 0

  # Will update the screen (every 250 MS)
  def updateScreen(self):

    global g_szTimeText
    global g_iTimeTextCounter

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    # Find out our resolution
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()
    self.m_iNumPlotListButtons = (xResolution - (iMultiListXL+iMultiListXR) - 68) / 34
    self.m_iNumMenuButtons = (xResolution - (iMultiListXL+iMultiListXR) - 18) / 50 # PAE, Ramk 34=>50

    # This should recreate the minimap on load games and returns if already exists -JW
    screen.initMinimap( xResolution - 210, xResolution - 9, yResolution - 131, yResolution - 9, -0.1 )

    messageControl = CyMessageControl()

    bShow = False

    # Hide all interface widgets
    #screen.hide( "EndTurnText" )

    if ( CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY ):
      if (gc.getGame().isPaused()):
        # Pause overrides other messages
        acOutput = localText.getText("SYSTEM_GAME_PAUSED", (gc.getPlayer(gc.getGame().getPausePlayer()).getNameKey(), ))
        #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
        screen.setEndTurnState( "EndTurnText", acOutput )
        bShow = True
      elif (messageControl.GetFirstBadConnection() != -1):
        # Waiting on a bad connection to resolve
        if (messageControl.GetConnState(messageControl.GetFirstBadConnection()) == 1):
          if (gc.getGame().isMPOption(MultiplayerOptionTypes.MPOPTION_ANONYMOUS)):
            acOutput = localText.getText("SYSTEM_WAITING_FOR_PLAYER", (gc.getPlayer(messageControl.GetFirstBadConnection()).getNameKey(), 0))
          else:
            acOutput = localText.getText("SYSTEM_WAITING_FOR_PLAYER", (gc.getPlayer(messageControl.GetFirstBadConnection()).getNameKey(), (messageControl.GetFirstBadConnection() + 1)))
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True
        elif (messageControl.GetConnState(messageControl.GetFirstBadConnection()) == 2):
          if (gc.getGame().isMPOption(MultiplayerOptionTypes.MPOPTION_ANONYMOUS)):
            acOutput = localText.getText("SYSTEM_PLAYER_JOINING", (gc.getPlayer(messageControl.GetFirstBadConnection()).getNameKey(), 0))
          else:
            acOutput = localText.getText("SYSTEM_PLAYER_JOINING", (gc.getPlayer(messageControl.GetFirstBadConnection()).getNameKey(), (messageControl.GetFirstBadConnection() + 1)))
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True
      else:
        # Flash select messages if no popups are present
        if ( CyInterface().shouldDisplayReturn() ):
          acOutput = localText.getText("SYSTEM_RETURN", ())
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True
        elif ( CyInterface().shouldDisplayWaitingOthers() ):
          acOutput = localText.getText("SYSTEM_WAITING", ())
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True
        elif ( CyInterface().shouldDisplayEndTurn() ):
          acOutput = localText.getText("SYSTEM_END_TURN", ())
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True
        elif ( CyInterface().shouldDisplayWaitingYou() ):
          acOutput = localText.getText("SYSTEM_WAITING_FOR_YOU", ())
          #screen.modifyLabel( "EndTurnText", acOutput, CvUtil.FONT_CENTER_JUSTIFY )
          screen.setEndTurnState( "EndTurnText", acOutput )
          bShow = True

    if ( bShow ):
      screen.showEndTurn( "EndTurnText" )
      if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW or CyInterface().isCityScreenUp() ):
        screen.moveItem( "EndTurnText", 0, yResolution - 194, -0.1 )
      else:
        screen.moveItem( "EndTurnText", 0, yResolution - 86, -0.1 )
    else:
      screen.hideEndTurn( "EndTurnText" )

    self.updateEndTurnButton()

    if (CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_ADVANCED_START):
      self.updateTimeText()
      screen.setLabel( "TimeText", "Background", g_szTimeText, CvUtil.FONT_RIGHT_JUSTIFY, xResolution - 56, 6, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.show( "TimeText" )
    else:
      screen.hide( "TimeText" )

    return 0

  # Will redraw the interface
  def redraw( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

# BUG - Field of View - start
    if bFieldOfView: self.setFieldofView(screen, CyInterface().isCityScreenUp())
# BUG - Field of View - end

    # Check Dirty Bits, see what we need to redraw...
    if (CyInterface().isDirty(InterfaceDirtyBits.PercentButtons_DIRTY_BIT) == True):
      # Percent Buttons
      self.updatePercentButtons()
      CyInterface().setDirty(InterfaceDirtyBits.PercentButtons_DIRTY_BIT, False)
    if (CyInterface().isDirty(InterfaceDirtyBits.Flag_DIRTY_BIT) == True):
      # Percent Buttons
      self.updateFlag()
      CyInterface().setDirty(InterfaceDirtyBits.Flag_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.MiscButtons_DIRTY_BIT) == True ):
      # Miscellaneous buttons (civics screen, etc)
      self.updateMiscButtons()
      CyInterface().setDirty(InterfaceDirtyBits.MiscButtons_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.InfoPane_DIRTY_BIT) == True ):
      # Info Pane Dirty Bit
      # This must come before updatePlotListButtons so that the entity widget appears in front of the stats
      self.updateInfoPaneStrings()
      CyInterface().setDirty(InterfaceDirtyBits.InfoPane_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.PlotListButtons_DIRTY_BIT) == True ):
      # Plot List Buttons Dirty
      self.updatePlotListButtons()
      CyInterface().setDirty(InterfaceDirtyBits.PlotListButtons_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT) == True ):
      # Selection Buttons Dirty
      self.updateSelectionButtons()
      CyInterface().setDirty(InterfaceDirtyBits.SelectionButtons_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.ResearchButtons_DIRTY_BIT) == True ):
      # Research Buttons Dirty
      self.updateResearchButtons()
      CyInterface().setDirty(InterfaceDirtyBits.ResearchButtons_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT) == True ):
      # Citizen Buttons Dirty
      self.updateCitizenButtons()
      CyInterface().setDirty(InterfaceDirtyBits.CitizenButtons_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.GameData_DIRTY_BIT) == True ):
      # Game Data Strings Dirty
      self.updateGameDataStrings()
      CyInterface().setDirty(InterfaceDirtyBits.GameData_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.Help_DIRTY_BIT) == True ):
      # Help Dirty bit
      self.updateHelpStrings()
      CyInterface().setDirty(InterfaceDirtyBits.Help_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.CityScreen_DIRTY_BIT) == True ):
      # Selection Data Dirty Bit
      self.updateCityScreen()
      CyInterface().setDirty(InterfaceDirtyBits.Domestic_Advisor_DIRTY_BIT, True)
      CyInterface().setDirty(InterfaceDirtyBits.CityScreen_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.Score_DIRTY_BIT) == True or CyInterface().checkFlashUpdate() ):
      # Scores!
      self.updateScoreStrings()
      CyInterface().setDirty(InterfaceDirtyBits.Score_DIRTY_BIT, False)
    if ( CyInterface().isDirty(InterfaceDirtyBits.GlobeInfo_DIRTY_BIT) == True ):
      # Globeview and Globelayer buttons
      CyInterface().setDirty(InterfaceDirtyBits.GlobeInfo_DIRTY_BIT, False)
      self.updateGlobeviewButtons()

    # PAE - River tiles
    if CvEventInterface.getEventManager().bRiverTiles_WaitOnMainInterface:
      CvEventInterface.getEventManager().bRiverTiles_WaitOnMainInterface = False
      CvEventInterface.getEventManager().bRiverTiles_NeedUpdate = True
      # Force update call. (The update event would not be propagte into
      # python as default.)
      CvEventInterface.getEventManager().onUpdate((0.0,))
    # PAE - River tiles end

    return 0

  # Will update the percent buttons
  def updatePercentButtons( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    for iI in range( CommerceTypes.NUM_COMMERCE_TYPES ):
      szString = "IncreasePercent" + str(iI)
      screen.hide( szString )
      szString = "DecreasePercent" + str(iI)
      screen.hide( szString )
# Min/Max Sliders - start
      szString = "MaxPercent" + str(iI)
      screen.hide( szString )
      szString = "MinPercent" + str(iI)
      screen.hide( szString )
# Min/Max Sliders - end

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()

    if ( not CyInterface().isCityScreenUp() or ( pHeadSelectedCity.getOwner() == gc.getGame().getActivePlayer() ) or gc.getGame().isDebugMode() ):
      iCount = 0

      if ( CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_ADVANCED_START):
        for iI in range( CommerceTypes.NUM_COMMERCE_TYPES ):
          # Intentional offset...
          eCommerce = (iI + 1) % CommerceTypes.NUM_COMMERCE_TYPES

          if (gc.getActivePlayer().isCommerceFlexible(eCommerce) or (CyInterface().isCityScreenUp() and (eCommerce == CommerceTypes.COMMERCE_GOLD))):
            szString1 = "IncreasePercent" + str(eCommerce)
            screen.setButtonGFC( szString1, u"", "", 90, 52 + (19 * iCount), 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, gc.getDefineINT("COMMERCE_PERCENT_CHANGE_INCREMENTS"), ButtonStyles.BUTTON_STYLE_CITY_PLUS )
            screen.show( szString1 )
            szString2 = "DecreasePercent" + str(eCommerce)
            screen.setButtonGFC( szString2, u"", "", 110, 52 + (19 * iCount), 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, -gc.getDefineINT("COMMERCE_PERCENT_CHANGE_INCREMENTS"), ButtonStyles.BUTTON_STYLE_CITY_MINUS )
            screen.show( szString2 )
# Min/Max Sliders - start
            szString3 = "MaxPercent" + str(eCommerce)
            screen.setButtonGFC( szString3, u"", "", 70, 52 + (19 * iCount), 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, 50, ButtonStyles.BUTTON_STYLE_CITY_PLUS )
            screen.show( szString3 )
            szString4 = "MinPercent" + str(eCommerce)
            screen.setButtonGFC( szString4, u"", "", 130, 52 + (19 * iCount), 20, 20, WidgetTypes.WIDGET_CHANGE_PERCENT, eCommerce, -50, ButtonStyles.BUTTON_STYLE_CITY_MINUS )
            screen.show( szString4 )
# Min/Max Sliders - end

            iCount = iCount + 1

            if (gc.getActivePlayer().isCommerceFlexible(eCommerce)):
              screen.enable( szString1, True )
              screen.enable( szString2, True )
# Min/Max Sliders - start
              screen.enable( szString3, True )
              screen.enable( szString4, True )
# Min/Max Sliders - end
            else:
              screen.enable( szString1, False )
              screen.enable( szString2, False )
# Min/Max Sliders - start
              screen.enable( szString3, False )
              screen.enable( szString4, False )
# Min/Max Sliders - end

    return 0

  # Will update the end Turn Button
  def updateEndTurnButton( self ):

    global g_eEndTurnButtonState

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    if ( CyInterface().shouldDisplayEndTurnButton() and CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):

      eState = CyInterface().getEndTurnState()

      bShow = False

      if ( eState == EndTurnButtonStates.END_TURN_OVER_HIGHLIGHT ):
        screen.setEndTurnState( "EndTurnButton", u"Red" )
        bShow = True
      elif ( eState == EndTurnButtonStates.END_TURN_OVER_DARK ):
        screen.setEndTurnState( "EndTurnButton", u"Red" )
        bShow = True
      elif ( eState == EndTurnButtonStates.END_TURN_GO ):
        screen.setEndTurnState( "EndTurnButton", u"Green" )
        bShow = True

      if ( bShow ):
        screen.showEndTurn( "EndTurnButton" )
      else:
        screen.hideEndTurn( "EndTurnButton" )

      if ( g_eEndTurnButtonState == eState ):
        return

      g_eEndTurnButtonState = eState

    else:
      screen.hideEndTurn( "EndTurnButton" )

    return 0

  # Update the miscellaneous buttons
  def updateMiscButtons( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    xResolution = screen.getXResolution()

    if ( CyInterface().shouldDisplayFlag() and CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
      screen.show( "CivilizationFlag" )
      screen.show( "InterfaceHelpButton" )
      screen.show( "MainMenuButton" )
    else:
      screen.hide( "CivilizationFlag" )
      screen.hide( "InterfaceHelpButton" )
      screen.hide( "MainMenuButton" )

    if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE_ALL or CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_MINIMAP_ONLY ):
      screen.hide( "InterfaceLeftBackgroundWidget" )
      screen.hide( "InterfaceTopBackgroundWidget" )
      screen.hide( "InterfaceCenterBackgroundWidget" )
      screen.hide( "InterfaceRightBackgroundWidget" )
      screen.hide( "MiniMapPanel" )
      screen.hide( "InterfaceTopLeft" )
      screen.hide( "InterfaceTopCenter" )
      screen.hide( "InterfaceTopRight" )
      screen.hide( "TurnLogButton" )
      screen.hide( "EspionageAdvisorButton" )
      screen.hide( "DomesticAdvisorButton" )
      screen.hide( "ForeignAdvisorButton" )
      screen.hide( "TechAdvisorButton" )
      screen.hide( "CivicsAdvisorButton" )
      screen.hide( "ReligiousAdvisorButton" )
      screen.hide( "CorporationAdvisorButton" )
      screen.hide( "FinanceAdvisorButton" )
      screen.hide( "MilitaryAdvisorButton" )
      screen.hide( "VictoryAdvisorButton" )
      screen.hide( "InfoAdvisorButton" )

      # Field of View slider
      screen.hide(self.szSliderTextId)
      screen.hide(self.szSliderId)

      screen.hide( "TradeRouteAdvisorButton" )
      screen.hide( "TradeRouteAdvisorButton2" )

    elif ( CyInterface().isCityScreenUp() ):
      screen.show( "InterfaceLeftBackgroundWidget" )
      screen.show( "InterfaceTopBackgroundWidget" )
      screen.show( "InterfaceCenterBackgroundWidget" )
      screen.show( "InterfaceRightBackgroundWidget" )
      screen.show( "MiniMapPanel" )
      screen.hide( "InterfaceTopLeft" )
      screen.hide( "InterfaceTopCenter" )
      screen.hide( "InterfaceTopRight" )
      screen.hide( "TurnLogButton" )
      screen.hide( "EspionageAdvisorButton" )
      screen.hide( "DomesticAdvisorButton" )
      screen.hide( "ForeignAdvisorButton" )
      screen.hide( "TechAdvisorButton" )
      screen.hide( "CivicsAdvisorButton" )
      screen.hide( "ReligiousAdvisorButton" )
      screen.hide( "CorporationAdvisorButton" )
      screen.hide( "FinanceAdvisorButton" )
      screen.hide( "MilitaryAdvisorButton" )
      screen.hide( "VictoryAdvisorButton" )
      screen.hide( "InfoAdvisorButton" )

      # Field of View slider
      screen.hide(self.szSliderTextId)
      screen.hide(self.szSliderId)

      screen.hide( "TradeRouteAdvisorButton" )
      screen.hide( "TradeRouteAdvisorButton2" )

    elif ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE):
      screen.hide( "InterfaceLeftBackgroundWidget" )
      screen.show( "InterfaceTopBackgroundWidget" )
      screen.hide( "InterfaceCenterBackgroundWidget" )
      screen.hide( "InterfaceRightBackgroundWidget" )
      screen.hide( "MiniMapPanel" )
      screen.show( "InterfaceTopLeft" )
      screen.show( "InterfaceTopCenter" )
      screen.show( "InterfaceTopRight" )
      screen.show( "TurnLogButton" )
      screen.show( "EspionageAdvisorButton" )
      screen.show( "DomesticAdvisorButton" )
      screen.show( "ForeignAdvisorButton" )
      screen.show( "TechAdvisorButton" )
      screen.show( "CivicsAdvisorButton" )
      screen.show( "ReligiousAdvisorButton" )
      screen.show( "CorporationAdvisorButton" )
      screen.show( "FinanceAdvisorButton" )
      screen.show( "MilitaryAdvisorButton" )
      screen.show( "VictoryAdvisorButton" )
      screen.show( "InfoAdvisorButton" )
      screen.moveToFront( "TurnLogButton" )
      screen.moveToFront( "EspionageAdvisorButton" )
      screen.moveToFront( "DomesticAdvisorButton" )
      screen.moveToFront( "ForeignAdvisorButton" )
      screen.moveToFront( "TechAdvisorButton" )
      screen.moveToFront( "CivicsAdvisorButton" )
      screen.moveToFront( "ReligiousAdvisorButton" )
      screen.moveToFront( "CorporationAdvisorButton" )
      screen.moveToFront( "FinanceAdvisorButton" )
      screen.moveToFront( "MilitaryAdvisorButton" )
      screen.moveToFront( "VictoryAdvisorButton" )
      screen.moveToFront( "InfoAdvisorButton" )

      # Field of View
      screen.hide(self.szSliderTextId)
      screen.hide(self.szSliderId)

      screen.show( "TradeRouteAdvisorButton" )
      screen.moveToFront( "TradeRouteAdvisorButton" )
      screen.show( "TradeRouteAdvisorButton2" )
      screen.moveToFront( "TradeRouteAdvisorButton2" )

    elif (CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_ADVANCED_START):
      screen.hide( "InterfaceLeftBackgroundWidget" )
      screen.hide( "InterfaceTopBackgroundWidget" )
      screen.hide( "InterfaceCenterBackgroundWidget" )
      screen.hide( "InterfaceRightBackgroundWidget" )
      screen.show( "MiniMapPanel" )
      screen.hide( "InterfaceTopLeft" )
      screen.hide( "InterfaceTopCenter" )
      screen.hide( "InterfaceTopRight" )
      screen.hide( "TurnLogButton" )
      screen.hide( "EspionageAdvisorButton" )
      screen.hide( "DomesticAdvisorButton" )
      screen.hide( "ForeignAdvisorButton" )
      screen.hide( "TechAdvisorButton" )
      screen.hide( "CivicsAdvisorButton" )
      screen.hide( "ReligiousAdvisorButton" )
      screen.hide( "CorporationAdvisorButton" )
      screen.hide( "FinanceAdvisorButton" )
      screen.hide( "MilitaryAdvisorButton" )
      screen.hide( "VictoryAdvisorButton" )
      screen.hide( "InfoAdvisorButton" )

      screen.hide( "TradeRouteAdvisorButton" )
      screen.hide( "TradeRouteAdvisorButton2" )

    elif ( CyEngine().isGlobeviewUp() ):
      screen.hide( "InterfaceLeftBackgroundWidget" )
      screen.hide( "InterfaceTopBackgroundWidget" )
      screen.hide( "InterfaceCenterBackgroundWidget" )
      screen.show( "InterfaceRightBackgroundWidget" )
      screen.show( "MiniMapPanel" )
      screen.show( "InterfaceTopLeft" )
      screen.show( "InterfaceTopCenter" )
      screen.show( "InterfaceTopRight" )
      screen.show( "TurnLogButton" )
      screen.show( "EspionageAdvisorButton" )
      screen.show( "DomesticAdvisorButton" )
      screen.show( "ForeignAdvisorButton" )
      screen.show( "TechAdvisorButton" )
      screen.show( "CivicsAdvisorButton" )
      screen.show( "ReligiousAdvisorButton" )
      screen.show( "CorporationAdvisorButton" )
      screen.show( "FinanceAdvisorButton" )
      screen.show( "MilitaryAdvisorButton" )
      screen.show( "VictoryAdvisorButton" )
      screen.show( "InfoAdvisorButton" )
      screen.moveToFront( "TurnLogButton" )
      screen.moveToFront( "EspionageAdvisorButton" )
      screen.moveToFront( "DomesticAdvisorButton" )
      screen.moveToFront( "ForeignAdvisorButton" )
      screen.moveToFront( "TechAdvisorButton" )
      screen.moveToFront( "CivicsAdvisorButton" )
      screen.moveToFront( "ReligiousAdvisorButton" )
      screen.moveToFront( "CorporationAdvisorButton" )
      screen.moveToFront( "FinanceAdvisorButton" )
      screen.moveToFront( "MilitaryAdvisorButton" )
      screen.moveToFront( "VictoryAdvisorButton" )
      screen.moveToFront( "InfoAdvisorButton" )

      # Field of View slider
      screen.hide(self.szSliderTextId)
      screen.hide(self.szSliderId)

      screen.show( "TradeRouteAdvisorButton" )
      screen.moveToFront( "TradeRouteAdvisorButton" )
      screen.show( "TradeRouteAdvisorButton2" )
      screen.moveToFront( "TradeRouteAdvisorButton2" )

    else:
      screen.show( "InterfaceLeftBackgroundWidget" )
      screen.show( "InterfaceTopBackgroundWidget" )
      screen.show( "InterfaceCenterBackgroundWidget" )
      screen.show( "InterfaceRightBackgroundWidget" )
      screen.show( "MiniMapPanel" )
      screen.show( "InterfaceTopLeft" )
      screen.show( "InterfaceTopCenter" )
      screen.show( "InterfaceTopRight" )
      screen.show( "TurnLogButton" )
      screen.show( "EspionageAdvisorButton" )
      screen.show( "DomesticAdvisorButton" )
      screen.show( "ForeignAdvisorButton" )
      screen.show( "TechAdvisorButton" )
      screen.show( "CivicsAdvisorButton" )
      screen.show( "ReligiousAdvisorButton" )
      screen.show( "CorporationAdvisorButton" )
      screen.show( "FinanceAdvisorButton" )
      screen.show( "MilitaryAdvisorButton" )
      screen.show( "VictoryAdvisorButton" )
      screen.show( "InfoAdvisorButton" )
      screen.moveToFront( "TurnLogButton" )
      screen.moveToFront( "EspionageAdvisorButton" )
      screen.moveToFront( "DomesticAdvisorButton" )
      screen.moveToFront( "ForeignAdvisorButton" )
      screen.moveToFront( "TechAdvisorButton" )
      screen.moveToFront( "CivicsAdvisorButton" )
      screen.moveToFront( "ReligiousAdvisorButton" )
      screen.moveToFront( "CorporationAdvisorButton" )
      screen.moveToFront( "FinanceAdvisorButton" )
      screen.moveToFront( "MilitaryAdvisorButton" )
      screen.moveToFront( "VictoryAdvisorButton" )
      screen.moveToFront( "InfoAdvisorButton" )

      # Field of View slider
      screen.show(self.szSliderTextId)
      screen.show(self.szSliderId)

      screen.show( "TradeRouteAdvisorButton" )
      screen.moveToFront( "TradeRouteAdvisorButton" )
      screen.show( "TradeRouteAdvisorButton2" )
      screen.moveToFront( "TradeRouteAdvisorButton2" )

    screen.updateMinimapVisibility()

    return 0

  # Update plot List Buttons
  def updatePlotListButtons( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    bHandled = False
    if ( CyInterface().shouldDisplayUnitModel() and CyEngine().isGlobeviewUp() == False and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL ):
      if ( CyInterface().isCitySelection() ):

        iOrders = CyInterface().getNumOrdersQueued()

        for i in range( iOrders ):
          if ( bHandled == False ):
            eOrderNodeType = CyInterface().getOrderNodeType(i)
            if (eOrderNodeType  == OrderTypes.ORDER_TRAIN ):
              screen.addUnitGraphicGFC( "InterfaceUnitModel", CyInterface().getOrderNodeData1(i), 175, yResolution - 138, 123, 132, WidgetTypes.WIDGET_HELP_SELECTED, 0, -1,  -20, 30, 1, False )
              bHandled = True
            elif ( eOrderNodeType == OrderTypes.ORDER_CONSTRUCT ):
              screen.addBuildingGraphicGFC( "InterfaceUnitModel", CyInterface().getOrderNodeData1(i), 175, yResolution - 138, 123, 132, WidgetTypes.WIDGET_HELP_SELECTED, 0, -1,  -20, 30, 0.8, False )
              bHandled = True
            elif ( eOrderNodeType == OrderTypes.ORDER_CREATE ):
              if(gc.getProjectInfo(CyInterface().getOrderNodeData1(i)).isSpaceship()):
                modelType = 0
                screen.addSpaceShipWidgetGFC("InterfaceUnitModel", 175, yResolution - 138, 123, 132, CyInterface().getOrderNodeData1(i), modelType, WidgetTypes.WIDGET_HELP_SELECTED, 0, -1)
              else:
                screen.hide( "InterfaceUnitModel" )
              bHandled = True
            elif ( eOrderNodeType == OrderTypes.ORDER_MAINTAIN ):
              screen.hide( "InterfaceUnitModel" )
              bHandled = True

        if ( not bHandled ):
          screen.hide( "InterfaceUnitModel" )
          bHandled = True

        screen.moveToFront("SelectedCityText")

      elif ( CyInterface().getHeadSelectedUnit() ):
        screen.addUnitGraphicGFC( "InterfaceUnitModel", CyInterface().getHeadSelectedUnit().getUnitType(), 175, yResolution - 138, 123, 132, WidgetTypes.WIDGET_UNIT_MODEL, CyInterface().getHeadSelectedUnit().getUnitType(), -1,  -20, 30, 1, False )
        #screen.moveToFront("SelectedUnitText")  # disabled for PAE Unit Detail Promo Icons
      else:
        screen.hide( "InterfaceUnitModel" )
    else:
      screen.hide( "InterfaceUnitModel" )

    pPlot = CyInterface().getSelectionPlot()

    for i in range(gc.getNumPromotionInfos()):
      szName = "PromotionButton" + str(i)
      screen.moveToFront( szName )


# BUG - Stack Promotions - start
    for i in range(gc.getNumPromotionInfos()):
                        szName = "PromotionButtonCircle" + str(i)
                        screen.moveToFront( szName )
                        szName = "PromotionButtonCount" + str(i)
                        screen.moveToFront( szName )
# BUG - Stack Promotions - end

    screen.hide( "PlotListMinus" )
    screen.hide( "PlotListPlus" )

    for j in range(gc.getMAX_PLOT_LIST_ROWS()):
      #szStringPanel = "PlotListPanel" + str(j)
      #screen.hide(szStringPanel)

      for i in range(self.numPlotListButtons()):
        szString = "PlotListButton" + str(j*self.numPlotListButtons()+i)
        screen.hide( szString )

        szStringHealth = szString + "Health"
        screen.hide( szStringHealth )

        szStringIcon = szString + "Icon"
        screen.hide( szStringIcon )

        # PAE Extra Overlay for Leaders, Heroes and PromotionReadyUnits
        szStringIcon = szString + "Icon2"
        screen.hide( szStringIcon )
        szStringIcon = szString + "Icon3"
        screen.hide( szStringIcon )
        # -----------

    if ( pPlot and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyEngine().isGlobeviewUp() == False):

      iVisibleUnits = CyInterface().getNumVisibleUnits()
      iCount = -(CyInterface().getPlotListColumn())


      bLeftArrow = False
      bRightArrow = False

      if (CyInterface().isCityScreenUp()):
        iMaxRows = 1
        iSkipped = (gc.getMAX_PLOT_LIST_ROWS() - 1) * self.numPlotListButtons()
        iCount += iSkipped
      else:
        iMaxRows = gc.getMAX_PLOT_LIST_ROWS()
        iCount += CyInterface().getPlotListOffset()
        iSkipped = 0

      CyInterface().cacheInterfacePlotUnits(pPlot)
      for i in range(CyInterface().getNumCachedInterfacePlotUnits()):
        pLoopUnit = CyInterface().getCachedInterfacePlotUnit(i)
        if (pLoopUnit):

          if ((iCount == 0) and (CyInterface().getPlotListColumn() > 0)):
            bLeftArrow = True
          elif ((iCount == (gc.getMAX_PLOT_LIST_ROWS() * self.numPlotListButtons() - 1)) and ((iVisibleUnits - iCount - CyInterface().getPlotListColumn() + iSkipped) > 1)):
            bRightArrow = True

          if ((iCount >= 0) and (iCount <  self.numPlotListButtons() * gc.getMAX_PLOT_LIST_ROWS())):
            if ((pLoopUnit.getTeam() != gc.getGame().getActiveTeam()) or pLoopUnit.isWaiting()):

              if pLoopUnit.getGroup().getActivityType() == ActivityTypes.ACTIVITY_SENTRY:
                szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_SENTRY").getPath()
              else:
                szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_FORTIFY").getPath()

            elif (pLoopUnit.canMove()):

              if (pLoopUnit.hasMoved()):
                szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_HASMOVED").getPath()
              else:
                szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_MOVE").getPath()

            else:
              szFileName = ArtFileMgr.getInterfaceArtInfo("OVERLAY_NOMOVE").getPath()

            # PAE Extra Overlay for Leaders, Heroes and PromotionReadyUnits
            szPAELeaderHero = ""
            szPAEPromotion = ""
            if pLoopUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_LEADER")) and pLoopUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_HERO")):
              szPAELeaderHero = "Art/Interface/Buttons/Unitoverlay/PAE_unitoverlay_hero2.dds"
            elif pLoopUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_LEADER")):
              szPAELeaderHero = "Art/Interface/Buttons/Unitoverlay/PAE_unitoverlay_star.dds"
            elif pLoopUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_HERO")):
              szPAELeaderHero = "Art/Interface/Buttons/Unitoverlay/PAE_unitoverlay_hero.dds"
            if pLoopUnit.isPromotionReady() and pLoopUnit.getOwner() == gc.getGame().getActivePlayer():
              szPAEPromotion = "Art/Interface/Buttons/Unitoverlay/PAE_unitoverlay_promo.dds"
            # -------------

            szString = "PlotListButton" + str(iCount)
            screen.changeImageButton( szString, pLoopUnit.getButton() )
            if ( pLoopUnit.getOwner() == gc.getGame().getActivePlayer() ):
              bEnable = True
            else:
              bEnable = False
            screen.enable(szString, bEnable)

            if (pLoopUnit.IsSelected()):
              screen.setState(szString, True)
            else:
              screen.setState(szString, False)
            screen.show( szString )

            # place the health bar
            if (pLoopUnit.isFighting()):
              bShowHealth = False
            elif (pLoopUnit.getDomainType() == DomainTypes.DOMAIN_AIR):
              bShowHealth = pLoopUnit.canAirAttack()
            else:
              bShowHealth = pLoopUnit.canFight()

            if bShowHealth:
              szStringHealth = szString + "Health"
              screen.setBarPercentage( szStringHealth, InfoBarTypes.INFOBAR_STORED, float( pLoopUnit.currHitPoints() ) / float( pLoopUnit.maxHitPoints() ) )
              if (pLoopUnit.getDamage() >= ((pLoopUnit.maxHitPoints() * 2) / 3)):
                screen.setStackedBarColors(szStringHealth, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_RED"))
              elif (pLoopUnit.getDamage() >= (pLoopUnit.maxHitPoints() / 3)):
                screen.setStackedBarColors(szStringHealth, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_YELLOW"))
              else:
                screen.setStackedBarColors(szStringHealth, InfoBarTypes.INFOBAR_STORED, gc.getInfoTypeForString("COLOR_GREEN"))
              screen.show( szStringHealth )

            # Adds the overlay first
            szStringIcon = szString + "Icon"
            screen.changeDDSGFC( szStringIcon, szFileName )
            screen.show( szStringIcon )

            # PAE Extra Overlay for Leaders, Heroes and PromotionReadyUnits
            if szPAELeaderHero != "":
              szStringIcon = szString + "Icon2"
              screen.changeDDSGFC( szStringIcon, szPAELeaderHero )
              screen.show( szStringIcon )
            if szPAEPromotion != "":
              szStringIcon = szString + "Icon3"
              screen.changeDDSGFC( szStringIcon, szPAEPromotion )
              screen.show( szStringIcon )
            # ----------------------

          iCount = iCount + 1

      if (iVisibleUnits > self.numPlotListButtons() * iMaxRows):
        screen.enable("PlotListMinus", bLeftArrow)
        screen.show( "PlotListMinus" )

        screen.enable("PlotListPlus", bRightArrow)
        screen.show( "PlotListPlus" )

    return 0

  # This will update the flag widget for SP hotseat and dbeugging
  def updateFlag( self ):

    if ( CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_ADVANCED_START ):
      screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
      xResolution = screen.getXResolution()
      yResolution = screen.getYResolution()
      screen.addFlagWidgetGFC( "CivilizationFlag", xResolution - 288, yResolution - 138, 68, 250, gc.getGame().getActivePlayer(), WidgetTypes.WIDGET_FLAG, gc.getGame().getActivePlayer(), -1)

  # Will hide and show the selection buttons and their associated buttons
  def updateSelectionButtons( self ):

    global SELECTION_BUTTON_COLUMNS
    global MAX_SELECTION_BUTTONS
    global g_pSelectedUnit

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()
    pHeadSelectedUnit = CyInterface().getHeadSelectedUnit()

    global g_NumEmphasizeInfos
    global g_NumCityTabTypes
    global g_NumHurryInfos
    global g_NumUnitClassInfos
    global g_NumBuildingClassInfos
    global g_NumProjectInfos
    global g_NumProcessInfos
    global g_NumActionInfos

    # Find out our resolution
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    # Ramk, Korrektur der Breite, um horizontale Scrollbar zu verhindern
    # screen.addMultiListControlGFC( "BottomButtonContainer", u"", iMultiListXL, yResolution - 113, xResolution - (iMultiListXL+iMultiListXR), 100, 4, 48, 48, TableStyles.TABLE_STYLE_STANDARD )
    breite = self.m_iNumMenuButtons * 50 + 34 # Hinterer Summand soll horizontale Scrollbar verhindern
    screen.addMultiListControlGFC( "BottomButtonContainer", u"", iMultiListXL, yResolution - 113, breite, 100, 4, 48, 48, TableStyles.TABLE_STYLE_STANDARD )

    screen.clearMultiList( "BottomButtonContainer" )
    screen.hide( "BottomButtonContainer" )

    # All of the hides...
    self.setMinimapButtonVisibility(False)

    screen.hideList( 0 )

    for i in range (g_NumEmphasizeInfos):
      szButtonID = "Emphasize" + str(i)
      screen.hide( szButtonID )

    # Hurry button show...
    for i in range( g_NumHurryInfos ):
      szButtonID = "Hurry" + str(i)
      screen.hide( szButtonID )

    # Conscript Button Show
    screen.hide( "Conscript" )
    #screen.hide( "Liberate" )
    screen.hide( "AutomateProduction" )
    screen.hide( "AutomateCitizens" )

    if (not CyEngine().isGlobeviewUp() and pHeadSelectedCity):

      self.setMinimapButtonVisibility(True)

      if ((pHeadSelectedCity.getOwner() == gc.getGame().getActivePlayer()) or gc.getGame().isDebugMode()):

        iBtnX = xResolution - 284
        iBtnY = yResolution - 177
        iBtnW = 64
        iBtnH = 30

        # Liberate button
        #szText = "<font=1>" + localText.getText("TXT_KEY_LIBERATE_CITY", ()) + "</font>"
        #screen.setButtonGFC( "Liberate", szText, "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_LIBERATE_CITY, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        #screen.setStyle( "Liberate", "Button_CityT1_Style" )
        #screen.hide( "Liberate" )

        iBtnSX = xResolution - 284

        iBtnX = iBtnSX
        iBtnY = yResolution - 140
        iBtnW = 64
        iBtnH = 30

        # Conscript button
        szText = "<font=1>" + localText.getText("TXT_KEY_DRAFT", ()) + "</font>"
        screen.setButtonGFC( "Conscript", szText, "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_CONSCRIPT, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        screen.setStyle( "Conscript", "Button_CityT1_Style" )
        screen.hide( "Conscript" )

        iBtnY += iBtnH
        iBtnW = 32
        iBtnH = 28

        # Hurry Buttons
        screen.setButtonGFC( "Hurry0", "", "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_HURRY, 0, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        screen.setStyle( "Hurry0", "Button_CityC1_Style" )
        screen.hide( "Hurry0" )

        iBtnX += iBtnW

        screen.setButtonGFC( "Hurry1", "", "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_HURRY, 1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        screen.setStyle( "Hurry1", "Button_CityC2_Style" )
        screen.hide( "Hurry1" )

        iBtnX = iBtnSX
        iBtnY += iBtnH

        # Automate Production Button
        screen.addCheckBoxGFC( "AutomateProduction", "", "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_AUTOMATE_PRODUCTION, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        screen.setStyle( "AutomateProduction", "Button_CityC3_Style" )

        iBtnX += iBtnW

        # Automate Citizens Button
        screen.addCheckBoxGFC( "AutomateCitizens", "", "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_AUTOMATE_CITIZENS, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
        screen.setStyle( "AutomateCitizens", "Button_CityC4_Style" )

        iBtnY += iBtnH
        iBtnX = iBtnSX

        iBtnW  = 22
        iBtnWa  = 20
        iBtnH  = 24
        iBtnHa  = 27

        # Set Emphasize buttons
        i = 0
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        i+=1
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX+iBtnW, iBtnY, iBtnWa, iBtnH, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        i+=1
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX+iBtnW+iBtnWa, iBtnY, iBtnW, iBtnH, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        iBtnY += iBtnH

        i+=1
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX, iBtnY, iBtnW, iBtnHa, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        i+=1
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX+iBtnW, iBtnY, iBtnWa, iBtnHa, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        i+=1
        szButtonID = "Emphasize" + str(i)
        screen.addCheckBoxGFC( szButtonID, "", "", iBtnX+iBtnW+iBtnWa, iBtnY, iBtnW, iBtnHa, WidgetTypes.WIDGET_EMPHASIZE, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
        szStyle = "Button_CityB" + str(i+1) + "_Style"
        screen.setStyle( szButtonID, szStyle )
        screen.hide( szButtonID )

        g_pSelectedUnit = 0
        screen.setState( "AutomateCitizens", pHeadSelectedCity.isCitizensAutomated() )
        screen.setState( "AutomateProduction", pHeadSelectedCity.isProductionAutomated() )

        for i in range (g_NumEmphasizeInfos):
          szButtonID = "Emphasize" + str(i)
          screen.show( szButtonID )
          if ( pHeadSelectedCity.AI_isEmphasize(i) ):
            screen.setState( szButtonID, True )
          else:
            screen.setState( szButtonID, False )

        # City Tabs
        for i in range( g_NumCityTabTypes ):
          szButtonID = "CityTab" + str(i)
          screen.show( szButtonID )

        # Hurry button show...
        for i in range( g_NumHurryInfos ):
          szButtonID = "Hurry" + str(i)
          screen.show( szButtonID )
          screen.enable( szButtonID, pHeadSelectedCity.canHurry(i, False) )

        # Conscript Button Show
        screen.show( "Conscript" )
        if (pHeadSelectedCity.canConscript()):
          screen.enable( "Conscript", True )
        else:
          screen.enable( "Conscript", False )

        # Liberate Button Show
        #screen.show( "Liberate" )
        #if (-1 != pHeadSelectedCity.getLiberationPlayer()):
        #  screen.enable( "Liberate", True )
        #else:
        #  screen.enable( "Liberate", False )

        """ (PAE, Ramk)
        - Unterteilung in in linken und rechten Block.
        - Maximale Anzahl von Icons pro Zeile: N.
        - Normale Aufteilung Links/Rechts: Jeweils N/2. ( links + N%2 )
        - Links und rechts werden zeilenweise Listen angelegt. Die Zeilen können beliebig lang sein.
        - Beginnt eine Zeile mit 'None', so erzwingt das immer eine neue Zeile für das folgende Icon.
          (Beispiel: Sprung von Gebäuden zu Wundern)
        - Danach werden Icons zeilenweise durchlaufen. Sind zu viele für die Maximalbreite angegeben,
          werden die überschüssigen in die nächste Zeile verschoben.
        - Falls links die Maximalbreite (N/2) nicht erreicht wird, wird der rechten Seite mehr Platz
          eingeräumt (sofern notwendig).
        - Am Ende werden die beiden Listen nebeneinander in den "BottomButtonContainer" eingefügt, wobei
          die Freistellen mit Platzhaltern gefüllt werden.
        """
        #numIcons = 23
        numIcons = max(2,self.m_iNumMenuButtons) - 1
        numIconsRight = numIcons/2
        numIconsLeft = numIcons - numIconsRight
        self.iconsLeft = [[]]
        self.iconsRight = [[]]
        rowLeft = 0
        rowRight = 0
        cityTab = 0

        iCount = 0
        iRow = 0
        bFound = False

        """# Debug, comment normal setText for this widget out, if you uncomment this...
        szBuffer = u"<font=4>"
        szBuffer += u"%s: %d %d %d" %("Test", numIcons, numIconsLeft, numIconsRight)
        szBuffer += u"</font>"
        screen.setText( "CityNameText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512), 32, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_CITY_NAME, -1, -1 )
        """

        # Units to construct
        for i in range(g_NumUnitClassInfos):

          # PAE - Abbruch bei unbaubare Einheiten
          if i == gc.getInfoTypeForString("UNITCLASS_PROPHET"): break

          eLoopUnit = gc.getCivilizationInfo(pHeadSelectedCity.getCivilizationType()).getCivilizationUnits(i)

          # PAE - Zeilenumbruch bei bestimmten Einheitenklassen (unitcombattypes)
          if (eLoopUnit == gc.getInfoTypeForString("UNIT_WARRIOR") or eLoopUnit == gc.getInfoTypeForString("UNIT_LIGHT_ARCHER") \
          or eLoopUnit == gc.getInfoTypeForString("UNIT_LIGHT_CHARIOT") or i == gc.getInfoTypeForString("UNITCLASS_SPECIAL1") \
          or eLoopUnit == gc.getInfoTypeForString("UNIT_INQUISITOR") or eLoopUnit == gc.getInfoTypeForString("UNITCLASS_ARCHER_KRETA")) and iCount > 6:
            iCount = 0
            if (bFound):
              iRow = iRow + 1
              rowLeft += 1
              self.iconsLeft.append([])
            bFound = False

          # Ramks city widgets
          if pHeadSelectedCity.canTrain(eLoopUnit, False, True):

            # PAE: Sobald die Einheit mit irgendeiner CLASS upgradebar ist, soll diese nicht mehr angezeigt werden
            bShow = True
            #j=i # Upgrade Classes kommen im XML eigentlich immer nachher, erspart den check von Beginn an
            #for j in range(g_NumUnitClassInfos):
            #  if gc.getUnitInfo(eLoopUnit).getUpgradeUnitClass(j):
            #    eLoopUnit2 = gc.getCivilizationInfo(pHeadSelectedCity.getCivilizationType()).getCivilizationUnits(j)
            #    if pHeadSelectedCity.canTrain(eLoopUnit2, False, False):
            #      bShow = False
            #      break

            if bShow:
              szButton = gc.getPlayer(pHeadSelectedCity.getOwner()).getUnitButton(eLoopUnit)
              self.iconsLeft[rowLeft].append( (
                [szButton, WidgetTypes.WIDGET_TRAIN, i, -1, False],
                pHeadSelectedCity.canTrain(eLoopUnit, False, False),
                cityTab
                ) )

              iCount = iCount + 1
              bFound = True

        iCount = 0
        if (bFound):
          iRow = iRow + 1
        bFound = False
        cityTab += 1

        # Buildings to construct
        for i in range ( g_NumBuildingClassInfos ):
          if (not isLimitedWonderClass(i)):
            eLoopBuilding = gc.getCivilizationInfo(pHeadSelectedCity.getCivilizationType()).getCivilizationBuildings(i)
            if (pHeadSelectedCity.canConstruct(eLoopBuilding, False, True, False)):
              szButton = gc.getBuildingInfo(eLoopBuilding).getButton()
              self.iconsRight[rowRight].append( (
                [szButton, WidgetTypes.WIDGET_CONSTRUCT, i, -1, False],
                pHeadSelectedCity.canConstruct(eLoopBuilding, False, False, False),
                cityTab
                ) )
              iCount = iCount + 1
              bFound = True

        iCount = 0
        if (bFound):
          iRow = iRow + 1
          rowRight += 1
          self.iconsRight.append([None])
        bFound = False
        cityTab += 1

        # Wonders to construct
        i = 0
        for i in range( g_NumBuildingClassInfos ):
          if (isLimitedWonderClass(i)):
            eLoopBuilding = gc.getCivilizationInfo(pHeadSelectedCity.getCivilizationType()).getCivilizationBuildings(i)
            if (pHeadSelectedCity.canConstruct(eLoopBuilding, False, True, False)):
              szButton = gc.getBuildingInfo(eLoopBuilding).getButton()
              self.iconsRight[rowRight].append( (
                [szButton, WidgetTypes.WIDGET_CONSTRUCT, i, -1, False],
                pHeadSelectedCity.canConstruct(eLoopBuilding, False, False, False),
                cityTab
                ) )
              iCount = iCount + 1
              bFound = True

        iCount = 0
        if (bFound):
          iRow = iRow + 1
          #rowRight += 1
          #self.iconsRight.append([])
        bFound = False

        # Projects
        i = 0
        for i in range( g_NumProjectInfos ):
          if (pHeadSelectedCity.canCreate(i, False, True)):
            szButton = gc.getProjectInfo(i).getButton()
            self.iconsRight[rowRight].append( (
              [szButton, WidgetTypes.WIDGET_CREATE, i, -1, False],
              pHeadSelectedCity.canCreate(i, False, False),
              cityTab
              ) )
            iCount = iCount + 1
            bFound = True

        # Processes
        i = 0
        for i in range( g_NumProcessInfos ):
          if (pHeadSelectedCity.canMaintain(i, False)):
            szButton = gc.getProcessInfo(i).getButton()
            self.iconsRight[rowRight].append( (
              [szButton, WidgetTypes.WIDGET_MAINTAIN, i, -1, False],
              True,
              cityTab
              ) )
            iCount = iCount + 1
            bFound = True

        if numIcons > 15:
          self.sortButtons( self.iconsLeft, numIconsLeft)
          [numIconsLeft, numIconsRight] = self.optimalPartition( numIconsLeft, numIconsRight, self.iconsLeft, self.iconsRight)
          self.sortButtons( self.iconsRight, numIconsRight)
          self.insertButtons( self.iconsLeft, self.iconsRight, numIconsLeft+1, numIcons+1)
          self.cityTabsJumpmarks = [0,0,self.findCityTabRow( self.iconsRight, 2)]
        else:
          self.sortButtons( self.iconsLeft, numIcons+1)
          self.sortButtons( self.iconsRight, numIcons+1)
          self.insertButtons( self.iconsLeft+self.iconsRight, [], 0, numIcons+1)
          # Find indizes of first building row and first wonder row
          rowBuildings = len(self.iconsLeft)
          rowWonders = rowBuildings + self.findCityTabRow( self.iconsRight, 2)
          self.cityTabsJumpmarks = [0,rowBuildings,rowWonders]

        screen.show( "BottomButtonContainer" )
        screen.selectMultiList( "BottomButtonContainer", CyInterface().getCityTabSelectionRow() )

    elif (not CyEngine().isGlobeviewUp() and pHeadSelectedUnit and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY):

      self.setMinimapButtonVisibility(True)

      if (CyInterface().getInterfaceMode() == InterfaceModeTypes.INTERFACEMODE_SELECTION):

        if ( pHeadSelectedUnit.getOwner() == gc.getGame().getActivePlayer() and g_pSelectedUnit != pHeadSelectedUnit ):

          g_pSelectedUnit = pHeadSelectedUnit

          iCount = 0

          # Limes
          lBuildInfos = []
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES1"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES3"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES4"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES5"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES6"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES7"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES8"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES9"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_1"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_2"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_3"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_4"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_5"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_6"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_7"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_8"))
          lBuildInfos.append(gc.getInfoTypeForString("BUILD_LIMES2_9"))

          actions = CyInterface().getActionsToShow()
          for i in actions:
            if not (gc.getActionInfo(i).getMissionType() == MissionTypes.MISSION_BUILD and gc.getActionInfo(i).getMissionData() in lBuildInfos):
              screen.appendMultiListButton( "BottomButtonContainer", gc.getActionInfo(i).getButton(), 0, WidgetTypes.WIDGET_ACTION, i, -1, False )
              screen.show( "BottomButtonContainer" )

              if ( not CyInterface().canHandleAction(i, False) ):
               screen.disableMultiListButton( "BottomButtonContainer", 0, iCount, gc.getActionInfo(i).getButton() )

              if ( pHeadSelectedUnit.isActionRecommended(i) ):#or gc.getActionInfo(i).getCommandType() == CommandTypes.COMMAND_PROMOTION ):
               screen.enableMultiListPulse( "BottomButtonContainer", True, 0, iCount )
              else:
               screen.enableMultiListPulse( "BottomButtonContainer", False, 0, iCount )

              # PAE V: Aussenhandelsposten fuer HI nur ausserhalb der eigenen Kulturgrenzen baubar
              #if gc.getActionInfo(i).getMissionData() == gc.getInfoTypeForString("BUILD_HANDELSPOSTEN"):
              #  if g_pSelectedUnit.plot().getOwner() == g_pSelectedUnit.getOwner():
              #    screen.disableMultiListButton( "BottomButtonContainer", 0, iCount, gc.getActionInfo(i).getButton() )

              iCount = iCount + 1

          if (CyInterface().canCreateGroup()):
            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_CREATEGROUP").getPath(), 0, WidgetTypes.WIDGET_CREATE_GROUP, -1, -1, False )
            screen.show( "BottomButtonContainer" )

            iCount = iCount + 1

          if (CyInterface().canDeleteGroup()):
            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_BUTTONS_SPLITGROUP").getPath(), 0, WidgetTypes.WIDGET_DELETE_GROUP, -1, -1, False )
            screen.show( "BottomButtonContainer" )

            iCount = iCount + 1

          ############################################ Unit Buttons #############################################
          pUnit = g_pSelectedUnit
          iUnitType = pUnit.getUnitType()
          pUnitOwner = gc.getPlayer(pUnit.getOwner())
          pTeam = gc.getTeam(pUnitOwner.getTeam())

          if pUnitOwner.isTurnActive():
            bCapital = False
            if gc.getMap().plot( g_pSelectedUnit.getX(), g_pSelectedUnit.getY() ).isCity():
              bCity = True
              pCity = gc.getMap().plot( g_pSelectedUnit.getX(), g_pSelectedUnit.getY() ).getPlotCity( )
              if pCity.isCapital() and pCity.getOwner() == pUnit.getOwner(): bCapital = True
            else:
              bCity = False


            # ----------
            # Missionar in eine eigene heidnische Stadt schicken
            #if pUnit.getUnitAIType() == gc.getInfoTypeForString("UNITAI_MISSIONARY"):
            #   screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_spread_rel.dds", 0, WidgetTypes.WIDGET_GENERAL, 731, 731, False )
            #   screen.show( "BottomButtonContainer" )
            #   iCount = iCount + 1

            # ----------
            # Haendler in die naechste fremde Stadt schicken
            #if pUnit.getUnitAIType() == gc.getInfoTypeForString("UNITAI_MERCHANT") or iUnitType == gc.getInfoTypeForString("UNIT_GAULOS") or iUnitType == gc.getInfoTypeForString("UNIT_CARVEL_TRADE"):
            #   if iUnitType != gc.getInfoTypeForString("UNIT_GREAT_SPY"):
            #     screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_merchant.dds", 0, WidgetTypes.WIDGET_GENERAL, 732, 732, False )
            #     screen.show( "BottomButtonContainer" )
            #     iCount = iCount + 1

            # ----------
            # Inquisitor
            if iUnitType == gc.getInfoTypeForString("UNIT_INQUISITOR") and bCity:
              pCityPlayer = gc.getPlayer( pCity.getOwner() )
              if ( pCity.getOwner() == pUnit.getOwner() ) or ( gc.getTeam( pCityPlayer.getTeam() ).isVassal( gc.getPlayer( pUnit. getOwner() ).getTeam() ) ):
                iStateReligion = gc.getPlayer( pUnit.getOwner() ).getStateReligion( )
                if iStateReligion != -1:
                  if pCity.isHasReligion( iStateReligion ):
                    for iReligion in range(gc.getNumReligionInfos()):
                      if pCity.isHasReligion(iReligion):
                       if pCity.isHolyCityByType(iReligion) == 0:
                        if iReligion != iStateReligion:


                          screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_GODS_PERSICUTION").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 665, 665, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return

            # --------------------
            # Elefant / Kamel
            if iUnitType == gc.getInfoTypeForString("UNIT_ELEFANT"):
              # in city
              if bCity:
                if not pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_ELEPHANT_STABLE")):
                  pCityPlayer = gc.getPlayer( pCity.getOwner() )
                  if pCity.getOwner() == pUnit.getOwner() or gc.getTeam(pCityPlayer.getTeam()).isVassal(gc.getPlayer(pUnit.getOwner()).getTeam()):
                    # Check plots (Klima / climate)
                    bOK = False
                    for i in range(3):
                      for j in range(3):
                        loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                        if loopPlot != None and not loopPlot.isNone():
                          if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") or loopPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                            bOK = True
                            break
                      if bOK: break

                    if bOK:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Builds/button_elefantenstall.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return

                    else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_elestall_grau.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 2, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return
              # not in city
              else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_elestall_grau.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 3, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return
            # --------------------
            elif iUnitType == gc.getInfoTypeForString("UNIT_CAMEL") or iUnitType == gc.getInfoTypeForString("UNIT_WILD_CAMEL"):
              # in city
              if bCity:
                if not pCity.isHasBuilding(gc.getInfoTypeForString("BUILDING_CAMEL_STABLE")):
                  pCityPlayer = gc.getPlayer( pCity.getOwner() )
                  if pCity.getOwner() == pUnit.getOwner() or gc.getTeam(pCityPlayer.getTeam()).isVassal(gc.getPlayer(pUnit.getOwner()).getTeam()):
                    # Check plots (Klima / climate)
                    bOK = False
                    for i in range(3):
                      for j in range(3):
                        loopPlot = gc.getMap().plot(pCity.getX() + i - 1, pCity.getY() + j - 1)
                        if loopPlot != None and not loopPlot.isNone():
                          if loopPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT"):
                            bOK = True
                            break
                      if bOK: break

                    if bOK:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Buildings/button_camel_stable.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 4, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return

                    else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_camel_stable_gray.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 5, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return
              # not in city
              else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_camel_stable_gray.dds", 0, WidgetTypes.WIDGET_GENERAL, 721, 6, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          return

            # ----------
            # PAE - Cultist cannot spread cult due to civic (749:1) => Show INFO Button !
            if bCity:
              Cultists = []
              Cultists.append(gc.getInfoTypeForString("UNIT_EXECUTIVE_1"))
              Cultists.append(gc.getInfoTypeForString("UNIT_EXECUTIVE_2"))
              Cultists.append(gc.getInfoTypeForString("UNIT_EXECUTIVE_3"))
              if iUnitType in Cultists:
                if pUnitOwner.isCivic(gc.getInfoTypeForString("CIVIC_ANIMISM")):
                  screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_cult_grey.dds", 0, WidgetTypes.WIDGET_GENERAL, 749, 1, False )
                  screen.show( "BottomButtonContainer" )
                  iCount = iCount + 1

# --------------------

# Veteran -> Eliteunit (netMessage 705) - Belobigung
# Auch in GameUtils fuer die KI aendern !
            if pUnit.canMove():

              # Kampferfahren (Streitwagen)
              if iUnitType == gc.getInfoTypeForString("UNIT_CHARIOT"):
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")):
                    screen.appendMultiListButton( "BottomButtonContainer", ",Art/Interface/Buttons/Units/Chariot_WarChariot.dds,Art/Interface/Buttons/Unit_Resource_Atlas.dds,5,7", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_WAR_CHARIOT"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

              # Rome: Roman praetorians ->  Cohors Praetoria | Cohors Urbana | Equites LH
              # Sollte ueber XML gehen. Auch wenn iCost -1
              #if iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN"):
              #    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PRINCIPAT")):
              #      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_praetorian2.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PRAETORIAN2"), False )
              #      screen.show( "BottomButtonContainer" )
              #      iCount = iCount + 1
              #    elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_FEUERWEHR")):
              #      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_cohortes_urbanae.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ROME_COHORTES_URBANAE"), False )
              #      screen.show( "BottomButtonContainer" )
              #      iCount = iCount + 1
              #    elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_LORICA_SEGMENTATA")):
              #      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_cohors_equitata.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2"), False )
              #      screen.show( "BottomButtonContainer" )
              #      iCount = iCount + 1

              # Veterans ++++++++++++++++++++++++++++
              if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")):

               # ROME
               if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ROME") \
               or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):

                 if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_ARCHER"):

                   # Sagittarii (Reflex) -> Arquites
                   if iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_ROME") :
                     if pTeam.isHasTech(gc.getInfoTypeForString("TECH_LORICA_SEGMENTATA")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_arquites_legionis.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ARCHER_LEGION"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Arquites -> Equites Sagittarii (Horse Archer)
                   elif iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_LEGION") :
                     if pTeam.isHasTech(gc.getInfoTypeForString("TECH_HORSE_ARCHER")):
                       screen.appendMultiListButton( "BottomButtonContainer", ",Art/Interface/Buttons/Units/HorseArcher.dds,Art/Interface/Buttons/Warlords_Atlas_1.dds,1,11", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1

                 elif pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):

                   # Elite Cohors Equitata -> Equites Singulares Augusti
                   if iUnitType == gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2") :
                     if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_praetorian2_horse.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1

                 else:

                   # Elite Limitanei -> Imperial Guard
                   if iUnitType == gc.getInfoTypeForString("UNIT_ROME_LIMITANEI"):
                     if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_limit_garde.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ROME_LIMITANEI_GARDE"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Elite Comitatenses -> Palatini
                   elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES") or iUnitType == gc.getInfoTypeForString("UNIT_ROME_COMITATENSES2"):
                     if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_palatini.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ROME_PALATINI"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Elite Cohorte praetoriae + Cohors urbana -> Praetorian Garde (max 3)
                   elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2") or iUnitType == gc.getInfoTypeForString("UNIT_ROME_COHORTES_URBANAE"):
                     if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
                      if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_PRAETORIAN3")) < 3:
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_praetorian3.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PRAETORIAN3"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Legion or Legion 2 -> Praetorians
                   elif iUnitType == gc.getInfoTypeForString("UNIT_LEGION") or iUnitType == gc.getInfoTypeForString("UNIT_LEGION2"):
                     # obsolete with Marching/Border Army
                     if not pTeam.isHasTech(gc.getInfoTypeForString("TECH_GRENZHEER")):
                      # Rang: Immunes
                      if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_RANG_ROM_3")):
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_praetorian.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PRAETORIAN"), False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1
                   # Elite Palatini or Clibanari or Cataphracti -> Scholae
                   elif iUnitType == gc.getInfoTypeForString("UNIT_ROME_PALATINI") \
                   or iUnitType == gc.getInfoTypeForString("UNIT_CLIBANARII_ROME") or iUnitType == gc.getInfoTypeForString("UNIT_CATAPHRACT_ROME"):
                     if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")):
                      if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ROME_SCHOLAE")) < 3:
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_scholae.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ROME_SCHOLAE"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Triari -> Praetorians
                   elif iUnitType == gc.getInfoTypeForString("UNIT_TRIARII2") and  pTeam.isHasTech(gc.getInfoTypeForString("TECH_BERUFSSOLDATEN")):
                     # obsolete with Marching/Border Army
                     if not pTeam.isHasTech(gc.getInfoTypeForString("TECH_GRENZHEER")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_praetorian.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PRAETORIAN"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Principes or Hastati -> Triarii
                   elif iUnitType == gc.getInfoTypeForString("UNIT_PRINCIPES2") \
                   or iUnitType == gc.getInfoTypeForString("UNIT_HASTATI2") :
                     if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
                       screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_triarii2.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_TRIARII2"), False )
                       screen.show( "BottomButtonContainer" )
                       iCount = iCount + 1
                   # Hasta Warrior -> Celeres
                   elif iUnitType == gc.getInfoTypeForString("UNIT_HASTATI1") :
                     #if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"):
                     screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_celeres.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_CELERES"), False )
                     screen.show( "BottomButtonContainer" )
                     iCount = iCount + 1


               # GREEKS
               elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") \
               or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
               or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") \
               or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
                # Hoplit -> Elite Hoplit
                if iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT") :
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_phalanx.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ELITE_HOPLIT"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                # Reflex -> Elite
                elif iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK") :
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_archer_greek.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

               # SPARTA
               if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA") or  pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE"):
                # Sparta Hoplit -> Elite Hoplit
                if iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT_SPARTA") :
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_spartaner2.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_SPARTAN"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

               # KARTHAGO
               elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CARTHAGE"):
                 if iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT_CARTHAGE") :
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_sacred_carthage.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

               # PERSIA
               elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PERSIA"):
                # Unsterblich -> Garde
                if iUnitType == gc.getInfoTypeForString("UNIT_UNSTERBLICH") :
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_immortalguard.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_UNSTERBLICH_2"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                # Unsterblichen Garde || Pezoi -> Apfeltraeger
                if iUnitType == gc.getInfoTypeForString("UNIT_UNSTERBLICH_2") or iUnitType == gc.getInfoTypeForString("UNIT_HOPLIT_PERSIA") :
                   if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE2")) < 3:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_persian_pezoi.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_APFELTRAEGER"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

               # MACEDONIA
               elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"):
                # Reflex -> Elite
                if iUnitType == gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK") :
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_archer_greek.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ARCHER_REFLEX_GREEK2"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                #  Hypaspist oder Pezhetairoi -> Argyraspidai
                elif iUnitType == gc.getInfoTypeForString("UNIT_HYPASPIST") \
                or iUnitType == gc.getInfoTypeForString("UNIT_SARISSA_MACEDON") :
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
                   if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE2")) < 3:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/macedon_garde.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ARGYRASPIDAI"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                #  Argyraspidai -> Argyraspidai 2 (Silberschild)
                elif iUnitType == gc.getInfoTypeForString("UNIT_ARGYRASPIDAI") :
                  if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ARGYRASPIDAI2")) < 3:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/macedon_argy.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_ARGYRASPIDAI2"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

               # EGYPT
               elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
                #  Gaufuerst -> Pharaonengarde
                if iUnitType == gc.getInfoTypeForString("UNIT_GAUFUERST") :
                  if gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getCivilizationUnits(gc.getInfoTypeForString("UNITCLASS_ELITE1")) < 3:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_pharaonengarde.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_PHARAONENGARDE"), False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1


               # Schildtraeger
               if iUnitType == gc.getInfoTypeForString("UNIT_SCHILDTRAEGER") :

                  if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_EGYPT"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_gaufuerst.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_GAUFUERST"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

                  elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_NUBIA"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_nubia_kuschit.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_NUBIAFUERST"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                    if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_CELT") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GALLIEN") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BRITEN") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_stammesfuerst.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_STAMMESFUERST"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_DAKER"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_dacianchief.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_FUERST_DAKER"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_israel_maccaber.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_MACCABEE"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):
                    if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_PHON") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ASSYRIA") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_BABYLON") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ISRAEL") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SUMERIA"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_syriengarde.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_SYRIAN_GARDE"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

               # Axeman
               elif iUnitType == gc.getInfoTypeForString("UNIT_AXEMAN2") :
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):

                    if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_axeman.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

               # Spearman
               elif iUnitType == gc.getInfoTypeForString("UNIT_SPEARMAN"):
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_ARMOR")):

                    # INDIA
                    if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_inder_radscha.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_RADSCHA"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    # GREEKS
                    elif pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GREECE") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_ATHENS") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_THEBAI") \
                    or pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_SPARTA"):
                      # Spearman -> Hoplit
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_hoplit_peze.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_HOPLIT"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_EISENWAFFEN")):

                    if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_GERMANEN"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_harii.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_GERMAN_HARIER"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

               # Swordsman
               elif iUnitType == gc.getInfoTypeForString("UNIT_SWORDSMAN"):

                  if pUnit.getCivilizationType() == gc.getInfoTypeForString("CIVILIZATION_INDIA"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_unit_nayar.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_INDIAN_NAYAR"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

               # Steppenreiter -> Geissel Gottes
               elif iUnitType == gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Units/button_heavy_horseman.dds", 0, WidgetTypes.WIDGET_GENERAL, 705, gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN_HUN"), False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1


               # Allgemein Veteran -> Reservist
               if bCity:
                 if pCity.getOwner() == pUnit.getOwner():
                   if pTeam.isHasTech(gc.getInfoTypeForString("TECH_RESERVISTEN")):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_reservist.dds", 0, WidgetTypes.WIDGET_GENERAL, 724, 724, False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

              # if Veteran -> Elite / Reservist -----------------------

              # Unit Rang Promos
              if CvUtil.getScriptData(pUnit, ["P", "t"]) == "RangPromoUp":
                 if pUnitOwner.getGold() < 100: bCapital = False
                 screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Rang/button_rang_up.dds", 0, WidgetTypes.WIDGET_GENERAL, 751, pUnit.getOwner(), bCapital )
                 screen.show( "BottomButtonContainer" )
                 iCount = iCount + 1


            # if can move


# --------------------
# BEGIN Horse <-> Unit
            if pUnit.canMove():
              bButtonDown = False
              bButtonUp = False
              bSearchPlot = False

              # Horse -> Unit
              if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):

                if iUnitType == gc.getInfoTypeForString("UNIT_AUXILIAR_HORSE"): bButtonDown = True
                elif iUnitType == gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"): bButtonDown = True
                #elif iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"): bButtonDown = True
                elif iUnitType == gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"): bButtonDown = True
                elif iUnitType == gc.getInfoTypeForString("UNIT_MOUNTED_SCOUT"): bButtonDown = True

              # Unit -> Horse
              elif pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_RECON"):
                if iUnitType == gc.getInfoTypeForString("UNIT_SCOUT") or iUnitType == gc.getInfoTypeForString("UNIT_SCOUT_GREEK"):
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING")):
                    bSearchPlot = True
              elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_HORSEBACK_RIDING_2")):

                lUnitAuxiliar = []
                lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR"))
                lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_ROME"))
                lUnitAuxiliar.append(gc.getInfoTypeForString("UNIT_AUXILIAR_MACEDON"))

                if iUnitType in lUnitAuxiliar \
                or iUnitType == gc.getInfoTypeForString("UNIT_FOEDERATI") \
                or iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE") :
                  #or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN") \
                  #or iUnitType == gc.getInfoTypeForString("UNIT_PRAETORIAN2") \


                  if iUnitType in lUnitAuxiliar and pTeam.isHasTech(gc.getInfoTypeForString("TECH_HUFEISEN")): bSearchPlot = True
                  elif iUnitType == gc.getInfoTypeForString("UNIT_FOEDERATI"):
                    TechHorse3 = gc.getInfoTypeForString("TECH_HUFEISEN")
                    if pTeam.isHasTech(TechHorse3): bSearchPlot = True
                  elif iUnitType == gc.getInfoTypeForString("UNIT_SACRED_BAND_CARTHAGE"):
                    TechHorse3 = gc.getInfoTypeForString("TECH_HUFEISEN")
                    TechHorse4 = gc.getInfoTypeForString("TECH_KETTENPANZER")
                    if pTeam.isHasTech(TechHorse3) and pTeam.isHasTech(TechHorse4): bSearchPlot = True


              # Pferd suchen
              if bSearchPlot:
                    pPlot = gc.getMap().plot( g_pSelectedUnit.getX(), g_pSelectedUnit.getY() )
                    UnitHorse = gc.getInfoTypeForString('UNIT_HORSE')
                    for iUnit in range (pPlot.getNumUnits()):
                      if pPlot.getUnit(iUnit).getUnitType() == UnitHorse and pPlot.getUnit(iUnit).getOwner() == pUnit.getOwner() and pPlot.getUnit(iUnit).canMove():
                        bButtonUp = True
                        break

              # Horse -> Swordsman
              if bButtonDown:
                screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_HORSE_DOWN").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 666, 666, False )
                screen.show( "BottomButtonContainer" )
                iCount = iCount + 1
              # Swordsman -> Horse
              if bButtonUp:
                screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_HORSE_UP").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 667, 667, False )
                screen.show( "BottomButtonContainer" )
                iCount = iCount + 1
            # Ende Horse <-> Unit

# ------------------
# BEGIN Merchant trade/cultivation/collect Bonus (738-741) (Boggy)
            if pUnit.canMove(): # and not pUnit.hasMoved():
                pPlot = g_pSelectedUnit.plot()
                if iUnitType in PAE_Trade.lCultivationUnits:
                  if pPlot.getOwner() == pUnit.getOwner():
                    iIsCity = pPlot.isCity()
                    eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
                    # Collect bonus from plot or city
                    ePlotBonus = pPlot.getBonusType(pUnit.getOwner()) # Invisible bonuses can NOT be collected
                    # remove from plot => iData2 = 0. 1 = charge all goods without removing. Nur bei leerem Karren.
                    if eBonus == -1:
                        if ePlotBonus != -1 and ePlotBonus in PAE_Trade.lCultivatable:
                            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_COLLECT").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 739, 0, True )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                        if iIsCity:
                            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_BUY").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 739, 1, True )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                    else:
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_COLLECT_IMPOSSIBLE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 739, 739, False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    # Cultivate bonus onto plot
                    if eBonus != -1 and PAE_Trade.isBonusCultivatable(pUnit):
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_CULTIVATE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 738, 738, iIsCity )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                # Buy / sell goods in cities (domestic or foreign)
                if iUnitType in PAE_Trade.lTradeUnits:
                  if pPlot.isCity():
                    eBonus = CvUtil.getScriptData(pUnit, ["b"], -1)
                    # Sell
                    if eBonus != -1:
                      iPrice = PAE_Trade.calculateBonusSellingPrice(pUnit, pPlot.getPlotCity())
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_SELL").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 741, iPrice, False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    # Buy
                    else:
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_BUY").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 740, 740, False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                    # Automated Trade Route
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_AUTO_START").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 744, 744, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
            # Cancel automated trade route
            if iUnitType in PAE_Trade.lTradeUnits:
              bTradeRouteActive = int(CvUtil.getScriptData(pUnit, ["autA"], 0))
              if bTradeRouteActive:
                screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TRADE_AUTO_STOP").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 748, 748, False )
                screen.show( "BottomButtonContainer" )
                iCount = iCount + 1

# END Merchant -----

# --------- Einheiten in einer Stadt
            if gc.getMap().plot( g_pSelectedUnit.getX(), g_pSelectedUnit.getY() ).isCity():
              pCity = gc.getMap().plot( g_pSelectedUnit.getX(), g_pSelectedUnit.getY() ).getPlotCity()

              # In der eigenen Stadt
              if pCity.getOwner() == pUnit.getOwner():

                pTeam = gc.getTeam(pUnitOwner.getTeam())

                # Provinzstatthalter / Tribut
                # Soeldner anheuern / Mercenaries (in der eigenen Stadt)
                iBuilding1 = gc.getInfoTypeForString("BUILDING_PROVINZPALAST")
                iBuilding2 = gc.getInfoTypeForString("BUILDING_SOELDNERPOSTEN")
                if pCity.isHasBuilding(iBuilding1) or  pCity.isHasBuilding(iBuilding2):

                  # Ist mind. 1 Einheit immobile oder beschaeftigt, so geht kein Tribut (damit man nicht mehr pro Runde durchfuehren kann)
                  bTribut = True
                  iOwner = pUnit.getOwner()
                  pPlot = pCity.plot()
                  iNumUnits = pPlot.getNumUnits()
                  if iNumUnits > 0:
                    for k in range (iNumUnits):
                      if iOwner == pPlot.getUnit(k).getOwner():
                        if not pPlot.getUnit(k).canMove():
                          bTribut = False
                          break

                  # Provinzstatthalter / Tribut - Patch 4: und nur moeglich, wenn Stadtzufriedenheit <= :)
                  if bTribut and pCity.isHasBuilding(iBuilding1):
                   if not pTeam.isHasTech(gc.getInfoTypeForString("TECH_POLYARCHY")) and pCity.happyLevel() - pCity.unhappyLevel(0) <= 0:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_statthalter_main.dds", 0, WidgetTypes.WIDGET_GENERAL, 737, 737, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                  # Soeldner anheuern / Mercenaries (in der eigenen Stadt)
                  if bTribut and pCity.isHasBuilding(iBuilding2):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_MERCENARIES_CITYBUTTON").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 707, 707, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                # --------------------------------------------------------

                # Sklaven in der Stadt
                if iUnitType == gc.getInfoTypeForString("UNIT_SLAVE"):

                  # Sklaven zu Feld oder Bergwerksklaven
                  bFarms = False
                  lFarms = []
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_PASTURE"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_FARM"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"))
                  lFarms.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM5"))

                  bMines = False
                  lMines = []
                  lMines.append(gc.getInfoTypeForString("IMPROVEMENT_MINE"))
                  lMines.append(gc.getInfoTypeForString("IMPROVEMENT_QUARRY"))

                  iX = pCity.getX()
                  iY = pCity.getY()
                  for x in range(5):
                          for y in range(5):
                            loopPlot = gc.getMap().plot(iX + x - 2, iY + y - 2)
                            if loopPlot != None and not loopPlot.isNone():
                              # Plot besetzt?
                              if pCity.canWork(loopPlot):
                                if loopPlot.getImprovementType() in lFarms: bFarms = True
                                elif loopPlot.getImprovementType() in lMines: bMines = True
                          # Schleife vorzeitig beenden
                          if bFarms and bMines: break

                  # Sklave -> SPECIALIST_SLAVE_FOOD
                  if bFarms:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2farm.dds", 0, WidgetTypes.WIDGET_GENERAL, 734, 1, True )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                  else:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2farm_gr.dds", 0, WidgetTypes.WIDGET_GENERAL, 734, 1, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                  # Sklave -> SPECIALIST_SLAVE_PROD
                  if bMines:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2mine.dds", 0, WidgetTypes.WIDGET_GENERAL, 734, 2, True )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                  else:
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2mine_gr.dds", 0, WidgetTypes.WIDGET_GENERAL, 734, 2, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                  # ------------

                  # Sklaven -> Gladiator
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GLADIATOR")):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_GLADIATOR").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 669, 669, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                  # Sklaven -> Schule   (Gymnasion hat bereits +5 Forschung)
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KUNST")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_SCHULE')
                  if pCity.isHasBuilding(iBuilding1):
                      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_RESEARCH, iBuilding1)
                      if iCulture < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SCHULE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 679, 679, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> Schule   (Gymnasion hat bereits +5 Forschung)
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KUNST")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_LIBRARY')
                  if pCity.isHasBuilding(iBuilding1):
                      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_RESEARCH, iBuilding1)
                      if iCulture < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2library.dds", 0, WidgetTypes.WIDGET_GENERAL, 729, 729, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> Bordell / Freudenhaus
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_SYNKRETISMUS")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_BORDELL')
                  if pCity.isHasBuilding(iBuilding1):
                      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
                      if iCulture < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_BORDELL").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 668, 668, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> Theater
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_DRAMA")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_THEATER')
                  if pCity.isHasBuilding(iBuilding1):
                      iCulture = pCity.getBuildingCommerceByBuilding(CommerceTypes.COMMERCE_CULTURE, iBuilding1)
                      if iCulture < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_THEATRE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 670, 670, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> Manufaktur
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANUFAKTUREN")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_CORP3')
                  if pCity.isHasBuilding(iBuilding1):
                      iProd = pCity.getBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 0)
                      if iProd < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_MANUFAKTUR_0").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 680, 680, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                      iProd = pCity.getBuildingYieldChange(gc.getBuildingInfo(iBuilding1).getBuildingClassType(), 1)
                      if iProd < 5:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_MANUFAKTUR_1").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 681, 681, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> Palast
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_PALACE')
                  if pCity.isHasBuilding(iBuilding1):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SLAVES_PALACE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 692, 692, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                  # Sklaven -> Tempel
                  iBuilding1 = gc.getInfoTypeForString("BUILDING_ZORO_TEMPLE")
                  iBuilding2 = gc.getInfoTypeForString("BUILDING_PHOEN_TEMPLE")
                  iBuilding3 = gc.getInfoTypeForString("BUILDING_SUMER_TEMPLE")
                  iBuilding4 = gc.getInfoTypeForString("BUILDING_ROME_TEMPLE")
                  iBuilding5 = gc.getInfoTypeForString("BUILDING_GREEK_TEMPLE")
                  iBuilding6 = gc.getInfoTypeForString("BUILDING_CELTIC_TEMPLE")
                  iBuilding7 = gc.getInfoTypeForString("BUILDING_EGYPT_TEMPLE")
                  iBuilding8 = gc.getInfoTypeForString("BUILDING_NORDIC_TEMPLE")
                  if pCity.isHasBuilding(iBuilding1) or pCity.isHasBuilding(iBuilding2) or pCity.isHasBuilding(iBuilding3) \
                  or pCity.isHasBuilding(iBuilding4) or pCity.isHasBuilding(iBuilding5) or pCity.isHasBuilding(iBuilding6) \
                  or pCity.isHasBuilding(iBuilding7) or pCity.isHasBuilding(iBuilding8):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SLAVES_TEMPLE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 693, 693, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                  # Sklaven -> Feuerwehr
                  #if pTeam.isHasTech(gc.getInfoTypeForString("TECH_FEUERWEHR")):
                  iBuilding1 = gc.getInfoTypeForString('BUILDING_FEUERWEHR')
                  if pCity.isHasBuilding(iBuilding1):
                      iHappyiness = pCity.getBuildingHappyChange (gc.getBuildingInfo(iBuilding1).getBuildingClassType())
                      if iHappyiness < 3:
                        screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SLAVES_FEUERWEHR").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 696, 696, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

                  # Sklaven -> An den Sklavenmarkt verkaufen
                  iBuilding1 = gc.getInfoTypeForString("BUILDING_SKLAVENMARKT")
                  if pCity.isHasBuilding(iBuilding1):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SELL_SLAVES").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 694, 694, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                # ---- Ende Sklaven (eigene Stadt)


                # Kauf einer edlen Ruestung (eigene Stadt)
                if pTeam.isHasTech(gc.getInfoTypeForString("TECH_ARMOR")):
                  iPromo = gc.getInfoTypeForString("PROMOTION_EDLE_RUESTUNG")
                  if not pUnit.isHasPromotion(iPromo):
                    iCombatArray = []
                    iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_NAVAL"))
                    iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SIEGE"))
                    iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_RECON"))
                    iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_HEALER"))
                    iCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_ARCHER"))
                    iCombatArray.append(gc.getInfoTypeForString("NONE"))
                    if pUnit.getUnitCombatType() not in iCombatArray and pUnit.getUnitCombatType() > 0:
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
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
                      iUnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
                      if pUnit.getUnitType() not in iUnitArray:
                        iBuilding1 = gc.getInfoTypeForString("BUILDING_FORGE")
                        bonus1 = gc.getInfoTypeForString("BONUS_OREICHALKOS")
                        bonus2 = gc.getInfoTypeForString("BONUS_MESSING")
                        iPromoPrereq = gc.getInfoTypeForString("PROMOTION_COMBAT5")

                        if pCity.isHasBuilding(iBuilding1) and (pCity.hasBonus(bonus1) or pCity.hasBonus(bonus2)) and pUnit.isHasPromotion(iPromoPrereq):
                          iCost = gc.getUnitInfo(pUnit.getUnitType()).getCombat() * 12
                          if gc.getPlayer(pUnit.getOwner()).getGold() >= iCost:
                            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_EDLE_RUESTUNG").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 699, iCost, True )
                          else:
                            screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_EDLE_RUESTUNG2").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 699, iCost, False )
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_EDLE_RUESTUNG2").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 699, -1, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1
                # Ende Kauf einer Edlen Rüstung

                # Terrain Promos - Ausbildner / Trainer (in City) ID 719
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_WOODSMAN5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_FOREST")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_GUERILLA5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_HILLS")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_JUNGLE5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_JUNGLE")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_SUMPF5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_SWAMP")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DESERT5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_DESERT")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_RAIDER5") ):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_CITY_A")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_CITY_GARRISON5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_CITY_D")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_PILLAGE5")):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_PILLAGE")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_NAVIGATION4")) and pCity.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
                  iBuilding = gc.getInfoTypeForString("BUILDING_PROMO_NAVI")
                  if not pCity.isHasBuilding(iBuilding):
                    screen.appendMultiListButton( "BottomButtonContainer", gc.getBuildingInfo(iBuilding).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 719, iBuilding, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1
                # Ende Ausbildung Promos

                # Auswanderer / Emigrant -> in der eigenen Stadt
                if iUnitType == gc.getInfoTypeForString("UNIT_EMIGRANT"):
                  # Stadt auflösen / disband city
                  if pUnitOwner.getNumCities() > 1 and pCity.getPopulation() < 3 and not pCity.isCapital():
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_DISBAND_CITY").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 673, 673, True )
                  else:
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_DISBAND_CITY2").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 673, 673, False )
                  screen.show( "BottomButtonContainer" )
                  iCount = iCount + 1
                  # zuwandern / immigrate
                  screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_EMIGRANT").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 672, 672, False )
                  screen.show( "BottomButtonContainer" )
                  iCount = iCount + 1
                # Siedler -> in der eigenen Stadt
                elif iUnitType == gc.getInfoTypeForString("UNIT_SETTLER"):
                  # Stadt auflösen / disband city
                  if pUnitOwner.getNumCities() > 1 and pCity.getPopulation() < 3 and not pCity.isCapital():
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_DISBAND_CITY").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 673, 673, True )
                    iCount = iCount + 1

                # Goldkarren / Treasure / Beutegold -> in die Hauptstadt
                if iUnitType == gc.getInfoTypeForString("UNIT_GOLDKARREN"):
                  #pUnitOwner = gc.getPlayer(pUnit.getOwner())
                  #pCapital = pUnitOwner.getCapitalCity()
                  #if pCity.getID() == pCapital.getID():
                  if pCity.isCapital():
                    # Gold in die Schatzkammer bringen
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_GOLDKARREN").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 677, 677, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                # Reservist -> Veteran (in der eigenen Stadt)
                iReservists = pCity.getFreeSpecialistCount(19) # SPECIALIST_RESERVIST
                if iReservists >= 1:
                   screen.appendMultiListButton( "BottomButtonContainer", ",Art/Interface/MainScreen/CityScreen/Great_Engineer.dds,Art/Interface/Buttons/Warlords_Atlas_2.dds,7,6", 0, WidgetTypes.WIDGET_GENERAL, 725, 725, False )
                   screen.show( "BottomButtonContainer" )
                   iCount = iCount + 1

                # Bonusverbreitung
                if iUnitType == gc.getInfoTypeForString("UNIT_SUPPLY_FOOD"):
                   # Nahrung abliefern
                   screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_getreide2town.dds", 0, WidgetTypes.WIDGET_GENERAL, 727, 727, False )
                   screen.show( "BottomButtonContainer" )
                   iCount = iCount + 1
                   # Bonus verbreiten
                   #screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_bonusverbreitung.dds", 0, WidgetTypes.WIDGET_GENERAL, 726, 726, False )
                   #screen.show( "BottomButtonContainer" )
                   #iCount = iCount + 1

                # Karten zeichnen (innerhalb eigene Stadt)
                #if pCity.isCapital():
                if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_RECON"):
                 if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KARTEN")):
                   screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Techs/button_tech_karten.dds", 0, WidgetTypes.WIDGET_GENERAL, 728, 728, False )
                   screen.show( "BottomButtonContainer" )
                   iCount = iCount + 1

                # Release slaves
                if pUnit.isMilitaryHappiness():
                   iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR
                   iCitySlavesHaus = pCity.getFreeSpecialistCount(16) # SPECIALIST_SLAVE
                   iCitySlavesFood = pCity.getFreeSpecialistCount(17) # SPECIALIST_SLAVE_FOOD
                   iCitySlavesProd = pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE_PROD
                   iCitySlaves = iCitySlavesHaus + iCitySlavesFood + iCitySlavesProd

                   if iCityGlads + iCitySlaves > 0:
                     screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave_release.dds", 0, WidgetTypes.WIDGET_GENERAL, 730, 730, True )
                     screen.show( "BottomButtonContainer" )
                     iCount = iCount + 1

              # ---- ENDE if Einheit -> in der eigenen Stadt

              # ++++++++++++++++++++++++++++++++
              # In eigenen und fremden Städten:
              # ++++++++++++++++++++++++++++++++

              # Verkauf von Einheiten
              if pUnit.isMilitaryHappiness():
                # Soll in jeder Stadt mit Soeldnerposten verkauft werden
                # Unit -> An den Soeldnerposten verkaufen
                iBuilding1 = gc.getInfoTypeForString("BUILDING_SOELDNERPOSTEN")
                if pCity.isHasBuilding(iBuilding1):
                    iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost() / 2
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_SELL_UNITS").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 695, iCost, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

                # Einheit segnen / bless unit (PAE V Patch 4)
                iPromo = gc.getInfoTypeForString("PROMOTION_BLESSED")
                if not pUnit.isHasPromotion(iPromo):
                  iBuilding1 = gc.getInfoTypeForString("BUILDING_CHRISTIAN_CATHEDRAL")
                  iBuilding2 = gc.getInfoTypeForString("BUILDING_HAGIA_SOPHIA")
                  if pCity.isHasBuilding(iBuilding1) or pCity.isHasBuilding(iBuilding2):
                    screen.appendMultiListButton( "BottomButtonContainer","Art/Interface/Buttons/Promotions/button_promo_blessed.dds", 0, WidgetTypes.WIDGET_GENERAL, 752, 0, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1


              # Kauf von Wellen-Oil -----------
              if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KUESTE")):
                iPromo = gc.getInfoTypeForString("PROMOTION_OIL_ON_WATER")
                if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL") and not pUnit.isHasPromotion(iPromo):
                  bonus1 = gc.getInfoTypeForString("BONUS_OLIVES")
                  iPromo2 = gc.getInfoTypeForString("PROMOTION_COMBAT2")
                  if pUnit.isHasPromotion(iPromo2) and pCity.hasBonus(bonus1):
                    iCost = PyInfo.UnitInfo(pUnit.getUnitType()).getProductionCost()
                    if iCost <= 0: iCost = 180
                    if gc.getPlayer(pUnit.getOwner()).getGold() >= iCost:
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_PROMO_OIL").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 701, iCost, True )
                    else:
                      screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_PROMO_OIL2").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 701, iCost, False )
                  else:
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_PROMO_OIL2").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 701, -1, False )
                  screen.show( "BottomButtonContainer" )
                  iCount = iCount + 1




            # ---- ENDE if Einheit in einer Stadt --------
            else:
            # ---- Einheit nicht in der Stadt

              # Trojanisches Pferd vor der Stadt
              if iUnitType == gc.getInfoTypeForString("UNIT_TROJAN_HORSE"):
                iX = g_pSelectedUnit.getX()
                iY = g_pSelectedUnit.getY()
                for x in range(3):
                  for y in range(3):
                    loopPlot = gc.getMap().plot(iX + x - 1, iY + y - 1)
                    if loopPlot != None and not loopPlot.isNone():
                      if loopPlot.isCity():
                        loopCity = loopPlot.getPlotCity()
                        if loopCity.getOwner() != pUnit.getOwner():
                          if gc.getTeam(pUnit.getOwner()).isAtWar(gc.getPlayer(loopCity.getOwner()).getTeam()):
                            iDefense = loopCity.getDefenseModifier(0)
                            if iDefense > 50:
                              # Stadtverteidigung auf 0 setzen
                              screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_TROJAN_HORSE").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 697, 697, False )
                              screen.show( "BottomButtonContainer" )
                              iCount = iCount + 1

              # Pillage Road
              if pUnit.isMilitaryHappiness():
                pPlot = gc.getMap().plot( pUnit.getX(), pUnit.getY() )
                if pPlot.getRouteType() > -1:
                  if pPlot.getOwner() < 0 or pPlot.getOwner() == pUnit.getOwner() or gc.getTeam(pPlot.getOwner()).isAtWar(pUnitOwner.getTeam()):
                    # Pillage Road
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_PILLAGE_ROAD").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 700, 700, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1

              # Piraten-Feature
              # Nur für bestimmte Nationen (ab PAE V Patch 3)
              if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_PIRACY")):

                  lCivPirates = []
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_BERBER"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_ETRUSCANS"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_HETHIT"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_IBERER"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_ILLYRIA"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_LIBYA"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_LYDIA"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_NUBIA"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_NUMIDIA"))
                  lCivPirates.append(gc.getInfoTypeForString("CIVILIZATION_VANDALS"))

                  if pUnit.getCivilizationType() in lCivPirates:
                    # Pirat -> normal
                    UnitArray1 = []
                    UnitArray1.append(gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"))
                    UnitArray1.append(gc.getInfoTypeForString("UNIT_PIRAT_BIREME"))
                    UnitArray1.append(gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"))
                    UnitArray1.append(gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"))
                    # Normal -> Pirat
                    UnitArray2 = []
                    UnitArray2.append(gc.getInfoTypeForString("UNIT_KONTERE"))
                    UnitArray2.append(gc.getInfoTypeForString("UNIT_BIREME"))
                    UnitArray2.append(gc.getInfoTypeForString("UNIT_TRIREME"))
                    UnitArray2.append(gc.getInfoTypeForString("UNIT_LIBURNE"))
                    if pUnit.getUnitType() in UnitArray1 or pUnit.getUnitType() in UnitArray2:
                      if pUnit.hasCargo():
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_pirat2.dds", 0, WidgetTypes.WIDGET_GENERAL, 722, 3, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1
                      else:
                        if pUnit.getUnitType() in UnitArray1:
                          screen.appendMultiListButton( "BottomButtonContainer", gc.getCivilizationInfo(pUnitOwner.getCivilizationType()).getButton(), 0, WidgetTypes.WIDGET_GENERAL, 722, 2, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                        elif pUnit.getUnitType() in UnitArray2:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_pirat.dds", 0, WidgetTypes.WIDGET_GENERAL, 722, 1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

              # Limes
              if iUnitType == gc.getInfoTypeForString("UNIT_LEGION") or iUnitType == gc.getInfoTypeForString("UNIT_LEGION2") \
              or iUnitType == gc.getInfoTypeForString("UNIT_AUXILIAR_ROME") or iUnitType == gc.getInfoTypeForString("UNIT_ROME_LIMITANEI"):
                if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_LIMES")):
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Buildings/button_building_limes.dds", 0, WidgetTypes.WIDGET_GENERAL, 733, -1, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

              # Handelsposten
              #if pUnit.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_WORKER") or pUnit.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_SLAVE"):
              if pUnit.getUnitClassType() == gc.getInfoTypeForString("UNITCLASS_TRADE_MERCHANT"):
                # Update: auch in eigenen Grenzen anzeigen (zB fuer Inseln), aber nur wenn nicht bereits was drauf steht
                #if pUnit.plot().getOwner() == -1:
                pPlot = pUnit.plot()
                if pPlot.getImprovementType() == -1:
                  if pPlot.getOwner() == -1 or pPlot.getOwner() == pUnit.getOwner():
                    if pPlot.getBonusType(-1) != -1:
                      if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_WARENHANDEL")):
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Builds/button_build_handelsposten.dds", 0, WidgetTypes.WIDGET_GENERAL, 736, -1, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

              # Sklaven ausserhalb der Stadt
              if iUnitType == gc.getInfoTypeForString("UNIT_SLAVE"):
                pPlot = pUnit.plot()
                if pPlot.getOwner() == pUnit.getOwner():
                  lLatifundien = []
                  lLatifundien.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM1"))
                  lLatifundien.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM2"))
                  lLatifundien.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM3"))
                  lLatifundien.append(gc.getInfoTypeForString("IMPROVEMENT_LATIFUNDIUM4"))
                  if pPlot.getImprovementType() in lLatifundien:
                    if pPlot.getUpgradeTimeLeft (pPlot.getImprovementType(), pUnit.getOwner()) > 1:
                        screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_slave2latifundium.dds", 0, WidgetTypes.WIDGET_GENERAL, 753, -1, False )
                        screen.show( "BottomButtonContainer" )
                        iCount = iCount + 1

            # Ende ausserhalb der Stadt --------


            # Innerhalb und ausserhalb der Stadt -------------------------------


            # FORMATIONEN / FORMATIONS (in oder ausserhalb der Stadt ab PAE V Patch 2) --------------------------------
            if pUnit.canMove() or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")):

              if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")):
                  bFormationUndo = True
              else:
                  bFormationUndo = False

              # PAE V Patch 2: disabled for fights on his own units
              if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")):

                lMelee = [gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"),gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"),gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN")]
                lArcher = [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]

                pPlot = pUnit.plot()

                FortArray = []
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_TURM2"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_FORT"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_FORT2"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_HANDELSPOSTEN"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES1"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES3"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES4"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES5"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES6"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES7"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES8"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES9"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_1"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_2"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_3"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_4"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_5"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_6"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_7"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_8"))
                FortArray.append(gc.getInfoTypeForString("IMPROVEMENT_LIMES2_9"))
                iImp = pPlot.getImprovementType()

                #FeatureArray = []
                #FeatureArray.append(gc.getInfoTypeForString("FEATURE_FOREST"))
                #FeatureArray.append(gc.getInfoTypeForString("FEATURE_DICHTERWALD"))
                #iFeat = pPlot.getFeatureType()

                # in Festungen (keine Formationen erlauben, ausser PROMOTION_FORM_FORTRESS)
                if iImp in FortArray:
                  # Besitzerabfrage
                  if pPlot.getOwner() == pUnit.getOwner() or pPlot.getOwner() == -1:
                    # Nur Melee
                    if pUnit.getUnitCombatType() in lMelee:
                        # Festungsformation
                        if PyInfo.UnitInfo(pUnit.getUnitType()).getMoves() == 1: iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS")
                        else: iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FORTRESS2")
                        if not pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_fortress.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                # ausserhalb von Festungen
                #elif iFeat not in FeatureArray:
                else:

                  # Naval
                  if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
                    if gc.getTeam(pUnitOwner.getTeam()).isHasTech(gc.getInfoTypeForString("TECH_LOGIK")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_WORKBOAT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KILIKIEN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_KONTERE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_BIREME"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_TRIREME"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PIRAT_LIBURNE"))
                      if pUnit.getUnitType() not in UnitArray:

                        # Keil
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_KEIL")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_keil_marine_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, 718, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_keil_marine.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                        # Zange
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_NAVAL_ZANGE")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_zange_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, 718, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_zange.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                  # Mounted mit Fernangriff
                  elif pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_MOUNTED"):
                    UnitArray = []
                    #UnitArray.append(gc.getInfoTypeForString("UNIT_CHARIOT_ARCHER"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_ROMAN"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_SCYTHS"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_HORSE_ARCHER_BAKTRIEN"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_ARABIA_CAMELARCHER"))
                    if pUnit.getUnitType() in UnitArray:
                      CivArray = []
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HETHIT"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PHON"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ISRAEL"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PERSIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BABYLON"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SUMERIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ASSYRIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SKYTHEN"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_PARTHER"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_HUNNEN"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_INDIA"))
                      CivArray.append(gc.getInfoTypeForString("CIVILIZATION_BARBARIAN"))
                      if pUnit.getCivilizationType() in CivArray and pTeam.isHasTech(gc.getInfoTypeForString("TECH_PARTHERSCHUSS")):
                        # Partherschuss
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_PARTHER")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_parther_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, 718, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_parther.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KANTAKREIS")):
                        # Kantabrischer Kreis
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_KANTAKREIS")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_kantakreis_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, 718, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_kantakreis.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1


                    # Keil (auch weiter unten fuer Melee)
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MOUNTED_SACRED_BAND_CARTHAGE"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_EQUITES"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_HORSEMAN_EQUITES2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_HORSEMAN_DECURIO"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_TRIBUN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CATAPHRACT_PERSIA"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CLIBANARII"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CLIBANARII_ROME"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIBERIAN_CAVALRY"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_MONGOL_KESHIK"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN_RIDER"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_HEAVY_HORSEMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CAMEL_CATAPHRACT"))

                      if pUnit.getUnitType() in UnitArray:
                        # Keil
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_KEIL")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_keil_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_keil.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                    UnitArray = []
                    UnitArray.append(gc.getInfoTypeForString("UNIT_BEGLEITHUND"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_TIBET"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_MACEDON"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_KAMPFHUND_BRITEN"))
                    UnitArray.append(gc.getInfoTypeForString("UNIT_BURNING_PIGS"))
                    if pUnit.getUnitType() not in UnitArray:
                      # Fourage
                      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BRANDSCHATZEN")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FOURAGE")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_fourage_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, 718, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_fourage.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                  # Melee and Spear
                  elif pUnit.getUnitCombatType() in lMelee:

                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_BEWAFFNUNG4")):
                      # Schildwall
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_WARRIOR"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KURZSCHWERT"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_KRUMMSAEBEL"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_FALCATA_IBERIA"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LIGHT_SPEARMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_AXEWARRIOR"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_AXEMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_BERSERKER_GERMAN"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_CELTIC_GALLIC_WARRIOR"))

                      if pUnit.getUnitType() not in UnitArray:
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_SCHILDWALL")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_wall_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_wall.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                    # Manipel, Phalanx, ...
                    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):

                      # Roman Legion (Kohorte / ersetzt alles)
                      UnitArray = []
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
                      UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN3"))

                      if pUnit.getUnitType() in UnitArray:
                        # Kohorte
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_KOHORTE")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_kohorte_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_kohorte.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                      # Treffen-Taktik ersetzt Manipel
                      elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_TREFFEN")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_treffen_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_treffen.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                      # Manipel ersetzt Phalanx, Manipular-Phalanx und Schiefe Phalanx
                      elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_MANIPEL")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_MANIPEL")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_manipel_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_manipel.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                      # Phalanx-Arten und Geschlossene Formation
                      else:
                       # Phalanx nur Speer
                       if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):

                        # Manipular-Phalanx und Schiefe Phalanx ersetzt Phalanx
                        if pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX2")):

                         # Schiefe Schlachtordnung
                         #CivArray = []
                         #CivArray.append(gc.getInfoTypeForString("CIVILIZATION_GREECE"))
                         #CivArray.append(gc.getInfoTypeForString("CIVILIZATION_ATHENS"))
                         #CivArray.append(gc.getInfoTypeForString("CIVILIZATION_THEBAI"))
                         #CivArray.append(gc.getInfoTypeForString("CIVILIZATION_SPARTA"))
                         #CivArray.append(gc.getInfoTypeForString("CIVILIZATION_MACEDONIA"))
                         #if pUnit.getCivilizationType() in CivArray:
                         iFormation = gc.getInfoTypeForString("PROMOTION_FORM_SCHIEF")
                         if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx_s_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                         else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx_s.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                         # Manipular-Phalanx
                         iFormation = gc.getInfoTypeForString("PROMOTION_FORM_PHALANX2")
                         if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx_m_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                         else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx_m.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                        # Phalanx
                        elif pTeam.isHasTech(gc.getInfoTypeForString("TECH_PHALANX")):
                          iFormation = gc.getInfoTypeForString("PROMOTION_FORM_PHALANX")
                          if pUnit.isHasPromotion(iFormation):
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                            bFormationUndo = True
                          else:
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_phalanx.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1


                       # Geschlossene Formation (alle Melee)
                       if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CLOSED_FORM")):
                         iFormation = gc.getInfoTypeForString("PROMOTION_FORM_CLOSED_FORM")
                         if pUnit.isHasPromotion(iFormation):
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_closed_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                            bFormationUndo = True
                         else:
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_closed.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                    # Drill end ------------

                    # Keil (auch bei Mounted)
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_KETTENPANZER")):
                        # Keil
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_KEIL")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_keil_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_keil.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                    # Zangenangriff
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_MILIT_STRAT")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_ZANGENANGRIFF")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_zange_a_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_form_zange_a.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                    # Flankenschutz (nur Speer)
                    if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"):
                      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TREFFEN")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FLANKENSCHUTZ")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_flanke_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_flanke.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1


                    # Gedrillte Soldaten
                    if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):

                      # Testudo (nur Legion)
                      if pTeam.isHasTech(gc.getInfoTypeForString("TECH_TESTUDO")):
                        UnitArray = []
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_OPTIO2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_LEGION_CENTURIO2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN2"))
                        UnitArray.append(gc.getInfoTypeForString("UNIT_PRAETORIAN3"))
                        if pUnit.getUnitType() in UnitArray:

                          iFormation = gc.getInfoTypeForString("PROMOTION_FORM_TESTUDO")
                          if pUnit.isHasPromotion(iFormation):
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_testudo_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1
                            bFormationUndo = True
                          else:
                            screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_testudo.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                            screen.show( "BottomButtonContainer" )
                            iCount = iCount + 1

                    # Elefantengasse (auch weiter unten fuer Bogen)
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_GASSE")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_gasse_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_gasse.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1


                  # Archers
                  elif pUnit.getUnitCombatType() in lArcher:
                    # Elefantengasse
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_GEOMETRIE2")):
                        #if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_DRILL1")):
                        iFormation = gc.getInfoTypeForString("PROMOTION_FORM_GASSE")
                        if pUnit.isHasPromotion(iFormation):
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_gasse_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1
                          bFormationUndo = True
                        else:
                          screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_gasse.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                          screen.show( "BottomButtonContainer" )
                          iCount = iCount + 1

                # -- Ende else Fortress

                # Flucht
                if pUnit.getDamage() >= 70:

                  UnitCombatArray = []
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_MELEE"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_AXEMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SWORDSMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SPEARMAN"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_ARCHER"))
                  UnitCombatArray.append(gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER"))

                  if pUnit.getUnitCombatType() in UnitCombatArray:
                   if pUnit.baseMoves() == 1:
                    iFormation = gc.getInfoTypeForString("PROMOTION_FORM_FLIGHT")
                    if pUnit.isHasPromotion(iFormation):
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_flight_gr.dds", 0, WidgetTypes.WIDGET_PEDIA_JUMP_TO_PROMOTION, iFormation, -1, False )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1
                      bFormationUndo = True
                    else:
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_flight.dds", 0, WidgetTypes.WIDGET_HELP_PROMOTION, iFormation, 718, True )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

              # Keine Formation
              if bFormationUndo:
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Formations/button_formation_none.dds", 0, WidgetTypes.WIDGET_GENERAL, -1, 718, True )
                      screen.show( "BottomButtonContainer" )
                      iCount = iCount + 1

            # Formationen / Formations End ------


            # Legend can become a Great General
            if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT6")):
               lArcher = [gc.getInfoTypeForString("UNITCOMBAT_ARCHER"),gc.getInfoTypeForString("UNITCOMBAT_SKIRMISHER")]
               if pUnit.getUnitCombatType() not in lArcher:
                  if not pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_LEADER")):
                    screen.appendMultiListButton( "BottomButtonContainer", ArtFileMgr.getInterfaceArtInfo("INTERFACE_LEGEND_HERO_TO_GENERAL").getPath(), 0, WidgetTypes.WIDGET_GENERAL, 720, 720, False )
                    screen.show( "BottomButtonContainer" )
                    iCount = iCount + 1


            # Salae/Sold/Salaire und/oder Dezimation/Dezimierung
            if pUnit.canMove():
               if pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG1")) or pUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MERCENARY")):
                  if pTeam.isHasTech(gc.getInfoTypeForString("TECH_CURRENCY")):
                    # +x Gold pro Promotion
                    FormationArray = []
                    FormationArray.append(gc.getInfoTypeForString("PROMOTION_WILDLIFE"))
                    FormationArray.append(gc.getInfoTypeForString("PROMOTION_LOYALITAT"))
                    FormationArray.append(gc.getInfoTypeForString("PROMOTION_MERCENARY"))
                    iGold = 0
                    iRange = gc.getNumPromotionInfos()
                    for j in range(iRange):
                      if "_FORM_" in gc.getPromotionInfo(j).getType(): continue
                      if "_RANG_" in gc.getPromotionInfo(j).getType(): continue
                      if "_MORAL_" in gc.getPromotionInfo(j).getType(): continue
                      if "_TRAIT_" in gc.getPromotionInfo(j).getType(): continue
                      if pUnit.isHasPromotion(j) and j not in FormationArray: iGold += 20
                    if iGold == 0: iGold = 20
                    if gc.getPlayer(pUnit.getOwner()).hasBonus(gc.getInfoTypeForString("BONUS_SALT")): iGold -= iGold / 4

                    #Button testen
                    screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_salae.dds", 0, WidgetTypes.WIDGET_GENERAL, 735, 1, True )
                    screen.show( "BottomButtonContainer" )

                    if gc.getPlayer(pUnit.getOwner()).getGold() < iGold:
                       screen.disableMultiListButton( "BottomButtonContainer", 0, iCount, "Art/Interface/Buttons/Actions/button_action_salae.dds" )
                    iCount += 1

                    # Dezimierung
                    if pTeam.isHasTech(gc.getInfoTypeForString("TECH_DEZIMATION")):
                      #Button
                      screen.appendMultiListButton( "BottomButtonContainer", "Art/Interface/Buttons/Actions/button_action_dezimierung.dds", 0, WidgetTypes.WIDGET_GENERAL, 735, 2, True )
                      screen.show( "BottomButtonContainer" )

                      if pUnit.getDamage() > 80:
                        screen.disableMultiListButton( "BottomButtonContainer", 0, iCount, "Art/Interface/Buttons/Actions/button_action_dezimierung.dds" )
                      iCount += 1



    elif (CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY):

      self.setMinimapButtonVisibility(True)

    return 0

  # Will update the research buttons
  def updateResearchButtons( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    for i in range( gc.getNumTechInfos() ):
      szName = "ResearchButton" + str(i)
      screen.hide( szName )

    # Find out our resolution
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    #screen.hide( "InterfaceOrnamentLeftLow" )
    #screen.hide( "InterfaceOrnamentRightLow" )

    for i in range(gc.getNumReligionInfos()):
      szName = "ReligionButton" + str(i)
      screen.hide( szName )

    i = 0
    if ( CyInterface().shouldShowResearchButtons() and CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
      iCount = 0

      for i in range( gc.getNumTechInfos() ):
        if (gc.getActivePlayer().canResearch(i, False)):
          if (iCount < 20):
            szName = "ResearchButton" + str(i)

            bDone = False
            for j in range( gc.getNumReligionInfos() ):
              if ( not bDone ):
                if (gc.getReligionInfo(j).getTechPrereq() == i):
                  if not (gc.getGame().isReligionSlotTaken(j)):
                    szName = "ReligionButton" + str(j)
                    bDone = True

            screen.show( szName )
            self.setResearchButtonPosition(szName, iCount)

          iCount = iCount + 1

    return 0

  # SPECIALIST STACKER        05/02/07      JOHNY
  def updateCitizenButtons( self ):

    global MAX_CITIZEN_BUTTONS
    global MAX_SUPER_SPECIALIST_BUTTONS
    global MAX_ANGRY_CITIZEN_BUTTONS
    global g_iSuperSpecialistCount
    global g_iAngryCitizensCount

    bHandled = False

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    screen.hide( "SpecialistBackground" )
    screen.hide( "SpecialistLabel" )


    # Find out our resolution
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    for i in range( g_iSuperSpecialistCount ):
      szName = "FreeSpecialist" + str(i)
      screen.hide( szName )

    for i in range( g_iAngryCitizensCount ):
      szName = "AngryCitizen" + str(i)
      screen.hide( szName )

    for i in range( gc.getNumSpecialistInfos() ):
      szName = "IncreaseSpecialist" + str(i)
      screen.hide( szName )
      szName = "DecreaseSpecialist" + str(i)
      screen.hide( szName )
      szName = "CitizenDisabledButton" + str(i)
      screen.hide( szName )
      for j in range(MAX_CITIZEN_BUTTONS):
        szName = "CitizenButton" + str((i * 100) + j)
        screen.hide( szName )
        szName = "CitizenButtonHighlight" + str((i * 100) + j)
        screen.hide( szName )

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()

    if ( CyInterface().isCityScreenUp() ):

      if (pHeadSelectedCity and CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW):
        #if ( pHeadSelectedCity.angryPopulation(0) < MAX_CITIZEN_BUTTONS ):
        #  iCount = pHeadSelectedCity.angryPopulation(0)
        #else:
        #  iCount = MAX_CITIZEN_BUTTONS

        currentAngryCitizenCount = pHeadSelectedCity.angryPopulation(0)

        for i in range(currentAngryCitizenCount):
          if (currentAngryCitizenCount < 9):
            stackWidth = 25
          elif (currentAngryCitizenCount == 9):
            stackWidth = 22
          elif (currentAngryCitizenCount == 10):
            stackWidth = 19
          elif (currentAngryCitizenCount == 11):
            stackWidth = 17
          elif (currentAngryCitizenCount == 12):
            stackWidth = 16
          elif (currentAngryCitizenCount == 13):
            stackWidth = 14
          elif (currentAngryCitizenCount == 14):
            stackWidth = 13
          elif (currentAngryCitizenCount == 15):
            stackWidth = 12
          elif (currentAngryCitizenCount == 16):
            stackWidth = 12
          elif (currentAngryCitizenCount == 17):
            stackWidth = 11
          elif (currentAngryCitizenCount == 18):
            stackWidth = 10
          elif (currentAngryCitizenCount == 19):
            stackWidth = 10
          elif (currentAngryCitizenCount == 20):
            stackWidth = 9
          elif (currentAngryCitizenCount == 21):
            stackWidth = 9
          elif (currentAngryCitizenCount == 22):
            stackWidth = 8
          elif (currentAngryCitizenCount == 23):
            stackWidth = 8
          elif (currentAngryCitizenCount == 24):
            stackWidth = 8
          elif (currentAngryCitizenCount == 25):
            stackWidth = 7
          elif (currentAngryCitizenCount == 26):
            stackWidth = 7
          elif (currentAngryCitizenCount == 27):
            stackWidth = 7
          elif (33 > currentAngryCitizenCount > 27):
            stackWidth = 6
          elif (39 > currentAngryCitizenCount > 32):
            stackWidth = 5
          elif (48 > currentAngryCitizenCount > 38):
            stackWidth = 4
          elif (64 > currentAngryCitizenCount > 47):
            stackWidth = 3
          elif (95 > currentAngryCitizenCount > 63):
            stackWidth = 2
          else:
            stackWidth = 1
          bHandled = True
          szName = "AngryCitizen" + str(i)
          screen.setImageButton( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_ANGRYCITIZEN_TEXTURE").getPath(), xResolution - 74 - (stackWidth * i), yResolution - 228, 24, 24, WidgetTypes.WIDGET_ANGRY_CITIZEN, -1, -1 )
          screen.show( szName )

        g_iAngryCitizensCount = currentAngryCitizenCount

        iCount = 0

        bHandled = False
        currentSuperSpecialistCount = 0

        for i in range(gc.getNumSpecialistInfos()):
          if(pHeadSelectedCity.getFreeSpecialistCount(i) > 0):
            if(g_bDisplayUniqueSuperSpecialistsOnly):
              currentSuperSpecialistCount = currentSuperSpecialistCount + 1
            else:
              currentSuperSpecialistCount = currentSuperSpecialistCount + pHeadSelectedCity.getFreeSpecialistCount(i)

        # Set the stackWidth to the original super specialist spacing amount
        for i in range(currentSuperSpecialistCount):
          if (currentSuperSpecialistCount < 9):
            stackWidth = 25
          elif (currentSuperSpecialistCount == 9):
            stackWidth = 22
          elif (currentSuperSpecialistCount == 10):
            stackWidth = 19
          elif (currentSuperSpecialistCount == 11):
            stackWidth = 17
          elif (currentSuperSpecialistCount == 12):
            stackWidth = 16
          elif (currentSuperSpecialistCount == 13):
            stackWidth = 14
          elif (currentSuperSpecialistCount == 14):
            stackWidth = 13
          elif (currentSuperSpecialistCount == 15):
            stackWidth = 12
          elif (currentSuperSpecialistCount == 16):
            stackWidth = 12
          elif (currentSuperSpecialistCount == 17):
            stackWidth = 11
          elif (currentSuperSpecialistCount == 18):
            stackWidth = 10
          elif (currentSuperSpecialistCount == 19):
            stackWidth = 10
          elif (currentSuperSpecialistCount == 20):
            stackWidth = 9
          elif (currentSuperSpecialistCount == 21):
            stackWidth = 9
          elif (currentSuperSpecialistCount == 22):
            stackWidth = 8
          elif (currentSuperSpecialistCount == 23):
            stackWidth = 8
          elif (currentSuperSpecialistCount == 24):
            stackWidth = 8
          elif (currentSuperSpecialistCount == 25):
            stackWidth = 7
          elif (currentSuperSpecialistCount == 26):
            stackWidth = 7
          elif (currentSuperSpecialistCount == 27):
            stackWidth = 7
          elif (33 > currentSuperSpecialistCount > 27):
            stackWidth = 6
          elif (39 > currentSuperSpecialistCount > 32):
            stackWidth = 5
          elif (48 > currentSuperSpecialistCount > 38):
            stackWidth = 4
          elif (64 > currentSuperSpecialistCount > 47):
            stackWidth = 3
          elif (95 > currentSuperSpecialistCount > 63):
            stackWidth = 2
          else:
            stackWidth = 1

        if(g_bStackSuperSpecialists and SUPER_SPECIALIST_STACK_WIDTH > 10):
          stackWidth = SUPER_SPECIALIST_STACK_WIDTH

        if(g_bStackSuperSpecialists and g_bDynamicSuperSpecialistsSpacing and currentSuperSpecialistCount > 0):
          stackWidth = 184/currentSuperSpecialistCount

        for i in range(gc.getNumSpecialistInfos()):
          for j in range( pHeadSelectedCity.getFreeSpecialistCount(i) ):
            if (g_bStackSuperSpecialists == False and iCount > MAX_SUPER_SPECIALIST_BUTTONS-1):
              break

            szName = "FreeSpecialist" + str(iCount)
            screen.setImageButton( szName, gc.getSpecialistInfo(i).getTexture(), (xResolution - 74  - (stackWidth * iCount)), yResolution - 203, 24, 24, WidgetTypes.WIDGET_FREE_CITIZEN, i, 1 )
            screen.show( szName )
            bHandled = True

            iCount = iCount + 1

            if(g_bDisplayUniqueSuperSpecialistsOnly):
              break

        g_iSuperSpecialistCount = iCount

        iXShiftVal = 0
        iYShiftVal = 0
        iSpecialistCount = 0

        for i in range( gc.getNumSpecialistInfos() ):

          bHandled = False
          if( iSpecialistCount > 5 ):
            iXShiftVal = 110
            iYShiftVal = (iSpecialistCount % 5) - 1
          else:
            iYShiftVal = iSpecialistCount

          if (gc.getSpecialistInfo(i).isVisible()):
            iSpecialistCount = iSpecialistCount + 1

          if (pHeadSelectedCity.getOwner() == gc.getGame().getActivePlayer() or gc.getGame().isDebugMode()):

            if ( pHeadSelectedCity.isSpecialistValid(i, 1) and ( pHeadSelectedCity.getForceSpecialistCount(i) < ( pHeadSelectedCity.getPopulation() + pHeadSelectedCity.totalFreeSpecialists() ) ) ):
              szName = "IncreaseSpecialist" + str(i)
              screen.show( szName )
              szName = "CitizenDisabledButton" + str(i)
              screen.show( szName )

            if ( pHeadSelectedCity.getSpecialistCount(i) > 0 or pHeadSelectedCity.getForceSpecialistCount(i) > 0 ):
              szName = "CitizenDisabledButton" + str(i)
              screen.hide( szName )
              szName = "DecreaseSpecialist" + str(i)
              screen.show( szName )

          if (pHeadSelectedCity.getSpecialistCount(i) < MAX_CITIZEN_BUTTONS):
            iCount = pHeadSelectedCity.getSpecialistCount(i)
          else:
            iCount = MAX_CITIZEN_BUTTONS

          j = iCount-1

          while(j >= 0):
            if( j <= 9):
                                                    bHandled = True
                                                    szName = "CitizenButton" + str((i * 100) + j)
                                                    if (gc.getSpecialistInfo(i).isVisible()):
                                                            screen.addCheckBoxGFC( szName, gc.getSpecialistInfo(i).getTexture(), "", xResolution + 5 - (74+iXShiftVal) - (SPECIALIST_STACK_WIDTH * j), (yResolution - 253 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j, ButtonStyles.BUTTON_STYLE_LABEL )
                                                    else:
                                                           screen.addCheckBoxGFC( szName, gc.getSpecialistInfo(i).getTexture(), "", xResolution + 5 - 74 - (SPECIALIST_STACK_WIDTH * j), (yResolution - 253 - (30 * i)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j, ButtonStyles.BUTTON_STYLE_LABEL )

                                                    screen.show( szName )
                                                    szName = "CitizenButtonHighlight" + str((i * 100) + j)
                                                    if (gc.getSpecialistInfo(i).isVisible()):
                                                            screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), xResolution + 5 - (74+iXShiftVal) - (SPECIALIST_STACK_WIDTH * j), (yResolution - 253 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j )
                                                    else:
                                                            screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), xResolution + 5 - 74 - (SPECIALIST_STACK_WIDTH * j), (yResolution - 253 - (30 * i)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j )

                                                    if ( pHeadSelectedCity.getForceSpecialistCount(i) > j and g_bHighlightForcedSpecialists):
                                                            screen.show( szName )
                                                    else:
                                                            screen.hide( szName )

            elif( j <= 20):
                                                    bHandled = True
                                                    szName = "CitizenButton" + str((i * 100) + j)
                                                    if (gc.getSpecialistInfo(i).isVisible()):
                                                            screen.addCheckBoxGFC( szName, gc.getSpecialistInfo(i).getTexture(), "", xResolution + 65 - (74+iXShiftVal) - (SPECIALIST_STACK_WIDTH * j), (yResolution - 261 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j, ButtonStyles.BUTTON_STYLE_LABEL )
                                                    else:
                                                            screen.addCheckBoxGFC( szName, gc.getSpecialistInfo(i).getTexture(), "", xResolution + 65 - 74 - (SPECIALIST_STACK_WIDTH * j), (yResolution - 261 - (30 * i)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j, ButtonStyles.BUTTON_STYLE_LABEL )

                                                    screen.show( szName )
                                                    szName = "CitizenButtonHighlight" + str((i * 100) + j)
                                                    if (gc.getSpecialistInfo(i).isVisible()):
                                                            screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), xResolution + 65 - (74+iXShiftVal) - (SPECIALIST_STACK_WIDTH * j), (yResolution - 261 - (30 * iYShiftVal)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j )
                                                    else:
                                                            screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(), xResolution + 65 - 74 - (SPECIALIST_STACK_WIDTH * j), (yResolution - 261 - (30 * i)), 24, 24, WidgetTypes.WIDGET_CITIZEN, i, j )

                                                    if ( pHeadSelectedCity.getForceSpecialistCount(i) > j and g_bHighlightForcedSpecialists):
                                                            screen.show( szName )
                                                    else:
                                                            screen.hide( szName )

            j = j-1

          if ( not bHandled ):
            szName = "CitizenDisabledButton" + str(i)
            screen.show( szName )

      screen.addPanel( "SpecialistBackground", u"", u"", True, False, xResolution - 243, yResolution-455, 230, 30, PanelStyles.PANEL_STYLE_STANDARD )
      screen.setStyle( "SpecialistBackground", "Panel_City_Header_Style" )
      screen.show( "SpecialistBackground" )
      screen.setLabel( "SpecialistLabel", "Background", localText.getText("TXT_KEY_LABEL_SPECIALISTS", ()), CvUtil.FONT_CENTER_JUSTIFY, xResolution - 128, yResolution-447, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.show( "SpecialistLabel" )

    return 0

  # SPECIALIST STACKER        END

  # Will update the game data strings
  def updateGameDataStrings( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    screen.hide( "ResearchText" )
    screen.hide( "GoldText" )
    screen.hide( "TimeText" )
    screen.hide( "ResearchBar" )

# PAE - Great General Bar - start
    screen.hide( "GreatGeneralBar" )
    screen.hide( "GreatGeneralBarText" )
    screen.hide( "GreatGeneralBarIcon" )
# PAE - Great General Bar - end
# PAE - Great Person Bar - start
    screen.hide( "GreatPersonBar" )
    screen.hide( "GreatPersonBarText" )
    screen.hide( "GreatPersonBarIcon" )
# PAE - Great Person Bar - end

    bShift = CyInterface().shiftKey()

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()

    if (pHeadSelectedCity):
      ePlayer = pHeadSelectedCity.getOwner()
    else:
      ePlayer = gc.getGame().getActivePlayer()

    if ( ePlayer < 0 or ePlayer >= gc.getMAX_PLAYERS() ):
      return 0

    for iI in range(CommerceTypes.NUM_COMMERCE_TYPES):
      szString = "PercentText" + str(iI)
      screen.hide(szString)
      szString = "RateText" + str(iI)
      screen.hide(szString)

    if ( CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY  and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_ADVANCED_START):

      # Percent of commerce
      if (gc.getPlayer(ePlayer).isAlive()):
        iCount = 0
        for iI in range( CommerceTypes.NUM_COMMERCE_TYPES ):
          eCommerce = (iI + 1) % CommerceTypes.NUM_COMMERCE_TYPES
          if (gc.getPlayer(ePlayer).isCommerceFlexible(eCommerce) or (CyInterface().isCityScreenUp() and (eCommerce == CommerceTypes.COMMERCE_GOLD))):
            szOutText = u"<font=2>%c:%d%%</font>" %(gc.getCommerceInfo(eCommerce).getChar(), gc.getPlayer(ePlayer).getCommercePercent(eCommerce))
            szString = "PercentText" + str(iI)
            screen.setLabel( szString, "Background", szOutText, CvUtil.FONT_LEFT_JUSTIFY, 14, 50 + (iCount * 19), -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            screen.show( szString )

            if not CyInterface().isCityScreenUp():
              szOutText = u"<font=2>" + localText.getText("TXT_KEY_MISC_POS_GOLD_PER_TURN", (gc.getPlayer(ePlayer).getCommerceRate(CommerceTypes(eCommerce)), )) + u"</font>"
              szString = "RateText" + str(iI)
# Min/Max Sliders - Alt: 112 Neu: 152
              screen.setLabel( szString, "Background", szOutText, CvUtil.FONT_LEFT_JUSTIFY, 152, 50 + (iCount * 19), -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
              screen.show( szString )

            iCount = iCount + 1

      self.updateTimeText()
      screen.setLabel( "TimeText", "Background", g_szTimeText, CvUtil.FONT_RIGHT_JUSTIFY, xResolution - 56, 6, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
      screen.show( "TimeText" )

      if (gc.getPlayer(ePlayer).isAlive()):

        szText = CyGameTextMgr().getGoldStr(ePlayer)
        screen.setLabel( "GoldText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, 12, 6, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.show( "GoldText" )

        if (((gc.getPlayer(ePlayer).calculateGoldRate() != 0) and not (gc.getPlayer(ePlayer).isAnarchy())) or (gc.getPlayer(ePlayer).getGold() != 0)):
          screen.show( "GoldText" )

        if (gc.getPlayer(ePlayer).isAnarchy()):

          szText = localText.getText("INTERFACE_ANARCHY", (gc.getPlayer(ePlayer).getAnarchyTurns(), ))
          screen.setText( "ResearchText", "Background", szText, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512), 3, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_RESEARCH, -1, -1 )
          if ( gc.getPlayer(ePlayer).getCurrentResearch() != -1 ):
            screen.show( "ResearchText" )
          else:
            screen.hide( "ResearchText" )

        elif (gc.getPlayer(ePlayer).getCurrentResearch() != -1):

          # PAE x - 30
          szText = CyGameTextMgr().getResearchStr(ePlayer)
          screen.setText( "ResearchText", "Background", szText, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512)-30, 3, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_RESEARCH, -1, -1 )
          screen.show( "ResearchText" )

          researchProgress = gc.getTeam(gc.getPlayer(ePlayer).getTeam()).getResearchProgress(gc.getPlayer(ePlayer).getCurrentResearch())
          overflowResearch = (gc.getPlayer(ePlayer).getOverflowResearch() * gc.getPlayer(ePlayer).calculateResearchModifier(gc.getPlayer(ePlayer).getCurrentResearch()))/100
          researchCost = gc.getTeam(gc.getPlayer(ePlayer).getTeam()).getResearchCost(gc.getPlayer(ePlayer).getCurrentResearch())
          researchRate = gc.getPlayer(ePlayer).calculateResearchRate(-1)

          iFirst = float(researchProgress + overflowResearch) / float(researchCost)
          screen.setBarPercentage( "ResearchBar", InfoBarTypes.INFOBAR_STORED, iFirst )
          if ( iFirst == 1 ):
            screen.setBarPercentage( "ResearchBar", InfoBarTypes.INFOBAR_RATE, ( float(researchRate) / float(researchCost) ) )
          else:
            screen.setBarPercentage( "ResearchBar", InfoBarTypes.INFOBAR_RATE, ( ( float(researchRate) / float(researchCost) ) ) / ( 1 - iFirst ) )

          screen.show( "ResearchBar" )

        # ERA Text _era era_
        screen.setLabel( "EraText", "Background", gc.getEraInfo(gc.getPlayer(ePlayer).getCurrentEra()).getDescription(), CvUtil.FONT_RIGHT_JUSTIFY, 244, 6, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.show( "EraText" )

# PAE - Great General Bar/Great Person Bar - start
        self.updateGreatGeneralBar(screen)
        self.updateGreatPersonBar(screen)
# PAE - Great Bars - end
    return 0

# PAE - Great General Bar - start - edited for PAE from BUG
  def updateGreatGeneralBar(self, screen):
                if not CyInterface().isCityScreenUp():
                        pPlayer = gc.getActivePlayer()
                        iCombatExp = pPlayer.getCombatExperience()
                        iThresholdExp = pPlayer.greatPeopleThreshold(True)
                        szText = u"<font=2>" + localText.getText("TXT_NEXT_GG_EXPERIENCE", (iCombatExp, iThresholdExp)) + u"</font>"
                        szGreatGeneralBar = "GreatGeneralBar"

                        xResolution = screen.getXResolution()
                        if (xResolution >= 1280):
                         xCoord = 270
                         yCoord = 7
                        else:
                         xCoord = 310
                         yCoord = 32

                        # General Bar ist bei X = 278 / B = 120
                        iGeneralIcon = gc.getInfoTypeForString("SPECIALIST_GREAT_GENERAL")
                        screen.setImageButton( "GreatGeneralBarIcon", gc.getSpecialistInfo(iGeneralIcon).getTexture(), xCoord, yCoord - 3, 24, 24, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1 )
                        screen.show( "GreatGeneralBarIcon" )
                        screen.setLabel( "GreatGeneralBarText", "Background", szText, CvUtil.FONT_CENTER_JUSTIFY, xCoord + 64, yCoord, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_GREAT_GENERAL, -1, -1 )
                        screen.show( "GreatGeneralBarText" )

                        fProgress = float(iCombatExp) / float(iThresholdExp)
                        screen.setBarPercentage( szGreatGeneralBar, InfoBarTypes.INFOBAR_STORED, fProgress )
                        screen.show( szGreatGeneralBar )
# PAE - Great General Bar - end

# PAE - Great Person Bar - start
  def updateGreatPersonBar(self, screen):
      if not CyInterface().isCityScreenUp():
        pPlayer = gc.getActivePlayer()
        iCityPersonRate = iCityPersonProgress = 0
        pCity = ""
        for i in range (pPlayer.getNumCities()):
          if pPlayer.getCity(i).getGreatPeopleProgress() > 0 or pPlayer.getCity(i).getGreatPeopleRate() > 0:
            if iCityPersonProgress < pPlayer.getCity(i).getGreatPeopleProgress():
              iCityPersonRate = pPlayer.getCity(i).getGreatPeopleRate()
              iCityPersonProgress = pPlayer.getCity(i).getGreatPeopleProgress()
              pCity = pPlayer.getCity(i)


        if iCityPersonProgress > 0:
          iPlayerTreshold = pPlayer.greatPeopleThreshold(False)

          # Spezialistengeburtenwahrscheinlichkeit herausfinden
          #INT getGreatPeopleUnitProgress (UnitType iIndex)
          #INT getGreatPeopleUnitRate (UnitType iIndex)
          iGreatPersonNum = 0
          iGreatPersonType = -1
          for i in range( gc.getNumSpecialistInfos() ):
            if iGreatPersonNum < pCity.getSpecialistCount(i):
              iGreatPersonNum  = pCity.getSpecialistCount(i)
              iGreatPersonType = i

          # Bei Chancengleichheit allg
          bGleicheChance = False
          for i in range( gc.getNumSpecialistInfos() ):
            if iGreatPersonNum == pCity.getSpecialistCount(i) and i != iGreatPersonType:
              bGleicheChance = True


          szGreatPersonBar = "GreatPersonBar"

          xResolution = screen.getXResolution()
          # >= 1440
          if (xResolution >= 1280):
            xCoord = xResolution - 470
            yCoord = 7
          else:
            xCoord = xResolution - 510
            yCoord = 32

          # General Bar ist bei xResolution - 480 / B = 200
          if bGleicheChance:
            szText = localText.getText("TXT_NEXT_GP_1", (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), 0))
            screen.setLabel( "GreatPersonBarIcon", "Background", szText, CvUtil.FONT_CENTER_JUSTIFY, xCoord + 12, yCoord, -1.0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          else:
            screen.setImageButton( "GreatPersonBarIcon", gc.getSpecialistInfo(iGreatPersonType).getTexture(), xCoord, yCoord - 3, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.show( "GreatPersonBarIcon" )

          szText = localText.getText("TXT_NEXT_GP_2", (pCity.getName(),iCityPersonRate,iCityPersonProgress,iPlayerTreshold))

          screen.setLabel( "GreatPersonBarText", "Background", szText, CvUtil.FONT_CENTER_JUSTIFY, xCoord + 106, yCoord, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.setHitTest( "GreatPersonBarText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "GreatPersonBarText" )

          iFirst = float(iCityPersonProgress) / float(iPlayerTreshold)
          screen.setBarPercentage( szGreatPersonBar, InfoBarTypes.INFOBAR_STORED, iFirst )
          if ( iFirst == 1 ):
            screen.setBarPercentage( szGreatPersonBar, InfoBarTypes.INFOBAR_RATE, ( float(iCityPersonRate) / float(iPlayerTreshold) ) )
          else:
            screen.setBarPercentage( szGreatPersonBar, InfoBarTypes.INFOBAR_RATE, ( ( float(iCityPersonRate) / float(iPlayerTreshold) ) ) / ( 1 - iFirst ) )
          screen.show( szGreatPersonBar )

# PAE - Great Person Bar - end

  def updateTimeText( self ):

    global g_szTimeText

    ePlayer = gc.getGame().getActivePlayer()

    g_szTimeText = localText.getText("TXT_KEY_TIME_TURN", (gc.getGame().getGameTurn(), )) + u" - " + unicode(CyGameTextMgr().getInterfaceTimeStr(ePlayer))
    if (CyUserProfile().isClockOn()):
      g_szTimeText = getClockText() + u" - " + g_szTimeText

  # Will update the selection Data Strings
  def updateCityScreen( self ):

    global MAX_DISPLAYABLE_BUILDINGS
    global MAX_DISPLAYABLE_TRADE_ROUTES
    global MAX_BONUS_ROWS

    global g_iNumTradeRoutes
    global g_iNumBuildings
    global g_iNumLeftBonus
    global g_iNumCenterBonus
    global g_iNumRightBonus

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()

    # Find out our resolution
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    bShift = CyInterface().shiftKey()

    screen.hide( "PopulationBar" )
    screen.hide( "ProductionBar" )
    screen.hide( "GreatPeopleBar" )
    screen.hide( "CultureBar" )
    screen.hide( "MaintenanceText" )
    screen.hide( "MaintenanceAmountText" )
    screen.hide( "PAE_SupplyText" )
    screen.hide( "PAE_SupplyBar" )
    screen.hide( "PAE_EmigrationText" )
    screen.hide( "PAE_EmigrationBar" )
    screen.hide( "PAE_RevoltText" )
    screen.hide( "PAE_RevoltBar" )
    screen.hide( "PAE_SlavesText" )
    screen.hide( "PAE_SlavesBar" )
#    screen.hide( "PAE_RebellionText" )
#    screen.hide( "PAE_RebellionBar" )
    screen.hide( "PAE_Rebellion2Text" )
    screen.hide( "PAE_Rebellion2Bar" )
    screen.hide( "NationalityText" )
    screen.hide( "NationalityBar" )
    screen.hide( "DefenseText" )
    screen.hide( "CityScrollMinus" )
    screen.hide( "CityScrollPlus" )
    screen.hide( "CityNameText" )
    screen.hide( "PopulationText" )
    screen.hide( "PopulationInputText" )
    screen.hide( "HealthText" )
    screen.hide( "ProductionText" )
    screen.hide( "ProductionInputText" )
    screen.hide( "HappinessText" )
    screen.hide( "CultureText" )
    screen.hide( "GreatPeopleText" )

    for i in range( gc.getNumReligionInfos() ):
      szName = "ReligionHolyCityDDS" + str(i)
      screen.hide( szName )
      szName = "ReligionDDS" + str(i)
      screen.hide( szName )

    for i in range( gc.getNumCorporationInfos() ):
      szName = "CorporationHeadquarterDDS" + str(i)
      screen.hide( szName )
      szName = "CorporationDDS" + str(i)
      screen.hide( szName )

    for i in range(CommerceTypes.NUM_COMMERCE_TYPES):
      szName = "CityPercentText" + str(i)
      screen.hide( szName )

    screen.addPanel( "BonusPane0", u"", u"", True, False, xResolution - 244, 94, 57, yResolution - 520, PanelStyles.PANEL_STYLE_CITY_COLUMNL )
    screen.hide( "BonusPane0" )
    screen.addScrollPanel( "BonusBack0", u"", xResolution - 242, 94, 157, yResolution - 536, PanelStyles.PANEL_STYLE_EXTERNAL )
    screen.hide( "BonusBack0" )

    screen.addPanel( "BonusPane1", u"", u"", True, False, xResolution - 187, 94, 68, yResolution - 520, PanelStyles.PANEL_STYLE_CITY_COLUMNC )
    screen.hide( "BonusPane1" )
    screen.addScrollPanel( "BonusBack1", u"", xResolution - 191, 94, 184, yResolution - 536, PanelStyles.PANEL_STYLE_EXTERNAL )
    screen.hide( "BonusBack1" )

    screen.addPanel( "BonusPane2", u"", u"", True, False, xResolution - 119, 94, 107, yResolution - 520, PanelStyles.PANEL_STYLE_CITY_COLUMNR )
    screen.hide( "BonusPane2" )
    screen.addScrollPanel( "BonusBack2", u"", xResolution - 125, 94, 205, yResolution - 536, PanelStyles.PANEL_STYLE_EXTERNAL )
    screen.hide( "BonusBack2" )

    screen.hide( "TradeRouteTable" )
    screen.hide( "BuildingListTable" )

    screen.hide( "BuildingListBackground" )
    screen.hide( "TradeRouteListBackground" )
    screen.hide( "BuildingListLabel" )
    screen.hide( "TradeRouteListLabel" )

    i = 0
    for i in range( g_iNumLeftBonus ):
      szName = "LeftBonusItem" + str(i)
      screen.hide( szName )

    i = 0
    for i in range( g_iNumCenterBonus ):
      szName = "CenterBonusItemLeft" + str(i)
      screen.hide( szName )
      szName = "CenterBonusItemRight" + str(i)
      screen.hide( szName )

    i = 0
    for i in range( g_iNumRightBonus ):
      szName = "RightBonusItemLeft" + str(i)
      screen.hide( szName )
      szName = "RightBonusItemRight" + str(i)
      screen.hide( szName )

    i = 0
    for i in range( 3 ):
      szName = "BonusPane" + str(i)
      screen.hide( szName )
      szName = "BonusBack" + str(i)
      screen.hide( szName )

    i = 0
    if ( CyInterface().isCityScreenUp() ):
      if ( pHeadSelectedCity ):

        screen.show( "InterfaceTopLeftBackgroundWidget" )
        screen.show( "InterfaceTopRightBackgroundWidget" )
        screen.show( "InterfaceCenterLeftBackgroundWidget" )
        screen.show( "CityScreenTopWidget" )
        screen.show( "CityNameBackground" )
        screen.show( "TopCityPanelLeft" )
        screen.show( "TopCityPanelRight" )
        screen.show( "CityScreenAdjustPanel" )
        screen.show( "InterfaceCenterRightBackgroundWidget" )

        if ( pHeadSelectedCity.getTeam() == gc.getGame().getActiveTeam() ):
          if ( gc.getActivePlayer().getNumCities() > 1 ):
            screen.show( "CityScrollMinus" )
            screen.show( "CityScrollPlus" )

        # Help Text Area
        screen.setHelpTextArea( 390, FontTypes.SMALL_FONT, 0, 0, -2.2, True, ArtFileMgr.getInterfaceArtInfo("POPUPS_BACKGROUND_TRANSPARENT").getPath(), True, True, CvUtil.FONT_LEFT_JUSTIFY, 0 )

        iFoodDifference = pHeadSelectedCity.foodDifference(True)
        iProductionDiffNoFood = pHeadSelectedCity.getCurrentProductionDifference(True, True)
        iProductionDiffJustFood = (pHeadSelectedCity.getCurrentProductionDifference(False, True) - iProductionDiffNoFood)

        # PAE city food supply for units / city supply
        #pPlot = gc.getMap().plot(pHeadSelectedCity.getX(), pHeadSelectedCity.getY())
        #iCityUnits = pPlot.getNumDefenders(pHeadSelectedCity.getOwner())
        #iCityPop = pHeadSelectedCity.getPopulation()
        # 1 food for 2 additional units (1 pop serves 1 unit)
        #iUnitFoodConsumption = 0
        #if iCityUnits > iCityPop * 2: iUnitFoodConsumption = (iCityUnits-iCityPop*2) / 2
        #iFoodDifference -= iUnitFoodConsumption

        szBuffer = u"<font=4>"

        if (pHeadSelectedCity.isCapital()):
          szBuffer += u"%c" %(CyGame().getSymbolID(FontSymbols.STAR_CHAR))
        elif (pHeadSelectedCity.isGovernmentCenter()):
          szBuffer += u"%c" %(CyGame().getSymbolID(FontSymbols.SILVER_STAR_CHAR))

        if (pHeadSelectedCity.isPower()):
          szBuffer += u"%c" %(CyGame().getSymbolID(FontSymbols.POWER_CHAR))

        szBuffer += u"%s: %d" %(pHeadSelectedCity.getName(), pHeadSelectedCity.getPopulation())

        if (pHeadSelectedCity.isOccupation()):
          szBuffer += u" (%c:%d)" %(CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR), pHeadSelectedCity.getOccupationTimer())

        szBuffer += u"</font>"

        screen.setText( "CityNameText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512), 32, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_CITY_NAME, -1, -1 )
        screen.setStyle( "CityNameText", "Button_Stone_Style" )
        screen.show( "CityNameText" )

        if ( (iFoodDifference != 0) or not (pHeadSelectedCity.isFoodProduction() ) ):
          if (iFoodDifference > 0):
            szBuffer = localText.getText("INTERFACE_CITY_GROWING", (pHeadSelectedCity.getFoodTurnsLeft(), ))
          elif (iFoodDifference < 0):
            szBuffer = localText.getText("INTERFACE_CITY_STARVING", ())
          else:
            szBuffer = localText.getText("INTERFACE_CITY_STAGNANT", ())

          screen.setLabel( "PopulationText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512), iCityCenterRow1Y, -1.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.setHitTest( "PopulationText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "PopulationText" )

        if (not pHeadSelectedCity.isDisorder() and not pHeadSelectedCity.isFoodProduction()):

          szBuffer = u"%d%c - %d%c" %(pHeadSelectedCity.getYieldRate(YieldTypes.YIELD_FOOD), gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar(), pHeadSelectedCity.foodConsumption(False, 0), CyGame().getSymbolID(FontSymbols.EATEN_FOOD_CHAR))
          screen.setLabel( "PopulationInputText", "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, iCityCenterRow1X - 6, iCityCenterRow1Y, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.show( "PopulationInputText" )

        else:

          szBuffer = u"%d%c" %(iFoodDifference, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar())
          screen.setLabel( "PopulationInputText", "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, iCityCenterRow1X - 6, iCityCenterRow1Y, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.show( "PopulationInputText" )

        if ((pHeadSelectedCity.badHealth(False) > 0) or (pHeadSelectedCity.goodHealth() >= 0)):
          if (pHeadSelectedCity.healthRate(False, 0) < 0):
            szBuffer = localText.getText("INTERFACE_CITY_HEALTH_BAD", (pHeadSelectedCity.goodHealth(), pHeadSelectedCity.badHealth(False), pHeadSelectedCity.healthRate(False, 0)))
          elif (pHeadSelectedCity.badHealth(False) > 0):
            szBuffer = localText.getText("INTERFACE_CITY_HEALTH_GOOD", (pHeadSelectedCity.goodHealth(), pHeadSelectedCity.badHealth(False)))
          else:
            szBuffer = localText.getText("INTERFACE_CITY_HEALTH_GOOD_NO_BAD", (pHeadSelectedCity.goodHealth(), ))

          screen.setLabel( "HealthText", "Background", szBuffer, CvUtil.FONT_LEFT_JUSTIFY, xResolution - iCityCenterRow1X + 6, iCityCenterRow1Y, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_HEALTH, -1, -1 )
          screen.show( "HealthText" )

        if (iFoodDifference < 0):

          if ( pHeadSelectedCity.getFood() + iFoodDifference > 0 ):
            iDeltaFood = pHeadSelectedCity.getFood() + iFoodDifference
          else:
            iDeltaFood = 0
          if ( -iFoodDifference < pHeadSelectedCity.getFood() ):
            iExtraFood = -iFoodDifference
          else:
            iExtraFood = pHeadSelectedCity.getFood()
          iFirst = float(iDeltaFood) / float(pHeadSelectedCity.growthThreshold())
          screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_STORED, iFirst )
          screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE, 0.0 )
          if ( iFirst == 1 ):
            screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE_EXTRA, ( float(iExtraFood) / float(pHeadSelectedCity.growthThreshold()) ) )
          else:
            screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE_EXTRA, ( ( float(iExtraFood) / float(pHeadSelectedCity.growthThreshold()) ) ) / ( 1 - iFirst ) )

        else:

          iFirst = float(pHeadSelectedCity.getFood()) / float(pHeadSelectedCity.growthThreshold())
          screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_STORED, iFirst )
          if ( iFirst == 1 ):
            screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE, ( float(iFoodDifference) / float(pHeadSelectedCity.growthThreshold()) ) )
          else:
            screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE, ( ( float(iFoodDifference) / float(pHeadSelectedCity.growthThreshold()) ) ) / ( 1 - iFirst ) )
          screen.setBarPercentage( "PopulationBar", InfoBarTypes.INFOBAR_RATE_EXTRA, 0.0 )

        screen.show( "PopulationBar" )

        if (pHeadSelectedCity.getOrderQueueLength() > 0):
          if (pHeadSelectedCity.isProductionProcess()):
            szBuffer = pHeadSelectedCity.getProductionName()
          else:
            szBuffer = localText.getText("INTERFACE_CITY_PRODUCTION", (pHeadSelectedCity.getProductionNameKey(), pHeadSelectedCity.getProductionTurnsLeft()))

          screen.setLabel( "ProductionText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, screen.centerX(512), iCityCenterRow2Y, -1.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.setHitTest( "ProductionText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "ProductionText" )

        if (pHeadSelectedCity.isProductionProcess()):
          szBuffer = u"%d%c" %(pHeadSelectedCity.getYieldRate(YieldTypes.YIELD_PRODUCTION), gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
        elif (pHeadSelectedCity.isFoodProduction() and (iProductionDiffJustFood > 0)):
          szBuffer = u"%d%c + %d%c" %(iProductionDiffJustFood, gc.getYieldInfo(YieldTypes.YIELD_FOOD).getChar(), iProductionDiffNoFood, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())
        else:
          szBuffer = u"%d%c" %(iProductionDiffNoFood, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getChar())

        screen.setLabel( "ProductionInputText", "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, iCityCenterRow1X - 6, iCityCenterRow2Y, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_PRODUCTION_MOD_HELP, -1, -1 )
        screen.show( "ProductionInputText" )

        if ((pHeadSelectedCity.happyLevel() >= 0) or (pHeadSelectedCity.unhappyLevel(0) > 0)):
          if (pHeadSelectedCity.isDisorder()):
            szBuffer = u"%d%c" %(pHeadSelectedCity.angryPopulation(0), CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR))
          elif (pHeadSelectedCity.angryPopulation(0) > 0):
            szBuffer = localText.getText("INTERFACE_CITY_UNHAPPY", (pHeadSelectedCity.happyLevel(), pHeadSelectedCity.unhappyLevel(0), pHeadSelectedCity.angryPopulation(0)))
          elif (pHeadSelectedCity.unhappyLevel(0) > 0):
            szBuffer = localText.getText("INTERFACE_CITY_HAPPY", (pHeadSelectedCity.happyLevel(), pHeadSelectedCity.unhappyLevel(0)))
          else:
            szBuffer = localText.getText("INTERFACE_CITY_HAPPY_NO_UNHAPPY", (pHeadSelectedCity.happyLevel(), ))

          screen.setLabel( "HappinessText", "Background", szBuffer, CvUtil.FONT_LEFT_JUSTIFY, xResolution - iCityCenterRow1X + 6, iCityCenterRow2Y, -0.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_HELP_HAPPINESS, -1, -1 )
          screen.show( "HappinessText" )

        if (not(pHeadSelectedCity.isProductionProcess())):

          iFirst = ((float(pHeadSelectedCity.getProduction())) / (float(pHeadSelectedCity.getProductionNeeded())))
          screen.setBarPercentage( "ProductionBar", InfoBarTypes.INFOBAR_STORED, iFirst )
          if ( iFirst == 1 ):
            iSecond = ( ((float(iProductionDiffNoFood)) / (float(pHeadSelectedCity.getProductionNeeded()))) )
          else:
            iSecond = ( ((float(iProductionDiffNoFood)) / (float(pHeadSelectedCity.getProductionNeeded()))) ) / ( 1 - iFirst )
          screen.setBarPercentage( "ProductionBar", InfoBarTypes.INFOBAR_RATE, iSecond )
          if ( iFirst + iSecond == 1 ):
            screen.setBarPercentage( "ProductionBar", InfoBarTypes.INFOBAR_RATE_EXTRA, ( ((float(iProductionDiffJustFood)) / (float(pHeadSelectedCity.getProductionNeeded()))) ) )
          else:
            screen.setBarPercentage( "ProductionBar", InfoBarTypes.INFOBAR_RATE_EXTRA, ( ( ((float(iProductionDiffJustFood)) / (float(pHeadSelectedCity.getProductionNeeded()))) ) ) / ( 1 - ( iFirst + iSecond ) ) )

          screen.show( "ProductionBar" )

        iCount = 0

        for i in range(CommerceTypes.NUM_COMMERCE_TYPES):
          eCommerce = (i + 1) % CommerceTypes.NUM_COMMERCE_TYPES

          if ((gc.getPlayer(pHeadSelectedCity.getOwner()).isCommerceFlexible(eCommerce)) or (eCommerce == CommerceTypes.COMMERCE_GOLD)):
            szBuffer = u"%d.%02d %c" %(pHeadSelectedCity.getCommerceRate(eCommerce), pHeadSelectedCity.getCommerceRateTimes100(eCommerce)%100, gc.getCommerceInfo(eCommerce).getChar())

            iHappiness = pHeadSelectedCity.getCommerceHappinessByType(eCommerce)

            if (iHappiness != 0):
              if ( iHappiness > 0 ):
                szTempBuffer = u", %d%c" %(iHappiness, CyGame().getSymbolID(FontSymbols.HAPPY_CHAR))
              else:
                szTempBuffer = u", %d%c" %(-iHappiness, CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR))
              szBuffer = szBuffer + szTempBuffer

            szName = "CityPercentText" + str(iCount)
            screen.setLabel( szName, "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, 220, 45 + (19 * iCount) + 4, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_COMMERCE_MOD_HELP, eCommerce, -1 )
            screen.show( szName )
            iCount = iCount + 1

        iCount = 0

        screen.addTableControlGFC( "TradeRouteTable", 3, 10, 187, 238, 98, False, False, 32, 32, TableStyles.TABLE_STYLE_STANDARD )
        screen.setStyle( "TradeRouteTable", "Table_City_Style" )
        screen.addTableControlGFC( "BuildingListTable", 3, 10, 317, 238, yResolution - 642, False, False, 32, 32, TableStyles.TABLE_STYLE_STANDARD ) # nur yResolution: +16 pro Balken
        screen.setStyle( "BuildingListTable", "Table_City_Style" )

        screen.setTableColumnHeader( "TradeRouteTable", 0, u"", 108 )
        screen.setTableColumnHeader( "TradeRouteTable", 1, u"", 118 )
        screen.setTableColumnHeader( "TradeRouteTable", 2, u"", 10 )
        screen.setTableColumnRightJustify( "TradeRouteTable", 1 )

        screen.setTableColumnHeader( "BuildingListTable", 0, u"", 108 )
        screen.setTableColumnHeader( "BuildingListTable", 1, u"", 118 )
        screen.setTableColumnHeader( "BuildingListTable", 2, u"", 10 )
        screen.setTableColumnRightJustify( "BuildingListTable", 1 )

        screen.show( "BuildingListBackground" )
        screen.show( "TradeRouteListBackground" )
        screen.show( "BuildingListLabel" )
        screen.show( "TradeRouteListLabel" )

        for i in range( 3 ):
          szName = "BonusPane" + str(i)
          screen.show( szName )
          szName = "BonusBack" + str(i)
          screen.show( szName )

        i = 0
        iNumBuildings = 0
        for i in range( gc.getNumBuildingInfos() ):
          if (pHeadSelectedCity.getNumBuilding(i) > 0) and gc.getBuildingInfo(i).getArtDefineTag() != "ART_DEF_BUILDING_FAKE":

            for k in range(pHeadSelectedCity.getNumBuilding(i)):

              szLeftBuffer = gc.getBuildingInfo(i).getDescription()
              szRightBuffer = u""
              bFirst = True

              if (pHeadSelectedCity.getNumActiveBuilding(i) > 0):
                iHealth = pHeadSelectedCity.getBuildingHealth(i)

                if (iHealth != 0):
                  if ( bFirst == False ):
                    szRightBuffer = szRightBuffer + ", "
                  else:
                    bFirst = False

                  if ( iHealth > 0 ):
                    szTempBuffer = u"+%d%c" %( iHealth, CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR) )
                    szRightBuffer = szRightBuffer + szTempBuffer
                  else:
                    szTempBuffer = u"+%d%c" %( -(iHealth), CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR) )
                    szRightBuffer = szRightBuffer + szTempBuffer

                iHappiness = pHeadSelectedCity.getBuildingHappiness(i)

                if (iHappiness != 0):
                  if ( bFirst == False ):
                    szRightBuffer = szRightBuffer + ", "
                  else:
                    bFirst = False

                  if ( iHappiness > 0 ):
                    szTempBuffer = u"+%d%c" %(iHappiness, CyGame().getSymbolID(FontSymbols.HAPPY_CHAR) )
                    szRightBuffer = szRightBuffer + szTempBuffer
                  else:
                    szTempBuffer = u"+%d%c" %( -(iHappiness), CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR) )
                    szRightBuffer = szRightBuffer + szTempBuffer

                for j in range( YieldTypes.NUM_YIELD_TYPES):
                  iYield = gc.getBuildingInfo(i).getYieldChange(j) + pHeadSelectedCity.getNumBuilding(i) * pHeadSelectedCity.getBuildingYieldChange(gc.getBuildingInfo(i).getBuildingClassType(), j)

                  if (iYield != 0):
                    if ( bFirst == False ):
                      szRightBuffer = szRightBuffer + ", "
                    else:
                      bFirst = False

                    if ( iYield > 0 ):
                      szTempBuffer = u"%s%d%c" %( "+", iYield, gc.getYieldInfo(j).getChar() )
                      szRightBuffer = szRightBuffer + szTempBuffer
                    else:
                      szTempBuffer = u"%s%d%c" %( "", iYield, gc.getYieldInfo(j).getChar() )
                      szRightBuffer = szRightBuffer + szTempBuffer

              for j in range(CommerceTypes.NUM_COMMERCE_TYPES):
                iCommerce = pHeadSelectedCity.getBuildingCommerceByBuilding(j, i) / pHeadSelectedCity.getNumBuilding(i)

                if (iCommerce != 0):
                  if ( bFirst == False ):
                    szRightBuffer = szRightBuffer + ", "
                  else:
                    bFirst = False

                  if ( iCommerce > 0 ):
                    szTempBuffer = u"%s%d%c" %( "+", iCommerce, gc.getCommerceInfo(j).getChar() )
                    szRightBuffer = szRightBuffer + szTempBuffer
                  else:
                    szTempBuffer = u"%s%d%c" %( "", iCommerce, gc.getCommerceInfo(j).getChar() )
                    szRightBuffer = szRightBuffer + szTempBuffer

              szBuffer = szLeftBuffer + "  " + szRightBuffer

              screen.appendTableRow( "BuildingListTable" )
              screen.setTableText( "BuildingListTable", 0, iNumBuildings, "<font=1>" + szLeftBuffer + "</font>", "", WidgetTypes.WIDGET_HELP_BUILDING, i, -1, CvUtil.FONT_LEFT_JUSTIFY )
              screen.setTableText( "BuildingListTable", 1, iNumBuildings, "<font=1>" + szRightBuffer + "</font>", "", WidgetTypes.WIDGET_HELP_BUILDING, i, -1, CvUtil.FONT_RIGHT_JUSTIFY )

              iNumBuildings = iNumBuildings + 1

        if ( iNumBuildings > g_iNumBuildings ):
          g_iNumBuildings = iNumBuildings

        iNumTradeRoutes = 0

        for i in range(gc.getDefineINT("MAX_TRADE_ROUTES")):
          pLoopCity = pHeadSelectedCity.getTradeCity(i)

          if (pLoopCity and pLoopCity.getOwner() >= 0):
            player = gc.getPlayer(pLoopCity.getOwner())
            szLeftBuffer = u"<color=%d,%d,%d,%d>%s</color>" %(player.getPlayerTextColorR(), player.getPlayerTextColorG(), player.getPlayerTextColorB(), player.getPlayerTextColorA(), pLoopCity.getName() )
            szRightBuffer = u""

            for j in range( YieldTypes.NUM_YIELD_TYPES ):
              iTradeProfit = pHeadSelectedCity.calculateTradeYield(j, pHeadSelectedCity.calculateTradeProfit(pLoopCity))

              if (iTradeProfit != 0):
                if ( iTradeProfit > 0 ):
                  szTempBuffer = u"%s%d%c" %( "+", iTradeProfit, gc.getYieldInfo(j).getChar() )
                  szRightBuffer = szRightBuffer + szTempBuffer
                else:
                  szTempBuffer = u"%s%d%c" %( "", iTradeProfit, gc.getYieldInfo(j).getChar() )
                  szRightBuffer = szRightBuffer + szTempBuffer

            screen.appendTableRow( "TradeRouteTable" )
            screen.setTableText( "TradeRouteTable", 0, iNumTradeRoutes, "<font=1>" + szLeftBuffer + "</font>", "", WidgetTypes.WIDGET_HELP_TRADE_ROUTE_CITY, i, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "TradeRouteTable", 1, iNumTradeRoutes, "<font=1>" + szRightBuffer + "</font>", "", WidgetTypes.WIDGET_HELP_TRADE_ROUTE_CITY, i, -1, CvUtil.FONT_RIGHT_JUSTIFY )

            iNumTradeRoutes = iNumTradeRoutes + 1

        if ( iNumTradeRoutes > g_iNumTradeRoutes ):
          g_iNumTradeRoutes = iNumTradeRoutes

        i = 0
        iLeftCount = 0
        iCenterCount = 0
        iRightCount = 0

        for i in range( gc.getNumBonusInfos() ):
          bHandled = False
          if ( pHeadSelectedCity.hasBonus(i) ):

            iHealth = pHeadSelectedCity.getBonusHealth(i)
            iHappiness = pHeadSelectedCity.getBonusHappiness(i)

            szBuffer = u""
            szLeadBuffer = u""

            szTempBuffer = u"<font=1>%c" %( gc.getBonusInfo(i).getChar() )
            szLeadBuffer = szLeadBuffer + szTempBuffer

            if (pHeadSelectedCity.getNumBonuses(i) > 1):
              szTempBuffer = u"(%d)" %( pHeadSelectedCity.getNumBonuses(i) )
              szLeadBuffer = szLeadBuffer + szTempBuffer

            szLeadBuffer = szLeadBuffer + "</font>"

            if (iHappiness != 0):
              if ( iHappiness > 0 ):
                szTempBuffer = u"<font=1>+%d%c</font>" %(iHappiness, CyGame().getSymbolID(FontSymbols.HAPPY_CHAR) )
              else:
                szTempBuffer = u"<font=1>+%d%c</font>" %( -iHappiness, CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR) )

              if ( iHealth > 0 ):
                szTempBuffer += u"<font=1>, +%d%c</font>" %( iHealth, CyGame().getSymbolID( FontSymbols.HEALTHY_CHAR ) )

              szName = "RightBonusItemLeft" + str(iRightCount)
              screen.setLabelAt( szName, "BonusBack2", szLeadBuffer, CvUtil.FONT_LEFT_JUSTIFY, 0, (iRightCount * 20) + 4, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, i, -1 )
              szName = "RightBonusItemRight" + str(iRightCount)
              screen.setLabelAt( szName, "BonusBack2", szTempBuffer, CvUtil.FONT_RIGHT_JUSTIFY, 102, (iRightCount * 20) + 4, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, i, -1 )

              iRightCount = iRightCount + 1

              bHandled = True

            if (iHealth != 0 and bHandled == False):
              if ( iHealth > 0 ):
                szTempBuffer = u"<font=1>+%d%c</font>" %( iHealth, CyGame().getSymbolID( FontSymbols.HEALTHY_CHAR ) )
              else:
                szTempBuffer = u"<font=1>+%d%c</font>" %( -iHealth, CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR) )

              szName = "CenterBonusItemLeft" + str(iCenterCount)
              screen.setLabelAt( szName, "BonusBack1", szLeadBuffer, CvUtil.FONT_LEFT_JUSTIFY, 0, (iCenterCount * 20) + 4, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, i, -1 )
              szName = "CenterBonusItemRight" + str(iCenterCount)
              screen.setLabelAt( szName, "BonusBack1", szTempBuffer, CvUtil.FONT_RIGHT_JUSTIFY, 62, (iCenterCount * 20) + 4, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, i, -1 )

              iCenterCount = iCenterCount + 1

              bHandled = True

            szBuffer = u""
            if ( not bHandled ):

              szName = "LeftBonusItem" + str(iLeftCount)
              screen.setLabelAt( szName, "BonusBack0", szLeadBuffer, CvUtil.FONT_LEFT_JUSTIFY, 0, (iLeftCount * 20) + 4, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_PEDIA_JUMP_TO_BONUS, i, -1 )

              iLeftCount = iLeftCount + 1

              bHandled = True

        g_iNumLeftBonus = iLeftCount
        g_iNumCenterBonus = iCenterCount
        g_iNumRightBonus = iRightCount

        iMaintenance = pHeadSelectedCity.getMaintenanceTimes100()

        szBuffer = localText.getText("INTERFACE_CITY_MAINTENANCE", ())

        screen.setLabel( "MaintenanceText", "Background", szBuffer, CvUtil.FONT_LEFT_JUSTIFY, 15, 126, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_HELP_MAINTENANCE, -1, -1 )
        screen.show( "MaintenanceText" )

        szBuffer = u"-%d.%02d %c" %(iMaintenance/100, iMaintenance%100, gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar())
        screen.setLabel( "MaintenanceAmountText", "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, 220, 125, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_HELP_MAINTENANCE, -1, -1 )
        screen.show( "MaintenanceAmountText" )

        szBuffer = u""

        # Alot of this code is just rewriten as it now only shows
        # religions the city has and has to deal with way more then
        lReligions = []
        for i in range(gc.getNumReligionInfos()):
          if (not pHeadSelectedCity.isHasReligion(i)):
            continue
          lReligions += [i]

        iCountReligions = len(lReligions)
        iMaxWidth = 250 #228
        iMaxButtons = iCountReligions
        if (iCountReligions < 8):
         iButtonSize = 24
         iButtonSpace = 10
        #elif (iCountReligions >= iMaxButtons):
         #iButtonSize = iMaxWidth / iMaxButtons
         #iButtonSpace = 0
        elif (iCountReligions == 8):
         iButtonSize = 24
         iButtonSpace = 5
        elif (iCountReligions == 9):
         iButtonSize = 24
         iButtonSpace = 2
        elif (iCountReligions == 10):
         iButtonSize = 21
         iButtonSpace = 2
        elif (iCountReligions == 11):
         iButtonSize = 20
         iButtonSpace = 1
        elif (iCountReligions == 12):
         iButtonSize = 18
         iButtonSpace = 1
        elif (iCountReligions == 13):
         iButtonSize = 18
         iButtonSpace = 0
        elif (iCountReligions == 14):
         iButtonSize = 16
         iButtonSpace = 0
        elif (iCountReligions == 15):
         iButtonSize = 15
         iButtonSpace = 0
        elif (iCountReligions == 16):
         iButtonSize = 14
         iButtonSpace = 0
        elif (iCountReligions == 17):
         iButtonSize = 13
         iButtonSpace = 0
        elif (iCountReligions == 18):
         iButtonSize = 13
         iButtonSpace = 0
        elif (37 > iCountReligions > 18):
         iMaxButtons = 18
         iButtonSize = 13
         iButtonSpace = 0
        elif (iCountReligions == 37) or (iCountReligions == 38):
         iMaxWidth = 240
         iMaxButtons = int(round(iCountReligions / 2.0, 0))# int(round(gc.getNumReligionInfos() / 2.0, 0))
         iButtonSize = iMaxWidth / iMaxButtons
         iButtonSpace = (iMaxWidth - (iButtonSize * iMaxButtons)) // (iMaxButtons - 1)
        else:
         iMaxButtons = int(round(iCountReligions / 2.0, 0))# int(round(gc.getNumReligionInfos() / 2.0, 0))
         iButtonSize = iMaxWidth / iMaxButtons
         iButtonSpace = (iMaxWidth - (iButtonSize * iMaxButtons)) // (iMaxButtons - 1)

        for ii in range(iCountReligions):
            i = lReligions[ii]
            xCoord = xResolution - 242 + ((ii % iMaxButtons) * (iButtonSize + iButtonSpace))
            #xCoord = xResolution - 242 + (i * 34) # Original Civ4 Code
            yCoord = 42 + iButtonSize * (ii // iMaxButtons)
            #yCoord = 42 # Original Civ4 Code

            bEnable = True

          #if pHeadSelectedCity.isHasReligion(i):

            if (pHeadSelectedCity.isHolyCityByType(i)):
              szTempBuffer = u"%c" %(gc.getReligionInfo(i).getHolyCityChar())
              #szName = "ReligionHolyCityDDS" + str(i)
              #screen.show( szName )
            else:
              szTempBuffer = u"%c" %(gc.getReligionInfo(i).getChar())
            szBuffer = szBuffer + szTempBuffer

            for j in range(CommerceTypes.NUM_COMMERCE_TYPES):
              iCommerce = pHeadSelectedCity.getReligionCommerceByReligion(j, i)

              if (iCommerce != 0):
                if ( iCommerce > 0 ):
                  szTempBuffer = u",%s%d%c" %("+", iCommerce, gc.getCommerceInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer
                else:
                  szTempBuffer = u",%s%d%c" %( "", iCommerce, gc.getCommerceInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer

            iHappiness = pHeadSelectedCity.getReligionHappiness(i)

            if (iHappiness != 0):
              if ( iHappiness > 0 ):
                szTempBuffer = u",+%d%c" %(iHappiness, CyGame().getSymbolID(FontSymbols.HAPPY_CHAR) )
                szBuffer = szBuffer + szTempBuffer
              else:
                szTempBuffer = u",+%d%c" %(-(iHappiness), CyGame().getSymbolID(FontSymbols.UNHAPPY_CHAR) )
                szBuffer = szBuffer + szTempBuffer

            szBuffer = szBuffer + " "

            szButton = gc.getReligionInfo(i).getButton()

          #else:
          #  bEnable = False
          #  szButton = gc.getReligionInfo(i).getButton()

            szName = "ReligionDDS" + str(i)
            screen.setImageButton( szName, szButton, xCoord, yCoord, 24, 24, WidgetTypes.WIDGET_HELP_RELIGION_CITY, i, -1 )
            screen.enable( szName, bEnable )
            screen.show( szName )

            # Holy City Overlay
            if (pHeadSelectedCity.isHolyCityByType(i)):
              szName = "ReligionHolyCityDDS" + str(i)
              screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_HOLYCITY_OVERLAY").getPath(), xCoord, yCoord, iButtonSize, iButtonSize, WidgetTypes.WIDGET_HELP_RELIGION_CITY, i, -1 )
              screen.show( szName )


        # Alot of this code is just rewriten as it now only shows
        # corporations the city has and is setup to handle more then 7
        lCorporations = []
        for i in range(gc.getNumCorporationInfos()):
          if (not pHeadSelectedCity.isHasCorporation(i)):
            continue
          lCorporations += [i]
        iCountCorporations = len(lCorporations)
        iMaxWidth = 250#228
        iMaxButtons = iCountCorporations
        if (iCountCorporations < 8):
               iButtonSize = 24
               iButtonSpace = 10
        #elif (iCountCorporations >= iMaxButtons):
               #iButtonSize = iMaxWidth / iMaxButtons
               #iButtonSpace = 0
        elif (iCountCorporations == 8):
               iButtonSize = 24
               iButtonSpace = 5
        elif (iCountCorporations == 9):
               iButtonSize = 24
               iButtonSpace = 2
        elif (iCountCorporations == 10):
               iButtonSize = 21
               iButtonSpace = 2
        elif (iCountCorporations == 11):
               iButtonSize = 20
               iButtonSpace = 1
        elif (iCountCorporations == 12):
               iButtonSize = 18
               iButtonSpace = 1
        elif (iCountCorporations == 13):
               iButtonSize = 18
               iButtonSpace = 0
        elif (iCountCorporations == 14):
               iButtonSize = 16
               iButtonSpace = 0
        elif (iCountCorporations == 15):
               iButtonSize = 15
               iButtonSpace = 0
        elif (iCountCorporations == 16):
               iButtonSize = 14
               iButtonSpace = 0
        elif (iCountCorporations == 17):
               iButtonSize = 13
               iButtonSpace = 0
        elif (iCountCorporations == 18):
               iButtonSize = 13
               iButtonSpace = 0
        elif (37 > iCountCorporations > 18):
               iMaxButtons = 18
               iButtonSize = 13
               iButtonSpace = 0
        elif (iCountCorporations == 37) or (iCountCorporations == 38):
               iMaxWidth = 240
               iMaxButtons = int(round(iCountCorporations / 2.0, 0))# int(round(gc.getNumCorporationInfos() / 2.0, 0))
               iButtonSize = iMaxWidth / iMaxButtons
               iButtonSpace = (iMaxWidth - (iButtonSize * iMaxButtons)) // (iMaxButtons - 1)
        else:
               iMaxButtons = int(round(iCountCorporations / 2.0, 0))# int(round(gc.getNumCorporationInfos() / 2.0, 0))
               iButtonSize = iMaxWidth / iMaxButtons
               iButtonSpace = (iMaxWidth - (iButtonSize * iMaxButtons)) // (iMaxButtons - 1)
        for ii in range(iCountCorporations):
            i = lCorporations[ii]
            xCoord = xResolution - 242 + ((ii % iMaxButtons) * (iButtonSize + iButtonSpace))
          #xCoord = xResolution - 242 + (i * 34) # Original Civ4 Code
            yCoord = 66 + iButtonSize * (ii // iMaxButtons)
          #yCoord = 66 # Original Civ4 Code

            bEnable = True

          #if (pHeadSelectedCity.isHasCorporation(i)):
            if (pHeadSelectedCity.isHeadquartersByType(i)):
              szTempBuffer = u"%c" %(gc.getCorporationInfo(i).getHeadquarterChar())
              #szName = "CorporationHeadquarterDDS" + str(i)
              #screen.show( szName )
            else:
              szTempBuffer = u"%c" %(gc.getCorporationInfo(i).getChar())
            szBuffer = szBuffer + szTempBuffer

            for j in range(YieldTypes.NUM_YIELD_TYPES):
              iYield = pHeadSelectedCity.getCorporationYieldByCorporation(j, i)

              if (iYield != 0):
                if ( iYield > 0 ):
                  szTempBuffer = u",%s%d%c" %("+", iYield, gc.getYieldInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer
                else:
                  szTempBuffer = u",%s%d%c" %( "", iYield, gc.getYieldInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer

            for j in range(CommerceTypes.NUM_COMMERCE_TYPES):
              iCommerce = pHeadSelectedCity.getCorporationCommerceByCorporation(j, i)

              if (iCommerce != 0):
                if ( iCommerce > 0 ):
                  szTempBuffer = u",%s%d%c" %("+", iCommerce, gc.getCommerceInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer
                else:
                  szTempBuffer = u",%s%d%c" %( "", iCommerce, gc.getCommerceInfo(j).getChar() )
                  szBuffer = szBuffer + szTempBuffer

            szBuffer += " "

            szButton = gc.getCorporationInfo(i).getButton()

          #else:
          #  bEnable = False
          #  szButton = gc.getCorporationInfo(i).getButton()

            szName = "CorporationDDS" + str(i)
            screen.setImageButton( szName, szButton, xCoord, yCoord, 24, 24, WidgetTypes.WIDGET_HELP_CORPORATION_CITY, i, -1 )
            screen.enable( szName, bEnable )
            screen.show( szName )
            # Holy City Overlay
            if (pHeadSelectedCity.isHeadquartersByType(i)):
              szName = "CorporationHeadquarterDDS" + str(i)
              screen.addDDSGFC( szName, ArtFileMgr.getInterfaceArtInfo("INTERFACE_HOLYCITY_OVERLAY").getPath(), xCoord, yCoord, iButtonSize, iButtonSize, WidgetTypes.WIDGET_HELP_CORPORATION_CITY, i, -1 )
              screen.show( szName )
        # Religion und Corporation END


        # Allgemeine Variablen für Revolten und Rebellionen
        pCity = pHeadSelectedCity
        pPlot = gc.getMap().plot(pCity.getX(), pCity.getY())
        iPlayer = pHeadSelectedCity.getOwner()
        pPlayer = gc.getPlayer(iPlayer)
        iNumCities = gc.getPlayer(iPlayer).getNumCities()
        iDistance = plotDistance(gc.getPlayer(iPlayer).getCapitalCity().getX(), gc.getPlayer(iPlayer).getCapitalCity().getY(), pCity.getX(), pCity.getY())
        iCitySlaves = pCity.getFreeSpecialistCount(16) + pCity.getFreeSpecialistCount(17) + pCity.getFreeSpecialistCount(18) # SPECIALIST_SLAVE = 16,17,18
        iCityGlads = pCity.getFreeSpecialistCount(15) # SPECIALIST_GLADIATOR = 15
        iCityPop = pCity.getPopulation()

        # Revolten-Gefahrenanzeige und -texte
        bRevoltDanger = False
        szBuffer = ""

        if pCity.goodHealth() < pCity.badHealth(0) and iCityPop > 4:
          if iCityPop > 8: szBuffer = localText.getText("TXT_KEY_MAIN_UNHEALTHY_PEST", (CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR), () ))
          else: szBuffer = localText.getText("TXT_KEY_MAIN_UNHEALTHY_LEPRA", (CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR), () ))
        elif iCityGlads + iCitySlaves > iCityPop:
          if iCityGlads > iCitySlaves:  szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_GLADS", (CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR), () ))
          else: szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_SLAVES", (CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR), () ))
        elif iCityPop > 3:

          iForeignCulture = 0
          if pCity.getOriginalOwner() != iPlayer and gc.getPlayer(pCity.getOriginalOwner()).isAlive():
            iForeignCulture = pHeadSelectedCity.plot().calculateCulturePercent(gc.getPlayer(pCity.getOriginalOwner()).getTeam())

          if iForeignCulture > 19:
            # Chance Kultur/10 - 1% pro Einheit
            iChance = int(iForeignCulture/10) - pPlot.getNumDefenders(iPlayer)
            if iChance > 0:
              szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_ALTE_HEIMAT", (CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR), (iChance) ))

          if szBuffer == "":
            iRel = pPlayer.getStateReligion()
            if pPlayer.getAnarchyTurns() > 0:
              szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_ANARCHY", (CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR), () ))
            elif iRel != -1 and not pCity.isHasReligion(iRel):
              szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_RELIGION", (CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR), () ))
            elif pCity.unhappyLevel(0) > pCity.happyLevel():
              szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_UNHAPPY", (CyGame().getSymbolID(FontSymbols.ANGRY_POP_CHAR), () ))
            elif pPlayer.getCommercePercent(0) > 50:
              iChance = int( (pPlayer.getCommercePercent(0) - 50) / 5 )
              # Pro Happy Citizen 5% Nachlass
              iChance = iChance - pCity.happyLevel() + pCity.unhappyLevel(0)
              if iChance > 0:
                szBuffer = localText.getText("TXT_KEY_MAIN_REVOLT_TAXES", (gc.getCommerceInfo(CommerceTypes.COMMERCE_GOLD).getChar(), (iChance) ))


        if szBuffer != "": bRevoltDanger = True
        else: szBuffer = localText.getText("TXT_KEY_MAIN_NO_DANGER", (CyGame().getSymbolID(FontSymbols.HAPPY_CHAR), () ))

        screen.setLabel( "PAE_RevoltText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 327, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "PAE_RevoltText", HitTestTypes.HITTEST_NOHIT )
        screen.show( "PAE_RevoltText" )

        if bRevoltDanger: screen.setStackedBarColorsRGB( "PAE_RevoltBar", 0, 255, 0, 0, 100 ) # red
        else: screen.setStackedBarColorsRGB( "PAE_RevoltBar", 0, 0, 255, 0, 100 ) # green
        screen.setBarPercentage( "PAE_RevoltBar", 0, 1.0 ) # immer 1 !

        screen.show( "PAE_RevoltBar" )


        # Emigration Bar / Emigrant -----------------------------------
        iTech = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_COLONIZATION')
        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)
        iChance = 0

        if iPlayer == gc.getBARBARIAN_PLAYER(): szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_AB_1",("",))
        elif not pTeam.isHasTech(iTech): szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_AB_2",("",))
        elif iCityPop < 4: szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_AB_3",("",))
        else:
          iCityUnhappy = pCity.unhappyLevel(0) - pCity.happyLevel()
          iCityUnhealthy = pCity.badHealth(False) - pCity.goodHealth()
          if iCityUnhappy > 0 or iCityUnhealthy > 0:
            if iCityUnhappy < 0: iCityUnhappy = 0
            if iCityUnhealthy < 0: iCityUnhealthy = 0
            iChance = (iCityUnhappy + iCityUnhealthy) * 2 # * iCityPop

            if iCityUnhappy > 0 and iCityUnhealthy > 0: szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_DANGER_1",("",iChance))
            elif iCityUnhappy > 0: szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_DANGER_2",("",iChance))
            else: szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_DANGER_3",("",iChance))
          else: szBuffer = localText.getText("TXT_KEY_MAIN_EMIGRATE_NO_DANGER",("",))


        screen.setLabel( "PAE_EmigrationText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 303, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "PAE_EmigrationText", HitTestTypes.HITTEST_NOHIT )
        screen.show( "PAE_EmigrationText" )

        # Bar 0 ist Balken von rechts / Bar 1 = Hintergrund
        screen.setStackedBarColorsRGB( "PAE_EmigrationBar", 1, 255, 0, 0, 100 ) # red
        if iChance > 5: screen.setStackedBarColorsRGB( "PAE_EmigrationBar", 0, 255, 255, 0, 100 ) # yellow
        else: screen.setStackedBarColorsRGB( "PAE_EmigrationBar", 0, 0, 255, 0, 100 ) # green
        fPercent = iChance * 0.1
        if fPercent < 0.0: fPercent = 0.0
        screen.setBarPercentage( "PAE_EmigrationBar", 0, 1.0 - fPercent ) # 0.8
        screen.setBarPercentage( "PAE_EmigrationBar", 1, 1.0 ) # immer 1 !

        screen.show( "PAE_EmigrationBar" )


        # Supply Bar / City supply of units ---------------------------
        # PAE V: Food Prod * 2 (capital: * 3)
        #iCityFoodDifference = pCity.foodDifference(True)
        iCityUnits = pPlot.getNumDefenders(iPlayer)
        # iCityPop

        #if pCity.isCapital(): iFactor = 3
        #else: iFactor = 2
        iFactor = 1
        iCityMaintainUnits = pCity.getYieldRate(0) * iFactor

        #iCityMaintainUnits = iCityFoodDifference * 2 + iCityPop * 2
        if iCityMaintainUnits - iCityUnits < 0:
          screen.setStackedBarColorsRGB( "PAE_SupplyBar", 0, 255, 0, 0, 100 ) # red
          szBuffer = localText.getText("TXT_KEY_MAIN_CITY_SUPPLY_DANGER",(iCityUnits,iCityMaintainUnits))
        #elif iCityMaintainUnits - iCityUnits == 0:
        #  screen.setStackedBarColorsRGB( "PAE_SupplyBar", 0, 255, 200, 0, 100 ) # kind of orange
        #  szBuffer = localText.getText("TXT_KEY_MAIN_CITY_SUPPLY_STAGNATION",(iCityUnits,iCityMaintainUnits))
        else:
          screen.setStackedBarColorsRGB( "PAE_SupplyBar", 0, 0, 255, 0, 100 ) # green
          szBuffer = localText.getText("TXT_KEY_MAIN_CITY_SUPPLY",(iCityUnits,iCityMaintainUnits))

        screen.setBarPercentage( "PAE_SupplyBar", 0, 1.0 )
        screen.setLabel( "PAE_SupplyText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 279, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "PAE_SupplyText", HitTestTypes.HITTEST_NOHIT )
        screen.show( "PAE_SupplyText" )

        screen.show( "PAE_SupplyBar" )


        # Slaves Bar / City slaves maintenance of units ---------------------------
        # PAE V: allowed Slaves = City Pop !
        # pTeam
        # iCityUnits
        # iCityPop
        # iCitySlaves
        # iCityGlads

        iTech  = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_ENSLAVEMENT')
        iTech2 = CvUtil.findInfoTypeNum(gc.getTechInfo,gc.getNumTechInfos(),'TECH_GLADIATOR')
        # TODO: Slave-Char ohne extra Bonus
        iSlaveIcon = gc.getInfoTypeForString("BONUS_THRAKIEN")
        iGladsIcon = gc.getInfoTypeForString("BONUS_BRONZE")

        szBuffer = u"%d %c " %(iCitySlaves,gc.getBonusInfo(iSlaveIcon).getChar())
        if not pTeam.isHasTech(iTech): szBuffer += localText.getText("TXT_KEY_MAIN_CITY_SLAVES_AB",("",))
        else:
          #szBuffer += localText.getText("TXT_KEY_MAIN_CITY_SLAVES_N_GLADS_CALC",(iCitySlaves,iCityPop))

          szBuffer += u"%d %c " %(iCityGlads,gc.getBonusInfo(iGladsIcon).getChar())
          if not pTeam.isHasTech(iTech): szBuffer += localText.getText("TXT_KEY_MAIN_CITY_GLADS_AB",("",))
          #else: szBuffer += localText.getText("TXT_KEY_MAIN_CITY_SLAVES_N_GLADS_CALC",(iCityGlads,iCityPop))

        szBuffer += u" (%d/%d)" %(iCitySlaves + iCityGlads,iCityPop)

        if iCitySlaves + iCityGlads > iCityPop:
          screen.setStackedBarColorsRGB( "PAE_SlavesBar", 0, 255, 0, 0, 100 ) # red
        else:
          screen.setStackedBarColorsRGB( "PAE_SlavesBar", 0, 0, 255, 0, 100 ) # green

        screen.setBarPercentage( "PAE_SlavesBar", 0, 1.0 )
        screen.setLabel( "PAE_SlavesText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 255, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "PAE_SlavesText", HitTestTypes.HITTEST_NOHIT )
        screen.show( "PAE_SlavesText" )

        screen.show( "PAE_SlavesBar" )


        # Rebellionsgefahr
#        iNumCities = gc.getPlayer(iPlayer).getNumCities()
#        iDistance = plotDistance(gc.getPlayer(iPlayer).getCapitalCity().getX(), gc.getPlayer(iPlayer).getCapitalCity().getY(), pCity.getX(), pCity.getY())
#
#        # Ab Klassik, wo es eine Hauptstadt geben sollte!
#        if pCity.getPopulation() > 4 and ( gc.getPlayer(iPlayer).getCurrentEra() >= 3 and iDistance > 10 or ( pCity.getOriginalOwner() != iPlayer and pCity.getGameTurnAcquired() + 100 > gc.getGame().getGameTurn() ) ):
#         iBuilding1 = CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_GREAT_PALACE')
#         if not (pCity.isHasBuilding(iBuilding1) or pCity.isCapital()):
#
#          iChanceOfRebellion = pPlayer.getNumCities() * 2
#
#          iChanceOfRebellion += iDistance * 2
#
#          if pCity.isHasBuilding(CvUtil.findInfoTypeNum(gc.getBuildingInfo, gc.getNumBuildingInfos(), 'BUILDING_COURTHOUSE')): iChanceOfRebellion -= 10
#
#          iChanceOfRebellion -= pCity.getNumNationalWonders() * 10
#
#          iChanceOfRebellion -= pCity.getNumWorldWonders() * 10
#
#          iChanceOfRebellion += ( pCity.unhappyLevel(0) - pCity.happyLevel() ) * 10
#
#          iChanceOfRebellion += pPlayer.getAnarchyTurns() * 10
#
#          iChanceOfRebellion += pCity.foodDifference(1) * 10
#
#          iChanceOfRebellion -= pPlot.getNumUnits() * 10
#
#          if not pCity.isConnectedToCapital(iPlayer): iChanceOfRebellion += 30
#
#          if pCity.getOccupationTimer() > 0: iChanceOfRebellion += pCity.getOccupationTimer() * 10
#
#          if gc.getPlayer(iPlayer).getCapitalCity().getOccupationTimer() > 0: iChanceOfRebellion += pCity.getOccupationTimer() * 20
#
#          if not pCity.isHasReligion(pPlayer.getStateReligion()): iChanceOfRebellion += 20
#
#          if pPlayer.isCivic(1)  or   pPlayer.isCivic(2): iChanceOfRebellion += 10
#          if pPlayer.isCivic(18): iChanceOfRebellion += 10
#          if pPlayer.isCivic(16): iChanceOfRebellion += 20
#          if pPlayer.isCivic(3)  or   pPlayer.isCivic(4) : iChanceOfRebellion -= 20
#          if pPlayer.isCivic(1)  and  pPlayer.isCivic(9) : iChanceOfRebellion += 10
#          if pPlayer.isCivic(4)  and  pPlayer.isCivic(8) : iChanceOfRebellion += 10
#          if pPlayer.isCivic(24) and  pPlayer.isCivic(9) : iChanceOfRebellion += 10
#          if pPlayer.isCivic(14) and  pPlayer.isCivic(18): iChanceOfRebellion += 10
#          if pPlayer.isCivic(14) and (pPlayer.isCivic(1)  or pPlayer.isCivic(2)) : iChanceOfRebellion += 10
#          if pPlayer.isCivic(14) and (pPlayer.isCivic(17) or pPlayer.isCivic(19)): iChanceOfRebellion -= 20
#
#          if pPlayer.getCommercePercent(0) > 50: iChanceOfRebellion += pPlayer.getCommercePercent(0) - 50
#
#          # Verstärkung, weil nur jede 4te Runde check
#          iChanceOfRebellion = iChanceOfRebellion * 3
#
#          fPercent = iChanceOfRebellion / 10.0
#
#          if fPercent < 0: fPercent = 0.1
#          elif fPercent > 100: fPercent = 100.0
#
#         else:
#          fPercent = 0.0
#        else:
#         fPercent = 0.0
#
#
#        szBuffer = localText.getText("TXT_KEY_MAIN_REBELLION_1", (CyGame().getSymbolID(FontSymbols.OCCUPATION_CHAR), str(round(fPercent,1)) ))
#        screen.setLabel( "PAE_RebellionText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 287, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
#        screen.setHitTest( "PAE_RebellionText", HitTestTypes.HITTEST_NOHIT )
#        screen.show( "PAE_RebellionText" )
#
#        # Hintergrund ist rot
#        screen.setStackedBarColorsRGB( "PAE_RebellionBar", 0, 255, 0, 0, 100 ) # red
#        if fPercent > 4: screen.setStackedBarColorsRGB( "PAE_RebellionBar", 1, 255, 255, 0, 100 ) # yellow
#        else: screen.setStackedBarColorsRGB( "PAE_RebellionBar", 1, 0, 255, 0, 100 ) # green
#        screen.setBarPercentage( "PAE_RebellionBar", 0, fPercent / 10 ) # 0.8
#        screen.setBarPercentage( "PAE_RebellionBar", 1, 1.0 ) # immer 1 !
#
#        screen.show( "PAE_RebellionBar" )


        # Stability against the enemy / renegade city )

        # ------ ab PAE V: soll nur mehr Stadt betreffen
        iBuilding = gc.getInfoTypeForString("BUILDING_STADT")
        # Berechnung
        if not pCity.isCapital() and pCity.isHasBuilding(iBuilding):

          # Anz Einheiten im Umkreis von 1 Feld, mit denen man im Krieg ist (military units)
          iUnitAnzahl = 0
          for i in range(3):
            for j in range(3):
              loopPlot = gc.getMap().plot(pPlot.getX() + i - 1, pPlot.getY() + j - 1)
              for iUnit in range (loopPlot.getNumUnits()):
                if loopPlot.getUnit(iUnit).canFight():
                  if gc.getTeam(pPlot.getOwner()).isAtWar(gc.getPlayer(loopPlot.getUnit(iUnit).getOwner()).getTeam()): iUnitAnzahl += 1

          # Anz Einheiten in der Stadt (military units)
          iUnitCity = i = iChanceUnits = 0
          for i in range (pPlot.getNumUnits()):
            if pPlot.getUnit(i).canFight():
              iUnitCity += 1
              # loyal units ?
              if pPlot.getUnit(i).isHasPromotion(0): iChanceUnits += 3
              else: iChanceUnits += 1

          # Verhältnis 1:4
          # gemeinsamen Nenner herausfinden
          if iUnitAnzahl == iUnitCity:
           iV1 = iV2 = 1
          elif iUnitAnzahl < iUnitCity:
            if iUnitAnzahl < 1:
              iV1 = 1
              iV2 = 0
            else:
              iV1 = int(iUnitCity / iUnitAnzahl)
              iV2 = 1
          else:
            if iUnitCity < 1:
              iV1 = 0
              iV2 = 1
            else:
              iV1 = 1
              iV2 = int(iUnitAnzahl / iUnitCity)

          # Per defense point +1%
          iChanceDefense = pCity.getNaturalDefense() + pCity.getTotalDefense(0) - pCity.getDefenseDamage()

          # Per happy smile +5%
          iChanceHappiness = (pCity.happyLevel() - pCity.unhappyLevel(0)) * 2

          # Wonders: 1st +20%, 2nd +16%, 3rd +12%, 8, 4, 0
          iNumNWs = pCity.getNumNationalWonders()
          if iNumNWs < 6: iChanceNWs = iNumNWs * (11 - iNumNWs) * 2
          else: iChanceNWs = 60
          iNumWWs = pCity.getNumWorldWonders()
          if iNumWWs < 6: iChanceWWs = iNumWWs * (11 - iNumWWs) * 2
          else: iChanceWWs = 60

          # City population +5% each pop
          iChancePop = pCity.getPopulation() * 2

          # City connected with capital?
          if not pCity.isConnectedToCapital(pCity.getOwner()): iChancePop -= 10
          else: iChancePop += 10

          # bei negativ Nahrung - !
          iChancePop += pCity.foodDifference(1) * 5

          # Total
          iChanceTotal = iChanceUnits + iChanceDefense + iChanceHappiness + iChanceNWs + iChanceWWs + iChancePop - iUnitAnzahl

          if iUnitAnzahl < iUnitCity * 5 or pCity.getPopulation() < 2:
            fPercent = 1.0
          else:
            if iChanceTotal < 100:
              fPercent = iChanceTotal / 100.0
#            else:
              # there is always a chance of 1%
#              iChanceTotal = 99
#              fPercent = 1.0

          szBuffer = localText.getText("TXT_KEY_MAIN_REBELLION_2", (iChanceTotal, str(iV1)+":"+str(iV2)))

        else:
          fPercent = 1.0
          szBuffer = localText.getText("TXT_KEY_MAIN_REBELLION_3", (CyGame().getSymbolID(FontSymbols.DEFENSIVE_PACT_CHAR),()))


        screen.setLabel( "PAE_Rebellion2Text", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 231, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "PAE_Rebellion2Text", HitTestTypes.HITTEST_NOHIT )
        screen.show( "PAE_Rebellion2Text" )

        if fPercent < 0.5: screen.setStackedBarColorsRGB( "PAE_Rebellion2Bar", 0, 255, 255, 0, 100 ) # yellow
        else: screen.setStackedBarColorsRGB( "PAE_Rebellion2Bar", 0, 0, 255, 0, 100 ) # green
        screen.setStackedBarColorsRGB( "PAE_Rebellion2Bar", 1, 255, 0, 0, 100 ) # red
        screen.setBarPercentage( "PAE_Rebellion2Bar", 0, fPercent )
        screen.setBarPercentage( "PAE_Rebellion2Bar", 1, 1.0 )

        screen.show( "PAE_Rebellion2Bar" )

        szBuffer = u"%d%% %s" %(pHeadSelectedCity.plot().calculateCulturePercent(pHeadSelectedCity.getOwner()), gc.getPlayer(pHeadSelectedCity.getOwner()).getCivilizationAdjective(0) )
        screen.setLabel( "NationalityText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 205, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
        screen.setHitTest( "NationalityText", HitTestTypes.HITTEST_NOHIT )
        screen.show( "NationalityText" )
        iRemainder = 0
        iWhichBar = 0
        for h in range( gc.getMAX_PLAYERS() ):
          if ( gc.getPlayer(h).isAlive() ):
            fPercent = pHeadSelectedCity.plot().calculateCulturePercent(h)
            if ( fPercent != 0 ):
              fPercent = fPercent / 100.0
              screen.setStackedBarColorsRGB( "NationalityBar", iWhichBar, gc.getPlayer(h).getPlayerTextColorR(), gc.getPlayer(h).getPlayerTextColorG(), gc.getPlayer(h).getPlayerTextColorB(), gc.getPlayer(h).getPlayerTextColorA() )
              if ( iRemainder == 1 ):
                screen.setBarPercentage( "NationalityBar", iWhichBar, fPercent )
              else:
                screen.setBarPercentage( "NationalityBar", iWhichBar, fPercent / ( 1 - iRemainder ) )
              iRemainder += fPercent
              iWhichBar += 1
        screen.show( "NationalityBar" )

        iDefenseModifier = pHeadSelectedCity.getDefenseModifier(False)

        if (iDefenseModifier != 0):
          szBuffer = localText.getText("TXT_KEY_MAIN_CITY_DEFENSE", (CyGame().getSymbolID(FontSymbols.DEFENSE_CHAR), iDefenseModifier))

          if (pHeadSelectedCity.getDefenseDamage() > 0):
            szTempBuffer = u" (%d%%)" %( ( ( gc.getMAX_CITY_DEFENSE_DAMAGE() - pHeadSelectedCity.getDefenseDamage() ) * 100 ) / gc.getMAX_CITY_DEFENSE_DAMAGE() )
            szBuffer = szBuffer + szTempBuffer
          szNewBuffer = "<font=4>"
          szNewBuffer = szNewBuffer + szBuffer
          szNewBuffer = szNewBuffer + "</font>"
          screen.setLabel( "DefenseText", "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, xResolution - 270, 40, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_HELP_DEFENSE, -1, -1 )
          screen.show( "DefenseText" )

        if ( pHeadSelectedCity.getCultureLevel != CultureLevelTypes.NO_CULTURELEVEL ):
          iRate = pHeadSelectedCity.getCommerceRateTimes100(CommerceTypes.COMMERCE_CULTURE)
          if (iRate%100 == 0):
            szBuffer = localText.getText("INTERFACE_CITY_COMMERCE_RATE", (gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar(), gc.getCultureLevelInfo(pHeadSelectedCity.getCultureLevel()).getTextKey(), iRate/100))
          else:
            szRate = u"+%d.%02d" % (iRate/100, iRate%100)
            szBuffer = localText.getText("INTERFACE_CITY_COMMERCE_RATE_FLOAT", (gc.getCommerceInfo(CommerceTypes.COMMERCE_CULTURE).getChar(), gc.getCultureLevelInfo(pHeadSelectedCity.getCultureLevel()).getTextKey(), szRate))
          screen.setLabel( "CultureText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, 125, yResolution - 182, -1.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.setHitTest( "CultureText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "CultureText" )

        if ((pHeadSelectedCity.getGreatPeopleProgress() > 0) or (pHeadSelectedCity.getGreatPeopleRate() > 0)):
          szBuffer = localText.getText("INTERFACE_CITY_GREATPEOPLE_RATE", (CyGame().getSymbolID(FontSymbols.GREAT_PEOPLE_CHAR), pHeadSelectedCity.getGreatPeopleRate()))

          screen.setLabel( "GreatPeopleText", "Background", szBuffer, CvUtil.FONT_CENTER_JUSTIFY, xResolution - 146, yResolution - 176, -1.3, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
          screen.setHitTest( "GreatPeopleText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "GreatPeopleText" )

          iFirst = float(pHeadSelectedCity.getGreatPeopleProgress()) / float( gc.getPlayer( pHeadSelectedCity.getOwner() ).greatPeopleThreshold(False) )
          screen.setBarPercentage( "GreatPeopleBar", InfoBarTypes.INFOBAR_STORED, iFirst )
          if ( iFirst == 1 ):
            screen.setBarPercentage( "GreatPeopleBar", InfoBarTypes.INFOBAR_RATE, ( float(pHeadSelectedCity.getGreatPeopleRate()) / float( gc.getPlayer( pHeadSelectedCity.getOwner() ).greatPeopleThreshold(False) ) ) )
          else:
            screen.setBarPercentage( "GreatPeopleBar", InfoBarTypes.INFOBAR_RATE, ( ( float(pHeadSelectedCity.getGreatPeopleRate()) / float( gc.getPlayer( pHeadSelectedCity.getOwner() ).greatPeopleThreshold(False) ) ) ) / ( 1 - iFirst ) )
          screen.show( "GreatPeopleBar" )

        iFirst = float(pHeadSelectedCity.getCultureTimes100(pHeadSelectedCity.getOwner())) / float(100 * pHeadSelectedCity.getCultureThreshold())
        screen.setBarPercentage( "CultureBar", InfoBarTypes.INFOBAR_STORED, iFirst )
        if ( iFirst == 1 ):
          screen.setBarPercentage( "CultureBar", InfoBarTypes.INFOBAR_RATE, ( float(pHeadSelectedCity.getCommerceRate(CommerceTypes.COMMERCE_CULTURE)) / float(pHeadSelectedCity.getCultureThreshold()) ) )
        else:
          screen.setBarPercentage( "CultureBar", InfoBarTypes.INFOBAR_RATE, ( ( float(pHeadSelectedCity.getCommerceRate(CommerceTypes.COMMERCE_CULTURE)) / float(pHeadSelectedCity.getCultureThreshold()) ) ) / ( 1 - iFirst ) )
        screen.show( "CultureBar" )

    else:

      # Help Text Area
      if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
        screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 172, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )
      else:
        screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 50, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )

      screen.hide( "InterfaceTopLeftBackgroundWidget" )
      screen.hide( "InterfaceTopRightBackgroundWidget" )
      screen.hide( "InterfaceCenterLeftBackgroundWidget" )
      screen.hide( "CityScreenTopWidget" )
      screen.hide( "CityNameBackground" )
      screen.hide( "TopCityPanelLeft" )
      screen.hide( "TopCityPanelRight" )
      screen.hide( "CityScreenAdjustPanel" )
      screen.hide( "InterfaceCenterRightBackgroundWidget" )

      if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
        self.setMinimapButtonVisibility(True)

    return 0

  # Will update the info pane strings
  def updateInfoPaneStrings( self ):

    iRow = 0

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    pHeadSelectedCity = CyInterface().getHeadSelectedCity()
    pHeadSelectedUnit = CyInterface().getHeadSelectedUnit()

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    bShift = CyInterface().shiftKey()

    screen.addPanel( "SelectedUnitPanel", u"", u"", True, False, 8, yResolution - 140, 280, 130, PanelStyles.PANEL_STYLE_STANDARD )
    screen.setStyle( "SelectedUnitPanel", "Panel_Game_HudStat_Style" )
    screen.hide( "SelectedUnitPanel" )

    screen.addTableControlGFC( "SelectedUnitText", 3, 6, yResolution - 109, 188, 102, False, False, 32, 32, TableStyles.TABLE_STYLE_STANDARD )
    screen.setStyle( "SelectedUnitText", "Table_EmptyScroll_Style" )
    screen.hide( "SelectedUnitText" )
    screen.hide( "SelectedUnitLabel" )
    # PAE Unit Detail Promo Icons:
    # PAE: Unit Combat Type
    screen.hide( "SelectedUnitCombatType" )
    # PAE Unit Ethnic und Religion
    screen.hide( "SelectedUnitEthnic" )
    screen.hide( "SelectedUnitReligion" )
    # PAE Ranking etc
    screen.hide( "SelectedUnitLoyalty" )
    screen.hide( "SelectedBadMoral" )
    screen.hide( "SelectedUnitCombatRank" )
    screen.hide( "SelectedUnitRang" )
    screen.hide( "SelectedUnitTrait" )
    screen.hide( "SelectedUnitFormation" )
    screen.hide( "SelectedUnitHero" )
    # PAE Trade Infos
    screen.addTableControlGFC( "SelectedTradeText", 1, 6, yResolution - 40, 300, 32, False, False, 32, 32, TableStyles.TABLE_STYLE_STANDARD )
    screen.setStyle( "SelectedTradeText", "Table_EmptyScroll_Style" )
    screen.hide( "SelectedTradeText" )


    screen.addTableControlGFC( "SelectedCityText", 3, 10, yResolution - 139, 183, 128, False, False, 32, 32, TableStyles.TABLE_STYLE_STANDARD )
    screen.setStyle( "SelectedCityText", "Table_EmptyScroll_Style" )
    screen.hide( "SelectedCityText" )

    for i in range(gc.getNumPromotionInfos()):
      szName = "PromotionButton" + str(i)
      screen.hide( szName )


# BUG - Stack Promotions - start
      szName = "PromotionButtonCircle" + str(i)
      screen.hide( szName )
      szName = "PromotionButtonCount" + str(i)
      screen.hide( szName )
# BUG - Stack Promotions - end

# PAE - Unit Info Bar - start
    UnitBarType = ""
    iValue1 = 0
    iValue2 = 0
    screen.hide( "UnitInfoBar" )
    screen.hide( "UnitInfoBarText" )
    screen.hide( "UnitInfoBarFlag" )
# PAE - Unit Info Bar - end

    if CyEngine().isGlobeviewUp():
      return

    if (pHeadSelectedCity):

      iOrders = CyInterface().getNumOrdersQueued()

      screen.setTableColumnHeader( "SelectedCityText", 0, u"", 121 )
      screen.setTableColumnHeader( "SelectedCityText", 1, u"", 54 )
      screen.setTableColumnHeader( "SelectedCityText", 2, u"", 10 )
      screen.setTableColumnRightJustify( "SelectedCityText", 1 )

      for i in range( iOrders ):

        szLeftBuffer = u""
        szRightBuffer = u""

        if ( CyInterface().getOrderNodeType(i) == OrderTypes.ORDER_TRAIN ):
          szLeftBuffer = gc.getUnitInfo(CyInterface().getOrderNodeData1(i)).getDescription()
          szRightBuffer = "(" + str(pHeadSelectedCity.getUnitProductionTurnsLeft(CyInterface().getOrderNodeData1(i), i)) + ")"

          if (CyInterface().getOrderNodeSave(i)):
            szLeftBuffer = u"*" + szLeftBuffer

        elif ( CyInterface().getOrderNodeType(i) == OrderTypes.ORDER_CONSTRUCT ):
          szLeftBuffer = gc.getBuildingInfo(CyInterface().getOrderNodeData1(i)).getDescription()
          szRightBuffer = "(" + str(pHeadSelectedCity.getBuildingProductionTurnsLeft(CyInterface().getOrderNodeData1(i), i)) + ")"

        elif ( CyInterface().getOrderNodeType(i) == OrderTypes.ORDER_CREATE ):
          szLeftBuffer = gc.getProjectInfo(CyInterface().getOrderNodeData1(i)).getDescription()
          szRightBuffer = "(" + str(pHeadSelectedCity.getProjectProductionTurnsLeft(CyInterface().getOrderNodeData1(i), i)) + ")"

        elif ( CyInterface().getOrderNodeType(i) == OrderTypes.ORDER_MAINTAIN ):
          szLeftBuffer = gc.getProcessInfo(CyInterface().getOrderNodeData1(i)).getDescription()

        screen.appendTableRow( "SelectedCityText" )
        screen.setTableText( "SelectedCityText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_LEFT_JUSTIFY )
        screen.setTableText( "SelectedCityText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_RIGHT_JUSTIFY )
        screen.show( "SelectedCityText" )
        screen.show( "SelectedUnitPanel" )
        iRow += 1

    elif (pHeadSelectedUnit and CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW):

      screen.setTableColumnHeader( "SelectedUnitText", 0, u"", 110 )
      screen.setTableColumnHeader( "SelectedUnitText", 1, u"", 75 )
      screen.setTableColumnHeader( "SelectedUnitText", 2, u"", 10 )
      screen.setTableColumnRightJustify( "SelectedUnitText", 1 )

      if (CyInterface().mirrorsSelectionGroup()):
        pSelectedGroup = pHeadSelectedUnit.getGroup()
      else:
        pSelectedGroup = 0

      if (CyInterface().getLengthSelectionList() > 1):

        screen.setText( "SelectedUnitLabel", "Background", localText.getText("TXT_KEY_UNIT_STACK", (CyInterface().getLengthSelectionList(), )), CvUtil.FONT_LEFT_JUSTIFY, 18, yResolution - 137, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_UNIT_NAME, -1, -1 )


# BUG - Stack Promotions - start
# + PAE Unit Info Bar inits
        iNumPromotions = gc.getNumPromotionInfos()
        lPromotionCounts = [0] * iNumPromotions
        for i in range(CyInterface().getLengthSelectionList()):
                pUnit = CyInterface().getSelectionUnit(i)
                if pUnit:
                        for j in range(iNumPromotions):
                                if (pUnit.isHasPromotion(j)):
                                        lPromotionCounts[j] += 1

        # PAE Unit Info Bar
                        if pUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):

                          UnitBarType = "HEALER"
                          (iSup, iMax) = PAE_Unit.getSupply(pUnit)
                          # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Current Supply "+str(iSup)+" max Supply "+str(iMax),)), None, 2, None, ColorTypes(10), 0, 0, False, False)
                          iValue1 += iSup
                          iValue2 += iMax

                        elif pUnit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
                          UnitBarType = "EMIGRANT"
                          sPlayer = CvUtil.getScriptData(pUnit, ["p", "t"])
                          if sPlayer != "": iValue1 = int(sPlayer)
                          else: iValue1 = pUnit.getOwner()

                        elif pUnit.getUnitType() in PAE_Trade.lTradeUnits:
                          UnitBarType = "TRADE"
                          iValue1 = CvUtil.getScriptData(pUnit, ["b"], -1)

        if CyInterface().getLengthSelectionList() > 19 and UnitBarType != "HEALER": UnitBarType = "NO_HEALER"
        # ------

        iPromotionCount = 0
        for i, iCount in enumerate(lPromotionCounts):
                if (iCount > 0):
                        szName = "PromotionButton" + str(i)
                        self.setPromotionButtonPosition( szName, iPromotionCount )
                        screen.moveToFront( szName )
                        screen.show( szName )
                        if (iCount > 1):
                                szName = "PromotionButtonCircle" + str(iPromotionCount)
                                screen.moveToFront( szName )
                                screen.show( szName )
                                szName = "PromotionButtonCount" + str(iPromotionCount)
                                x, y = self.calculatePromotionButtonPosition(screen, iPromotionCount)
                                screen.setText( szName, "Background", (u"<font=2>%i</font>" % iCount), CvUtil.FONT_CENTER_JUSTIFY, x + 18, y + 6, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_ACTION, -1, -1 )
                                screen.setHitTest( szName, HitTestTypes.HITTEST_NOHIT )
                                screen.moveToFront( szName )
                                screen.show( szName )
                        iPromotionCount += 1
# BUG - Stack Promotions - end


        if ((pSelectedGroup == 0) or (pSelectedGroup.getLengthMissionQueue() <= 1)):
          if (pHeadSelectedUnit):
            for i in range(gc.getNumUnitInfos()):
              iCount = CyInterface().countEntities(i)

              if (iCount > 0):
                szRightBuffer = u""

                szLeftBuffer = gc.getUnitInfo(i).getDescription()

                if (iCount > 1):
                  szRightBuffer = u"(" + str(iCount) + u")"

                szBuffer = szLeftBuffer + u"  " + szRightBuffer
                screen.appendTableRow( "SelectedUnitText" )
                screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_LEFT_JUSTIFY )
                screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_RIGHT_JUSTIFY )
                screen.show( "SelectedUnitText" )
                screen.show( "SelectedUnitPanel" )
                iRow += 1
      else:

        if (pHeadSelectedUnit.getHotKeyNumber() == -1):
          szBuffer = localText.getText("INTERFACE_PANE_UNIT_NAME", (pHeadSelectedUnit.getName(), ))
        else:
          szBuffer = localText.getText("INTERFACE_PANE_UNIT_NAME_HOT_KEY", (pHeadSelectedUnit.getHotKeyNumber(), pHeadSelectedUnit.getName()))
        if (len(szBuffer) > 60):
          szBuffer = "<font=2>" + szBuffer + "</font>"

        # PAE: Show Unit Type Button
        if pHeadSelectedUnit.getUnitCombatType() > -1:
          x = 32
          iUnitCombatType = pHeadSelectedUnit.getUnitCombatType()
          screen.setImageButton("SelectedUnitCombatType", gc.getUnitCombatInfo(iUnitCombatType).getButton(), 10, yResolution - 137, 24, 24, WidgetTypes.WIDGET_PEDIA_JUMP_TO_UNIT_COMBAT, iUnitCombatType, -1)
        else:
          x = 18 # Original

        # PAE change: x  / Original: y - 137
        screen.setText( "SelectedUnitLabel", "Background", szBuffer, CvUtil.FONT_LEFT_JUSTIFY, x, yResolution - 138, -0.1, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_UNIT_NAME, -1, -1 )

        if (pSelectedGroup == 0 or pSelectedGroup.getLengthMissionQueue() <= 1):
          screen.show( "SelectedUnitText" )
          screen.show( "SelectedUnitPanel" )

          iNumPromos = gc.getNumPromotionInfos()

          szBuffer = u""

          szLeftBuffer = u""
          szRightBuffer = u""

          if (pHeadSelectedUnit.getDomainType() == DomainTypes.DOMAIN_AIR):
            if (pHeadSelectedUnit.airBaseCombatStr() > 0):
              szLeftBuffer = localText.getText("INTERFACE_PANE_AIR_STRENGTH", ())
              if (pHeadSelectedUnit.isFighting()):
                szRightBuffer = u"?/%d%c" %(pHeadSelectedUnit.airBaseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
              elif (pHeadSelectedUnit.isHurt()):
                szRightBuffer = u"%.1f/%d%c" %(((float(pHeadSelectedUnit.airBaseCombatStr() * pHeadSelectedUnit.currHitPoints())) / (float(pHeadSelectedUnit.maxHitPoints()))), pHeadSelectedUnit.airBaseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
              else:
                szRightBuffer = u"%d%c" %(pHeadSelectedUnit.airBaseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
          else:
            if (pHeadSelectedUnit.canFight()):
              szLeftBuffer = localText.getText("INTERFACE_PANE_STRENGTH", ())
              if (pHeadSelectedUnit.isFighting()):
                szRightBuffer = u"?/%d%c" %(pHeadSelectedUnit.baseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
              elif (pHeadSelectedUnit.isHurt()):
                szRightBuffer = u"%.1f/%d%c" %(((float(pHeadSelectedUnit.baseCombatStr() * pHeadSelectedUnit.currHitPoints())) / (float(pHeadSelectedUnit.maxHitPoints()))), pHeadSelectedUnit.baseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))
              else:
                szRightBuffer = u"%d%c" %(pHeadSelectedUnit.baseCombatStr(), CyGame().getSymbolID(FontSymbols.STRENGTH_CHAR))

          szBuffer = szLeftBuffer + szRightBuffer
          if ( szBuffer ):
            screen.appendTableRow( "SelectedUnitText" )
            screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
            screen.show( "SelectedUnitText" )
            screen.show( "SelectedUnitPanel" )
            iRow += 1

          szLeftBuffer = u""
          szRightBuffer = u""

          if ( (pHeadSelectedUnit.movesLeft() % gc.getMOVE_DENOMINATOR()) > 0 ):
            iDenom = 1
          else:
            iDenom = 0
          iCurrMoves = ((pHeadSelectedUnit.movesLeft() / gc.getMOVE_DENOMINATOR()) + iDenom )
          szLeftBuffer = localText.getText("INTERFACE_PANE_MOVEMENT", ())
          if (pHeadSelectedUnit.baseMoves() == iCurrMoves):
            szRightBuffer = u"%d%c" %(pHeadSelectedUnit.baseMoves(), CyGame().getSymbolID(FontSymbols.MOVES_CHAR) )
          else:
            szRightBuffer = u"%d/%d%c" %(iCurrMoves, pHeadSelectedUnit.baseMoves(), CyGame().getSymbolID(FontSymbols.MOVES_CHAR) )

          screen.appendTableRow( "SelectedUnitText" )
          screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
          screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
          screen.show( "SelectedUnitText" )
          screen.show( "SelectedUnitPanel" )
          iRow += 1

          if (pHeadSelectedUnit.getLevel() > 0):

            szLeftBuffer = localText.getText("INTERFACE_PANE_LEVEL", ())
            szRightBuffer = u"%d" %(pHeadSelectedUnit.getLevel())

            screen.appendTableRow( "SelectedUnitText" )
            screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
            screen.show( "SelectedUnitText" )
            screen.show( "SelectedUnitPanel" )
            iRow += 1

          if ((pHeadSelectedUnit.getExperience() > 0) and not pHeadSelectedUnit.isFighting()):

            szLeftBuffer = localText.getText("INTERFACE_PANE_EXPERIENCE", ())
            szRightBuffer = u"(%d/%d)" %(pHeadSelectedUnit.getExperience(), pHeadSelectedUnit.experienceNeeded())

            screen.appendTableRow( "SelectedUnitText" )
            screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
            screen.show( "SelectedUnitText" )
            screen.show( "SelectedUnitPanel" )
            iRow += 1

          # PAE Unit Detail Promo Icons:

          # ZEILE 1 (Staerke)

          # PAE Combat Ranking
          iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT1")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             if pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT6")):   iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT6")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT5")): iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT5")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT4")): iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT4")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT3")): iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT3")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_COMBAT2")): iPromo = gc.getInfoTypeForString("PROMOTION_COMBAT2")
             screen.setImageButton("SelectedUnitCombatRank", gc.getPromotionInfo(iPromo).getButton(), 60, yResolution - 110, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)

          # PAE War Weariness
          iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG1")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             if pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG5")):   iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG5")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG4")): iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG4")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG3")): iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG3")
             elif pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString("PROMOTION_MORAL_NEG2")): iPromo = gc.getInfoTypeForString("PROMOTION_MORAL_NEG2")
             screen.setImageButton("SelectedBadMoral", gc.getPromotionInfo(iPromo).getButton(), 84, yResolution - 110, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)

          # PAE Loyalty
          iPromo = gc.getInfoTypeForString("PROMOTION_LOYALITAT")
          iPromo2 = gc.getInfoTypeForString("PROMOTION_MERCENARY")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             screen.setImageButton("SelectedUnitLoyalty", gc.getPromotionInfo(iPromo).getButton(), 108, yResolution - 110, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)
          elif pHeadSelectedUnit.isHasPromotion(iPromo2):
             screen.setImageButton("SelectedUnitLoyalty", gc.getPromotionInfo(iPromo2).getButton(), 108, yResolution - 110, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo2, -1)


          # ZEILE 2 (Fortbewegung)

          # PAE Formation SelectedUnitFormation
          iPromo = 0
          for iPromo in range(iNumPromos):
            if "_FORM_" in gc.getPromotionInfo(iPromo).getType() and pHeadSelectedUnit.isHasPromotion(iPromo):
              screen.setImageButton("SelectedUnitFormation", gc.getPromotionInfo(iPromo).getButton(), 108, yResolution - 85, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)

          # ZEILE 3 (Stufe)

          # PAE Trait
          iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_AGGRESSIVE")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             screen.setImageButton("SelectedUnitTrait", gc.getPromotionInfo(iPromo).getButton(), 60, yResolution - 60, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)
          iPromo = gc.getInfoTypeForString("PROMOTION_TRAIT_MARITIME")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             screen.setImageButton("SelectedUnitTrait", gc.getPromotionInfo(iPromo).getButton(), 60, yResolution - 60, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)

          # PAE Unit Ethnic und Religion
          #if 1 != -1:
          #   iUnitEthnic = 4 # => pHeadSelectedUnit.getEthnic()
          #   screen.setImageButton("SelectedUnitEthnic", gc.getCivilizationInfo(iUnitEthnic).getButton(), 84, yResolution - 60, 24, 24, WidgetTypes.WIDGET_GENERAL, 750, iUnitEthnic)
          #if 1 != -1:
          #   iUnitReligion = 4 # => pHeadSelectedUnit.getReligion()
          #   screen.setImageButton("SelectedUnitReligion", gc.getReligionInfo(iUnitReligion).getButton(), 108, yResolution - 60, 24, 24, WidgetTypes.WIDGET_HELP_RELIGION, iUnitReligion, -1)

          # ZEILE 4 (Erfahrung)

          # PAE Held
          iPromo = gc.getInfoTypeForString("PROMOTION_HERO")
          if pHeadSelectedUnit.isHasPromotion(iPromo):
             screen.setImageButton("SelectedUnitHero", gc.getPromotionInfo(iPromo).getButton(), 84, yResolution - 36, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)

          # PAE Unit Rang Promos
          iPromo = iNumPromos-1
          for iPromo in xrange(iNumPromos-1,0,-1):
            if "_TRAIT_" in gc.getPromotionInfo(iPromo).getType(): break
            if "_RANG_" in gc.getPromotionInfo(iPromo).getType():
              if pHeadSelectedUnit.isHasPromotion(iPromo):
                screen.setImageButton("SelectedUnitRang", gc.getPromotionInfo(iPromo).getButton(), 108, yResolution - 36, 24, 24, WidgetTypes.WIDGET_HELP_PROMOTION, iPromo, -1)
                break
          # ----

          # PAE Cultivation and Trade (Boggy)
          szText = ""
          if pHeadSelectedUnit.getUnitType() in PAE_Trade.lTradeUnits + PAE_Trade.lCultivationUnits:
              szText = localText.getText("TXT_UNIT_INFO_BAR_5", ()) + u" "
              iValue1 = CvUtil.getScriptData(pHeadSelectedUnit, ["b"], -1)
              if iValue1 != -1:
                  sBonusDesc = gc.getBonusInfo(iValue1).getDescription()
                  iBonusChar = gc.getBonusInfo(iValue1).getChar()
                  szText += localText.getText("TXT_UNIT_INFO_BAR_4", (iBonusChar,sBonusDesc))
              else:
                  szText += localText.getText("TXT_KEY_NO_BONUS_STORED", ())

          if szText != "":
            screen.setTableColumnHeader( "SelectedTradeText", 0, u"", 300 )
            screen.appendTableRow( "SelectedTradeText" )
            screen.setTableText( "SelectedTradeText", 0, 0, szText, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.show( "SelectedTradeText" )
          # ----

          # PAE HEALER and EMIGRANT + Unit Info Bar
          if pHeadSelectedUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_HEALER"):
            UnitBarType = "HEALER"
            (iSup, iMax) = PAE_Unit.getSupply(pHeadSelectedUnit)
            iValue1 += iSup
            iValue2 += iMax
            # CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 10, CyTranslator().getText("TXT_KEY_MESSAGE_TEST",("Current Supply "+str(iValue1)+" max Supply "+str(iValue2),)), None, 2, None, ColorTypes(10), 0, 0, False, False)

            szLeftBuffer = localText.getText("TXT_UNIT_INFO_BAR_6", ())
            szRightBuffer = u"(%d/%d)" %(iValue1, iValue2)

            screen.appendTableRow( "SelectedUnitText" )
            screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY )
            screen.show( "SelectedUnitText" )
            screen.show( "SelectedUnitPanel" )
            iRow += 1

          elif pHeadSelectedUnit.getUnitType() == gc.getInfoTypeForString("UNIT_EMIGRANT"):
            UnitBarType = "EMIGRANT"
            txt = CvUtil.getScriptData(pHeadSelectedUnit, ["p", "t"])
            # txt kann "NO_PLAYER" oder eine list mit "NO_PLAYER" enthalten
            if txt != "" and isinstance(txt, int): iValue1 = txt
            else: iValue1 = pHeadSelectedUnit.getOwner()
          # ---


## Hidden Promotions: changed by Pie for PAE to avoid info type XY not found errors!
          lIgnorePromos = []
          lIgnorePromos.append("PROMOTION_COVER4")
          lIgnorePromos.append("PROMOTION_PARADE_SKIRM4")
          lIgnorePromos.append("PROMOTION_PARADE_AXE4")
          lIgnorePromos.append("PROMOTION_PARADE_SWORD4")
          lIgnorePromos.append("PROMOTION_PARADE_SPEAR4")
          lIgnorePromos.append("PROMOTION_FORMATION4")
          lIgnorePromos.append("PROMOTION_SKIRMISH4")
          lIgnorePromos.append("PROMOTION_MEDIC6")
          lIgnorePromos.append("PROMOTION_GUERILLA6")
          lIgnorePromos.append("PROMOTION_WOODSMAN6")
          lIgnorePromos.append("PROMOTION_JUNGLE6")
          lIgnorePromos.append("PROMOTION_SUMPF6")
          lIgnorePromos.append("PROMOTION_CITY_RAIDER6")
          lIgnorePromos.append("PROMOTION_CITY_GARRISON6")
          lIgnorePromos.append("PROMOTION_DRILL5")
          lIgnorePromos.append("PROMOTION_BARRAGE6")
          lIgnorePromos.append("PROMOTION_ACCURACY4")
          lIgnorePromos.append("PROMOTION_FLANKING4")
          lIgnorePromos.append("PROMOTION_OVERRUN4")
          lIgnorePromos.append("PROMOTION_NAVIGATION5")
          lIgnorePromos.append("PROMOTION_PILLAGE6")
          lIgnorePromos.append("PROMOTION_DESERT6")
          lIgnorePromos.append("PROMOTION_FLUCHT4")
          lIgnorePromos.append("PROMOTION_FUROR4")

          iPromotionCount = 0
          i = 0
          for i in range(iNumPromos):
            sPromotion = gc.getPromotionInfo(i).getType()

            # PAE seperate Rankings etc
            if "_COMBAT" in sPromotion: continue
            if "_RANG_"  in sPromotion: continue
            if "_LOYAL"  in sPromotion: continue
            if "_TRAIT_" in sPromotion: continue
            if "_FORM_"  in sPromotion: continue
            if "_MORAL_" in sPromotion: continue
            if "_MERC"   in sPromotion: continue
            if "_HERO"   in sPromotion: continue

            if pHeadSelectedUnit.isHasPromotion(i):
## Hidden Promotions (Platyping) ##
## adapted for PAE by Pie to avoid info type XY not found warnings
              sLast = sPromotion[len(sPromotion)-1]
              if sLast.isdigit():
                 sPromotion = sPromotion[:len(sPromotion)-1] + str(int(sLast)+1)
                 if sPromotion not in lIgnorePromos:
                   if gc.getInfoTypeForString(sPromotion) > -1:
                     if (pHeadSelectedUnit.isHasPromotion(gc.getInfoTypeForString(sPromotion))): continue
## Hidden Promotions (Platyping) ##
              szName = "PromotionButton" + str(i)
              self.setPromotionButtonPosition( szName, iPromotionCount )
              screen.moveToFront( szName )
              screen.show( szName )

              iPromotionCount = iPromotionCount + 1


      if (pSelectedGroup):

        iNodeCount = pSelectedGroup.getLengthMissionQueue()

        if (iNodeCount > 1):
          for i in range( iNodeCount ):
            szLeftBuffer = u""
            szRightBuffer = u""

            if (gc.getMissionInfo(pSelectedGroup.getMissionType(i)).isBuild()):
              if (i == 0):
                szLeftBuffer = gc.getBuildInfo(pSelectedGroup.getMissionData1(i)).getDescription()
                szRightBuffer = localText.getText("INTERFACE_CITY_TURNS", (pSelectedGroup.plot().getBuildTurnsLeft(pSelectedGroup.getMissionData1(i), 0, 0), ))
              else:
                szLeftBuffer = u"%s..." %(gc.getBuildInfo(pSelectedGroup.getMissionData1(i)).getDescription())
            else:
              szLeftBuffer = u"%s..." %(gc.getMissionInfo(pSelectedGroup.getMissionType(i)).getDescription())

            szBuffer = szLeftBuffer + "  " + szRightBuffer
            screen.appendTableRow( "SelectedUnitText" )
            screen.setTableText( "SelectedUnitText", 0, iRow, szLeftBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_LEFT_JUSTIFY )
            screen.setTableText( "SelectedUnitText", 1, iRow, szRightBuffer, "", WidgetTypes.WIDGET_HELP_SELECTED, i, -1, CvUtil.FONT_RIGHT_JUSTIFY )
            screen.show( "SelectedUnitText" )
            screen.show( "SelectedUnitPanel" )
            iRow += 1

      # PAE- Unit Info Bar
      if UnitBarType != "": self.updateUnitInfoBar(screen,UnitBarType,iValue1,iValue2)

    return 0

# PAE - Unit Info Bar - start
  def updateUnitInfoBar(self, screen, UnitBarType, iValue1, iValue2):
      #if not CyInterface().isCityScreenUp():
          pPlayer = gc.getActivePlayer()
          xResolution = screen.getXResolution()

          xCoord = xResolution - 250
          yCoord = 90

          szText = ""
          if UnitBarType == "EMIGRANT":
            szText = localText.getText("TXT_UNIT_INFO_BAR_1", ("",gc.getPlayer(iValue1).getCivilizationAdjective(2).capitalize()))
            screen.setLabel( "UnitInfoBarText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xCoord + 40, yCoord + 5, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

            screen.setStackedBarColorsRGB( "UnitInfoBar", 1, gc.getPlayer(iValue1).getPlayerTextColorR(), gc.getPlayer(iValue1).getPlayerTextColorG(), gc.getPlayer(iValue1).getPlayerTextColorB(), gc.getPlayer(iValue1).getPlayerTextColorA() )
            screen.setBarPercentage( "UnitInfoBar", 0, 0.0 ) # disable

            screen.addFlagWidgetGFC( "UnitInfoBarFlag", xCoord+5, yCoord-20, 30, 80, iValue1, WidgetTypes.WIDGET_FLAG, iValue1, -1)
            screen.show( "UnitInfoBarFlag" )

          elif UnitBarType == "HEALER":
            szText = localText.getText("TXT_UNIT_INFO_BAR_2", (CyGame().getSymbolID(FontSymbols.HEALTHY_CHAR),iValue1,iValue2))
            screen.setLabel( "UnitInfoBarText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xCoord + 10, yCoord + 5, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )

            screen.setStackedBarColorsRGB( "UnitInfoBar", 1, 0, 0, 0, 100 ) # black

            fPercent = 1.0 / float(iValue2) * float(iValue1)
            if fPercent > 0.0:

              if fPercent < 0.2: screen.setStackedBarColorsRGB( "UnitInfoBar", 0, 255, 0, 0, 100 ) # red
              if fPercent < 0.5: screen.setStackedBarColorsRGB( "UnitInfoBar", 0, 255, 255, 0, 100 ) # yellow
              else: screen.setStackedBarColorsRGB( "UnitInfoBar", 0, 0, 255, 0, 100 ) # green
              screen.setBarPercentage( "UnitInfoBar", 0, fPercent ) # 0.8

          elif UnitBarType == "NO_HEALER":
            szText = localText.getText("TXT_UNIT_INFO_BAR_3", (CyGame().getSymbolID(FontSymbols.UNHEALTHY_CHAR),0))
            screen.setLabel( "UnitInfoBarText", "Background", szText, CvUtil.FONT_LEFT_JUSTIFY, xCoord + 10, yCoord + 5, -0.4, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1 )
            screen.setStackedBarColorsRGB( "UnitInfoBar", 1, 255, 0, 0, 100 ) # red
            screen.setBarPercentage( "UnitInfoBar", 0, 0.0 ) # disable


          # red = 255,0,0
          # yellow = 255,255,0
          # green = 0,255,0

          # Bar 0 ist Balken von rechts / Bar 1 = Hintergrund
          screen.setBarPercentage( "UnitInfoBar", 1, 1.0 ) # immer 1 !
          screen.show( "UnitInfoBar" )

          screen.setHitTest( "UnitInfoBarText", HitTestTypes.HITTEST_NOHIT )
          screen.show( "UnitInfoBarText" )

# PAE - Unit Info Bar - end

  # Will update the scores
  def updateScoreStrings( self ):

    # Platy Scoreboard adapted and changed by Pie and debugged by Ramk
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    screen.hide("ScoreBackground")
    screen.hide("ScoreBackground2")
    screen.hide("ScoreRowPlus")
    screen.hide("ScoreRowMinus")
    screen.hide("ScoreWidthPlus")
    screen.hide("ScoreWidthMinus")
    screen.hide("ScoreHidePoints") #PAE
    if CyEngine().isGlobeviewUp(): return
    if CyInterface().isCityScreenUp(): return
    if CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE_ALL: return
    if CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_MINIMAP_ONLY: return
    if not CyInterface().isScoresVisible(): return

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    lMasters = []
    lVassals = []
    lPlayers = []
    iRange = gc.getMAX_CIV_PLAYERS()
    for iPlayerX in xrange(iRange):
        if CyInterface().isScoresMinimized():
            if iPlayerX == CyGame().getActivePlayer():
                lPlayers.append(iPlayerX)
                break
        else:
            pPlayerX = gc.getPlayer(iPlayerX)
            if pPlayerX.isAlive():
                iTeamX = pPlayerX.getTeam()
                pTeamX = gc.getTeam(iTeamX)
                if pTeamX.isHasMet(CyGame().getActiveTeam()) or CyGame().isDebugMode():
                    if pTeamX.isAVassal():
                        for iTeamY in xrange(gc.getMAX_CIV_TEAMS()):
                            if pTeamX.isVassal(iTeamY):
                                lVassals.append([CyGame().getTeamRank(iTeamY), CyGame().getTeamRank(iTeamX), CyGame().getPlayerRank(iPlayerX), iPlayerX])
                                break
                    else:
                        lMasters.append([CyGame().getTeamRank(iTeamX), CyGame().getPlayerRank(iPlayerX), iPlayerX])
    lMasters.sort()
    lVassals.sort()
    iOldRank = -1
    for i in lMasters:
        if iOldRank != i[0]:
            for j in lVassals:
                if j[0] == iOldRank:
                    lPlayers.append(j[3])
                elif j[0] > iOldRank:
                    break
            iOldRank = i[0]
        lPlayers.append(i[2])

    nRows = len(lPlayers)
    self.iScoreRows = max(0, min(self.iScoreRows, nRows - 1))
    iHeight = min(yResolution - 300, max(1, (nRows - self.iScoreRows)) * 24 + 2)
#                screen.addTableControlGFC("ScoreBackground", 6, xResolution - self.iScoreWidth - 230, yResolution - iHeight - 180, self.iScoreWidth + 230, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
#                screen.enableSelect("ScoreBackground", False)
#                screen.setTableColumnHeader("ScoreBackground", 0, "", self.iScoreWidth)
#                screen.setTableColumnHeader("ScoreBackground", 1, "", 23)
#                screen.setTableColumnHeader("ScoreBackground", 2, "", 23)
#                screen.setTableColumnHeader("ScoreBackground", 3, "", 23)
#                screen.setTableColumnHeader("ScoreBackground", 4, "", 90)
#                screen.setTableColumnHeader("ScoreBackground", 5, "", 73)
    screen.addTableControlGFC("ScoreBackground2", 6, xResolution - self.iScoreWidth - 230, yResolution - iHeight - 180, self.iScoreWidth + 230, iHeight, False, False, 24, 24, TableStyles.TABLE_STYLE_EMPTY)
    screen.enableSelect("ScoreBackground2", False)
    screen.setTableColumnHeader("ScoreBackground2", 0, "", self.iScoreWidth)
    screen.setTableColumnHeader("ScoreBackground2", 1, "", 23)
    screen.setTableColumnHeader("ScoreBackground2", 2, "", 23)
    screen.setTableColumnHeader("ScoreBackground2", 3, "", 23)
    screen.setTableColumnHeader("ScoreBackground2", 4, "", 90)
    screen.setTableColumnHeader("ScoreBackground2", 5, "", 73)
    if self.iScoreWidth > 0:
        screen.setButtonGFC("ScoreWidthMinus", "", "", xResolution - 48, yResolution - 179, 17, 17, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_ARROW_RIGHT)
    screen.setButtonGFC("ScoreRowMinus", "", "", xResolution - 70, yResolution - 180, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_CITY_MINUS )
    screen.setButtonGFC("ScoreHidePoints", "", "", xResolution - 90, yResolution - 180, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setButtonGFC("ScoreRowPlus", "", "", xResolution - 110, yResolution - 180, 20, 20, WidgetTypes.WIDGET_GENERAL, -1, -1, ButtonStyles.BUTTON_STYLE_CITY_PLUS )
    if self.iScoreWidth < 200:
        screen.setButtonGFC("ScoreWidthPlus", "", "", xResolution - 129, yResolution - 179, 17, 17, WidgetTypes.WIDGET_GENERAL, 1, -1, ButtonStyles.BUTTON_STYLE_ARROW_LEFT)
    for iPlayer in lPlayers:
#       iRow = screen.appendTableRow("ScoreBackground")
        iRow = screen.appendTableRow("ScoreBackground2")
        pPlayer = gc.getPlayer(iPlayer)
        iTeam = pPlayer.getTeam()
        pTeam = gc.getTeam(iTeam)

        sText1 = u"<font=2>"

        if CyGame().isGameMultiPlayer():
          if not pPlayer.isTurnActive():
            sText1 += "*"
        if CyGame().isNetworkMultiPlayer():
            sText1 += CyGameTextMgr().getNetStats(iPlayer)
        if pPlayer.isHuman() and CyInterface().isOOSVisible():
            sText1 += u" <color=255,0,0>* %s *</color>" %(CyGameTextMgr().getOOSSeeds(iPlayer))
        if not pTeam.isHasMet(CyGame().getActiveTeam()):
            sText1 += "? "

        #sButton = "INTERFACE_ATTITUDE_BOY"
        #if not pPlayer.isHuman():
        #        lVincent = ["INTERFACE_ATTITUDE_0", "INTERFACE_ATTITUDE_1", "INTERFACE_ATTITUDE_2", "INTERFACE_ATTITUDE_3", "INTERFACE_ATTITUDE_4"]
        #        sButton = lVincent[pPlayer.AI_getAttitude(CyGame().getActivePlayer())]

        # PAE
        sButton = ""
        if not pPlayer.isHuman():
            iAtt = pPlayer.AI_getAttitude(gc.getGame().getActivePlayer())
            sButton = u"%c" %(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 4 + iAtt)
        # None was: ArtFileMgr.getInterfaceArtInfo(sButton).getPath()
        screen.setTableText("ScoreBackground2", 1, iRow, sButton, None, WidgetTypes.WIDGET_CONTACT_CIV, iPlayer, -1, CvUtil.FONT_LEFT_JUSTIFY)
        #szTempBuffer = u"<color=%d,%d,%d,%d>%s</color>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA(), pPlayer.getName())
        #screen.setTableText("ScoreBackground2", 2, iRow, szTempBuffer, None, WidgetTypes.WIDGET_CONTACT_CIV, iPlayer, -1, CvUtil.FONT_LEFT_JUSTIFY)
        screen.setTableText("ScoreBackground2", 2, iRow, "", gc.getLeaderHeadInfo(pPlayer.getLeaderType()).getButton(), WidgetTypes.WIDGET_CONTACT_CIV, iPlayer, -1, CvUtil.FONT_LEFT_JUSTIFY)
        screen.setTableText("ScoreBackground2", 3, iRow, "", gc.getCivilizationInfo(pPlayer.getCivilizationType()).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, pPlayer.getCivilizationType(), 1, CvUtil.FONT_LEFT_JUSTIFY)
        szTempBuffer = u"<color=%d,%d,%d,%d>%s</color>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA(), pPlayer.getCivilizationShortDescription(0))
        screen.setTableText("ScoreBackground2", 4, iRow, szTempBuffer, None, WidgetTypes.WIDGET_PEDIA_JUMP_TO_CIV, pPlayer.getCivilizationType(), 1, CvUtil.FONT_LEFT_JUSTIFY)

        if pTeam.isAVassal():
            sText1 += CyTranslator().getText("[ICON_SILVER_STAR]", ())

        #if iPlayer == CyGame().getActivePlayer():
        #        sText1 += CyTranslator().getText("[ICON_POWER]", ())
        #else:
        if iPlayer != CyGame().getActivePlayer():
            if pTeam.getPower(1) >= gc.getTeam(gc.getGame().getActiveTeam()).getPower(1):
                sText1 += CyTranslator().getText("[ICON_STRENGTH]", ())
            if pTeam.isDefensivePact(CyGame().getActiveTeam()):
                sText1 += CyTranslator().getText("[ICON_DEFENSIVEPACT]", ())
            if pTeam.getEspionagePointsAgainstTeam(CyGame().getActiveTeam()) < gc.getTeam(CyGame().getActiveTeam()).getEspionagePointsAgainstTeam(iTeam):
                sText1 += CyTranslator().getText("[ICON_ESPIONAGE]", ())
            if pTeam.isAtWar(CyGame().getActiveTeam()):
                #sText1 += CyTranslator().getText("[ICON_OCCUPATION]", ())
                sText1 += "("  + localText.getColorText("TXT_KEY_CONCEPT_WAR", (), gc.getInfoTypeForString("COLOR_RED")).upper() + ")"
            if pTeam.isOpenBorders(CyGame().getActiveTeam()):
                sText1 += CyTranslator().getText("[ICON_OPENBORDERS]", ())
            if pPlayer.canTradeNetworkWith(CyGame().getActivePlayer()):
                sText1 += CyTranslator().getText("[ICON_TRADE]", ())

        iReligion = pPlayer.getStateReligion()
        if iReligion > -1:
            if pPlayer.hasHolyCity(iReligion):
                sText1 += u"%c" %(gc.getReligionInfo(iReligion).getHolyCityChar())
            else:
                sText1 += u"%c" %(gc.getReligionInfo(iReligion).getChar())

        if not self.iScoreHidePoints:
           sText1 += u"<color=%d,%d,%d,%d>%d</color>" %(pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA(), CyGame().getPlayerScore(iPlayer))

        screen.setTableText("ScoreBackground2", 0, iRow, sText1, "", WidgetTypes.WIDGET_GENERAL, -1, -1, CvUtil.FONT_RIGHT_JUSTIFY)

        bEspionageCanSeeResearch = False
        for iMissionLoop in xrange(gc.getNumEspionageMissionInfos()):
            if (gc.getEspionageMissionInfo(iMissionLoop).isSeeResearch()):
                bEspionageCanSeeResearch = gc.getPlayer(CyGame().getActivePlayer()).canDoEspionageMission(iMissionLoop, iPlayer, None, -1)
                break

        if iTeam == CyGame().getActiveTeam() or pTeam.isVassal(CyGame().getActiveTeam()) or CyGame().isDebugMode() or bEspionageCanSeeResearch:
            iTech = pPlayer.getCurrentResearch()
            if iTech > -1:
                sTech = u"<color=%d,%d,%d,%d>%d</color>" %( pPlayer.getPlayerTextColorR(), pPlayer.getPlayerTextColorG(), pPlayer.getPlayerTextColorB(), pPlayer.getPlayerTextColorA(), pPlayer.getResearchTurnsLeft(pPlayer.getCurrentResearch(), True))
                screen.setTableText("ScoreBackground2", 5, iRow, sTech, gc.getTechInfo(iTech).getButton(), WidgetTypes.WIDGET_PEDIA_JUMP_TO_TECH, iTech, 1, CvUtil.FONT_LEFT_JUSTIFY)
# Platy Scoreboard - End

  # Will update the scores - TEAMS Ansicht
  def updateScoreStrings_PAEIV( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    screen.hide("ScoreBackground")
    screen.hide("ScoreBackground2")

    for i in range( gc.getMAX_PLAYERS() ):
      szName = "ScoreText" + str(i)
      screen.hide( szName )

    iWidth = 0
    iCount = 0
    iBtnHeight = 22

    if ((CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_MINIMAP_ONLY)):
      if (CyInterface().isScoresVisible() and not CyInterface().isCityScreenUp() and CyEngine().isGlobeviewUp() == False):

        i = gc.getMAX_CIV_TEAMS() - 1
        while (i > -1):
          eTeam = gc.getGame().getRankTeam(i)

          #if (gc.getTeam(gc.getGame().getActiveTeam()).isHasMet(eTeam) or gc.getTeam(eTeam).isHuman() or gc.getGame().isDebugMode()):
          if (gc.getTeam(gc.getGame().getActiveTeam()).isHasMet(eTeam) or gc.getGame().isDebugMode()):
            j = gc.getMAX_CIV_PLAYERS() - 1
            while (j > -1):
              ePlayer = gc.getGame().getRankPlayer(j)

              if (not CyInterface().isScoresMinimized() or gc.getGame().getActivePlayer() == ePlayer):
                if (gc.getPlayer(ePlayer).isAlive() and not gc.getPlayer(ePlayer).isMinorCiv()):

                  if (gc.getPlayer(ePlayer).getTeam() == eTeam):
                    szBuffer = u"<font=2>"

                    #if (gc.getGame().isGameMultiPlayer()):
                    if (not (gc.getPlayer(ePlayer).isTurnActive())):
                        szBuffer = szBuffer + "*"

                    # Leadername OR Civname (Leadername) OR Civname
                    #szPAECivName = gc.getPlayer(ePlayer).getName() # Original
                    szPAECivName = gc.getPlayer(ePlayer).getCivilizationDescription(0) + " (" + gc.getPlayer(ePlayer).getName() + ")"
                    #szPAECivName = gc.getPlayer(ePlayer).getCivilizationShortDescription(0)

                    if (not CyInterface().isFlashingPlayer(ePlayer) or CyInterface().shouldFlash(ePlayer)):
                      if (ePlayer == gc.getGame().getActivePlayer()):
                        szTempBuffer = u"%d: [<color=%d,%d,%d,%d>%s</color>]" %(gc.getGame().getPlayerScore(ePlayer), gc.getPlayer(ePlayer).getPlayerTextColorR(), gc.getPlayer(ePlayer).getPlayerTextColorG(), gc.getPlayer(ePlayer).getPlayerTextColorB(), gc.getPlayer(ePlayer).getPlayerTextColorA(), szPAECivName)
                      else:
                        szTempBuffer = u"%d: <color=%d,%d,%d,%d>%s</color>" %(gc.getGame().getPlayerScore(ePlayer), gc.getPlayer(ePlayer).getPlayerTextColorR(), gc.getPlayer(ePlayer).getPlayerTextColorG(), gc.getPlayer(ePlayer).getPlayerTextColorB(), gc.getPlayer(ePlayer).getPlayerTextColorA(), szPAECivName)
                    else:
                      szTempBuffer = u"%d: %s" %(gc.getGame().getPlayerScore(ePlayer), szPAECivName)
                    szBuffer = szBuffer + szTempBuffer

                    bEspionageCanSeeResearch = False
                    for iMissionLoop in range(gc.getNumEspionageMissionInfos()):
                      if (gc.getEspionageMissionInfo(iMissionLoop).isSeeResearch()):
                        bEspionageCanSeeResearch = gc.getPlayer(gc.getGame().getActivePlayer()).canDoEspionageMission(iMissionLoop, ePlayer, None, -1)
                        break

                    if (((gc.getPlayer(ePlayer).getTeam() == gc.getGame().getActiveTeam()) and (gc.getTeam(gc.getGame().getActiveTeam()).getNumMembers() > 1)) or (gc.getTeam(gc.getPlayer(ePlayer).getTeam()).isVassal(gc.getGame().getActiveTeam())) or gc.getGame().isDebugMode() or bEspionageCanSeeResearch):
                      if (gc.getPlayer(ePlayer).getCurrentResearch() != -1):
                        szTempBuffer = u"-%s (%d)" %(gc.getTechInfo(gc.getPlayer(ePlayer).getCurrentResearch()).getDescription(), gc.getPlayer(ePlayer).getResearchTurnsLeft(gc.getPlayer(ePlayer).getCurrentResearch(), True))
                        szBuffer = szBuffer + szTempBuffer
                    if (CyGame().isNetworkMultiPlayer()):
                      szBuffer = szBuffer + CyGameTextMgr().getNetStats(ePlayer)

                    if (gc.getTeam(eTeam).isAlive()):
                      if ( not (gc.getTeam(gc.getGame().getActiveTeam()).isHasMet(eTeam)) ):
                        szBuffer = szBuffer + (" ?")
                      if (gc.getTeam(eTeam).isAtWar(gc.getGame().getActiveTeam())):
                        szBuffer = szBuffer + "("  + localText.getColorText("TXT_KEY_CONCEPT_WAR", (), gc.getInfoTypeForString("COLOR_RED")).upper() + ")"
                      if (gc.getPlayer(ePlayer).canTradeNetworkWith(gc.getGame().getActivePlayer()) and (ePlayer != gc.getGame().getActivePlayer())):
                        szTempBuffer = u"%c" %(CyGame().getSymbolID(FontSymbols.TRADE_CHAR))
                        szBuffer = szBuffer + szTempBuffer
                      if (gc.getTeam(eTeam).isOpenBorders(gc.getGame().getActiveTeam())):
                        szTempBuffer = u"%c" %(CyGame().getSymbolID(FontSymbols.OPEN_BORDERS_CHAR))
                        szBuffer = szBuffer + szTempBuffer
                      if (gc.getTeam(eTeam).isDefensivePact(gc.getGame().getActiveTeam())):
                        szTempBuffer = u"%c" %(CyGame().getSymbolID(FontSymbols.DEFENSIVE_PACT_CHAR))
                        szBuffer = szBuffer + szTempBuffer
                      if (gc.getTeam(eTeam).getEspionagePointsAgainstTeam(gc.getGame().getActiveTeam()) < gc.getTeam(gc.getGame().getActiveTeam()).getEspionagePointsAgainstTeam(eTeam)):
                        szTempBuffer = u"%c" %(gc.getCommerceInfo(CommerceTypes.COMMERCE_ESPIONAGE).getChar())
                        szBuffer = szBuffer + szTempBuffer

#attitude icons - start smileys
                      if not gc.getPlayer(ePlayer).isHuman():
                        iAtt = gc.getPlayer(ePlayer).AI_getAttitude(gc.getGame().getActivePlayer())
                        szTempBuffer = u"%c" %(CyGame().getSymbolID(FontSymbols.POWER_CHAR) + 4 + iAtt)
                        szBuffer = szBuffer + szTempBuffer
#attitude icons - end

                      if (gc.getPlayer(ePlayer).getStateReligion() != -1):
                        if (gc.getPlayer(ePlayer).hasHolyCity(gc.getPlayer(ePlayer).getStateReligion())):
                          szTempBuffer = u"%c" %(gc.getReligionInfo(gc.getPlayer(ePlayer).getStateReligion()).getHolyCityChar())
                          szBuffer = szBuffer + szTempBuffer
                        else:
                          szTempBuffer = u"%c" %(gc.getReligionInfo(gc.getPlayer(ePlayer).getStateReligion()).getChar())
                          szBuffer = szBuffer + szTempBuffer

                    if (gc.getPlayer(ePlayer).isHuman() and CyInterface().isOOSVisible()):
                      szTempBuffer = u" <color=255,0,0>* %s *</color>" %(CyGameTextMgr().getOOSSeeds(ePlayer))
                      szBuffer = szBuffer + szTempBuffer

                    szBuffer = szBuffer + "</font>"

                    if ( CyInterface().determineWidth( szBuffer ) > iWidth ):
                      iWidth = CyInterface().determineWidth( szBuffer )

                    szName = "ScoreText" + str(ePlayer)
                    if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW or CyInterface().isInAdvancedStart()):
                      yCoord = yResolution - 206
                    else:
                      yCoord = yResolution - 88
                    screen.setText( szName, "Background", szBuffer, CvUtil.FONT_RIGHT_JUSTIFY, xResolution - 12, yCoord - (iCount * iBtnHeight), -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_CONTACT_CIV, ePlayer, -1 )
                    screen.show( szName )

                    CyInterface().checkFlashReset(ePlayer)

                    iCount = iCount + 1
              j = j - 1
          i = i - 1

        if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW or CyInterface().isInAdvancedStart()):
          yCoord = yResolution - 186
        else:
          yCoord = yResolution - 68
        screen.setPanelSize( "ScoreBackground", xResolution - 21 - iWidth, yCoord - (iBtnHeight * iCount) - 4, iWidth + 12, (iBtnHeight * iCount) + 8 )
        screen.show( "ScoreBackground" )

  # Will update the help Strings
  def updateHelpStrings( self ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE_ALL ):
      screen.setHelpTextString( "" )
    else:
      screen.setHelpTextString( CyInterface().getHelpString() )

    return 0

  # Will set the promotion button position
  def setPromotionButtonPosition( self, szName, iPromotionCount ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    # Find out our resolution
    #yResolution = screen.getYResolution()
    #
    #if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
    #  screen.moveItem( szName, 266 - (24 * (iPromotionCount / 6)), yResolution - 144 + (24 * (iPromotionCount % 6)), -0.3 )

# BUG - Stack Promotions - start
    x, y = self.calculatePromotionButtonPosition(screen, iPromotionCount)
    screen.moveItem( szName, x, y, -0.3 )

  def calculatePromotionButtonPosition( self, screen, iPromotionCount ):
    yResolution = screen.getYResolution()
    # x=266, y=144
    return (266 - (24 * (iPromotionCount / 6)), yResolution - 144 + (24 * (iPromotionCount % 6)))
# BUG - Stack Promotions - end

  # Will set the selection button position
  def setResearchButtonPosition( self, szButtonID, iCount ):

    # PAE: x+5 and Original modulo: 15
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    xResolution = screen.getXResolution()
    screen.moveItem( szButtonID, 264 + 5 + ( ( xResolution - 1024 ) / 2 ) + ( 34 * ( iCount % 12 ) ), 0 + ( 34 * ( iCount / 12 ) ), -0.3 )

  # Will set the selection button position
  def setScoreTextPosition( self, szButtonID, iWhichLine ):

    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    yResolution = screen.getYResolution()
    if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
      yCoord = yResolution - 180
    else:
      yCoord = yResolution - 88
    screen.moveItem( szButtonID, 996, yCoord - (iWhichLine * 18), -0.3 )

  # Will build the globeview UI
  def updateGlobeviewButtons( self ):
    kInterface = CyInterface()
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    kEngine = CyEngine()
    kGLM = CyGlobeLayerManager()
    iNumLayers = kGLM.getNumLayers()
    iCurrentLayerID = kGLM.getCurrentLayerID()

    # Positioning things based on the visibility of the globe
    if kEngine.isGlobeviewUp():
      screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 50, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )
    else:
      if ( CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_SHOW ):
        screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 172, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )
      else:
        screen.setHelpTextArea( 350, FontTypes.SMALL_FONT, 7, yResolution - 50, -0.1, False, "", True, False, CvUtil.FONT_LEFT_JUSTIFY, 150 )


    # Set base Y position for the LayerOptions, if we find them
    if CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE:
      iY = yResolution - iGlobeLayerOptionsY_Minimal
    else:
      iY = yResolution - iGlobeLayerOptionsY_Regular

    # Hide the layer options ... all of them
    for i in range (20):
      szName = "GlobeLayerOption" + str(i)
      screen.hide(szName)

    # Setup the GlobeLayer panel
    iNumLayers = kGLM.getNumLayers()
    if kEngine.isGlobeviewUp() and CyInterface().getShowInterface() != InterfaceVisibility.INTERFACE_HIDE_ALL:
      # set up panel
      if iCurrentLayerID != -1 and kGLM.getLayer(iCurrentLayerID).getNumOptions() != 0:
        bHasOptions = True
      else:
        bHasOptions = False
        screen.hide("ScoreBackground")
        screen.hide("ScoreBackground2")

      # set up toggle button
      screen.setState("GlobeToggle", True)

      # Set GlobeLayer indicators correctly
      for i in range(kGLM.getNumLayers()):
        szButtonID = "GlobeLayer" + str(i)
        screen.setState( szButtonID, iCurrentLayerID == i )

      # Set up options pane
      if bHasOptions:
        kLayer = kGLM.getLayer(iCurrentLayerID)

        iCurY = iY
        iNumOptions = kLayer.getNumOptions()
        iCurOption = kLayer.getCurrentOption()
        iMaxTextWidth = -1
        for iTmp in range(iNumOptions):
          iOption = iTmp # iNumOptions - iTmp - 1
          szName = "GlobeLayerOption" + str(iOption)
          szCaption = kLayer.getOptionName(iOption)
          if(iOption == iCurOption):
            szBuffer = "  <color=0,255,0>%s</color>  " % (szCaption)
          else:
            szBuffer = "  %s  " % (szCaption)
          iTextWidth = CyInterface().determineWidth( szBuffer )

          screen.setText( szName, "Background", szBuffer, CvUtil.FONT_LEFT_JUSTIFY, xResolution - 9 - iTextWidth, iCurY-iGlobeLayerOptionHeight-10, -0.3, FontTypes.SMALL_FONT, WidgetTypes.WIDGET_GLOBELAYER_OPTION, iOption, -1 )
          screen.show( szName )

          iCurY -= iGlobeLayerOptionHeight

          if iTextWidth > iMaxTextWidth:
            iMaxTextWidth = iTextWidth

        #make extra space
        iCurY -= iGlobeLayerOptionHeight
        iPanelWidth = iMaxTextWidth + 32
        iPanelHeight = iY - iCurY
        iPanelX = xResolution - 14 - iPanelWidth
        iPanelY = iCurY
        screen.setPanelSize( "ScoreBackground", iPanelX, iPanelY, iPanelWidth, iPanelHeight )
        screen.show( "ScoreBackground" )

    else:
      if iCurrentLayerID != -1:
        kLayer = kGLM.getLayer(iCurrentLayerID)
        if kLayer.getName() == "RESOURCES":
          screen.setState("ResourceIcons", True)
        else:
          screen.setState("ResourceIcons", False)

        if kLayer.getName() == "UNITS":
          screen.setState("UnitIcons", True)
        else:
          screen.setState("UnitIcons", False)
      else:
        screen.setState("ResourceIcons", False)
        screen.setState("UnitIcons", False)

      screen.setState("Grid", CyUserProfile().getGrid())
      screen.setState("BareMap", CyUserProfile().getMap())
      screen.setState("Yields", CyUserProfile().getYields())
      screen.setState("ScoresVisible", CyUserProfile().getScores())

      screen.hide( "InterfaceGlobeLayerPanel" )
      screen.setState("GlobeToggle", False )

  # Update minimap buttons
  def setMinimapButtonVisibility( self, bVisible):
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    kInterface = CyInterface()
    kGLM = CyGlobeLayerManager()
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    if ( CyInterface().isCityScreenUp() ):
      bVisible = False

    kMainButtons = ["UnitIcons", "Grid", "BareMap", "Yields", "ScoresVisible", "ResourceIcons"]
    kGlobeButtons = []
    for i in range(kGLM.getNumLayers()):
      szButtonID = "GlobeLayer" + str(i)
      kGlobeButtons.append(szButtonID)

    if bVisible:
      if CyEngine().isGlobeviewUp():
        kHide = kMainButtons
        kShow = kGlobeButtons
      else:
        kHide = kGlobeButtons
        kShow = kMainButtons
      screen.show( "GlobeToggle" )

    else:
      kHide = kMainButtons + kGlobeButtons
      kShow = []
      screen.hide( "GlobeToggle" )

    for szButton in kHide:
      screen.hide(szButton)

    if CyInterface().getShowInterface() == InterfaceVisibility.INTERFACE_HIDE:
      iY = yResolution - iMinimapButtonsY_Minimal
      iGlobeY = yResolution - iGlobeButtonY_Minimal
    else:
      iY = yResolution - iMinimapButtonsY_Regular
      iGlobeY = yResolution - iGlobeButtonY_Regular

    iBtnX = xResolution - 39
    screen.moveItem("GlobeToggle", iBtnX, iGlobeY, 0.0)

    iBtnAdvance = 28
    iBtnX = iBtnX - len(kShow)*iBtnAdvance - 10
    if len(kShow) > 0:
      i = 0
      for szButton in kShow:
        screen.moveItem(szButton, iBtnX, iY, 0.0)
        screen.moveToFront(szButton)
        screen.show(szButton)
        iBtnX += iBtnAdvance
        i += 1


  def createGlobeviewButtons( self ):
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )

    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    kEngine = CyEngine()
    kGLM = CyGlobeLayerManager()
    iNumLayers = kGLM.getNumLayers()

    for i in range (kGLM.getNumLayers()):
      szButtonID = "GlobeLayer" + str(i)

      kLayer = kGLM.getLayer(i)
      szStyle = kLayer.getButtonStyle()

      if szStyle == 0 or szStyle == "":
        szStyle = "Button_HUDSmall_Style"

      screen.addCheckBoxGFC( szButtonID, "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_GLOBELAYER, i, -1, ButtonStyles.BUTTON_STYLE_LABEL )
      screen.setStyle( szButtonID, szStyle )
      screen.hide( szButtonID )


  def createMinimapButtons( self ):
    screen = CyGInterfaceScreen( "MainInterface", CvScreenEnums.MAIN_INTERFACE )
    xResolution = screen.getXResolution()
    yResolution = screen.getYResolution()

    screen.addCheckBoxGFC( "UnitIcons", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_UNIT_ICONS).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "UnitIcons", "Button_HUDGlobeUnit_Style" )
    screen.setState( "UnitIcons", False )
    screen.hide( "UnitIcons" )

    screen.addCheckBoxGFC( "Grid", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_GRID).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "Grid", "Button_HUDBtnGrid_Style" )
    screen.setState( "Grid", False )
    screen.hide( "Grid" )

    screen.addCheckBoxGFC( "BareMap", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_BARE_MAP).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "BareMap", "Button_HUDBtnClearMap_Style" )
    screen.setState( "BareMap", False )
    screen.hide( "BareMap" )

    screen.addCheckBoxGFC( "Yields", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_YIELDS).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "Yields", "Button_HUDBtnTileAssets_Style" )
    screen.setState( "Yields", False )
    screen.hide( "Yields" )

    screen.addCheckBoxGFC( "ScoresVisible", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_SCORES).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "ScoresVisible", "Button_HUDBtnRank_Style" )
    screen.setState( "ScoresVisible", True )
    screen.hide( "ScoresVisible" )

    screen.addCheckBoxGFC( "ResourceIcons", "", "", 0, 0, 28, 28, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_RESOURCE_ALL).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "ResourceIcons", "Button_HUDBtnResources_Style" )
    screen.setState( "ResourceIcons", False )
    screen.hide( "ResourceIcons" )

    screen.addCheckBoxGFC( "GlobeToggle", "", "", -1, -1, 36, 36, WidgetTypes.WIDGET_ACTION, gc.getControlInfo(ControlTypes.CONTROL_GLOBELAYER).getActionInfoIndex(), -1, ButtonStyles.BUTTON_STYLE_LABEL )
    screen.setStyle( "GlobeToggle", "Button_HUDZoom_Style" )
    screen.setState( "GlobeToggle", False )
    screen.hide( "GlobeToggle" )

  # Will handle the input for this screen...
  def handleInput (self, inputClass):

    # sendModNetMessage -> sends data to GLOBAL GAME AREA (CvEventManager)

# PAE - Great Person Bar - start
    if (inputClass.getNotifyCode() == NotifyCode.NOTIFY_CLICKED and inputClass.getFunctionName().startswith("GreatPersonBar")):
        pPlayer = gc.getActivePlayer()
        iCityPersonRate = iCityPersonProgress = 0
        pCity = ""
        for i in range (pPlayer.getNumCities()):
          if pPlayer.getCity(i).getGreatPeopleProgress() > 0 or pPlayer.getCity(i).getGreatPeopleRate() > 0:
            if iCityPersonProgress < pPlayer.getCity(i).getGreatPeopleProgress():
              iCityPersonRate = pPlayer.getCity(i).getGreatPeopleRate()
              iCityPersonProgress = pPlayer.getCity(i).getGreatPeopleProgress()
              pCity = pPlayer.getCity(i)

        if pCity and not pCity.isNone():
          CyInterface().selectCity(pCity, False)
        return 1
# PAE - Great Person Bar - end

# Field of View
    elif inputClass.getNotifyCode() == NotifyCode.NOTIFY_SLIDER_NEWSTOP:
     if bFieldOfView:
      if inputClass.getFunctionName() == self.szSliderId:
       screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
       self.iField_View = inputClass.getData() + 1
       self.setFieldofView(screen, False)
       self.setFieldofView_Text(screen)
# -------------

    # # PAE TradeRouteAdvisor Screen
    # if inputClass.getButtonType() == WidgetTypes.WIDGET_ACTION and inputClass.getData1() == -1 and inputClass.getData2() == 1:
       # import CvTradeRouteAdvisor
       # CvTradeRouteAdvisor.CvTradeRouteAdvisor().interfaceScreen()
       # return 1
    # if inputClass.getButtonType() == WidgetTypes.WIDGET_ACTION and inputClass.getData1() == -1 and inputClass.getData2() == 2:
       # import CvTradeRouteAdvisor2
       # CvTradeRouteAdvisor2.CvTradeRouteAdvisor().interfaceScreen()
       # return 1

    # PAE TradeRouteAdvisor Screen
    if inputClass.getButtonType() == WidgetTypes.WIDGET_GENERAL and inputClass.getData1() == 10000 and inputClass.getData2() == 1:
        import CvTradeRouteAdvisor
        CvTradeRouteAdvisor.CvTradeRouteAdvisor().interfaceScreen()
        return 1
    if inputClass.getButtonType() == WidgetTypes.WIDGET_GENERAL and inputClass.getData1() == 10000 and inputClass.getData2() == 2:
        import CvTradeRouteAdvisor2
        CvTradeRouteAdvisor2.CvTradeRouteAdvisor().interfaceScreen()
        return 1

    # Initialisierung
    if g_pSelectedUnit:
      iOwner = g_pSelectedUnit.getOwner()
      iUnitID = g_pSelectedUnit.getID()
      pPlot = g_pSelectedUnit.plot()

    if inputClass.getButtonType() == WidgetTypes.WIDGET_GENERAL:
     if inputClass.getNotifyCode() == 11:
      iData1  = inputClass.getData1()
      iData2  = inputClass.getData2()
      bOption = inputClass.getOption()

      # Inquisitor
      if iData1 == 665 and iData2 == 665:
        CyMessageControl().sendModNetMessage( 665, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Horse down
      elif iData1 == 666 and iData2 == 666:
        CyAudioGame().Play2DSound('AS2D_HORSE_DOWN')
        CyMessageControl().sendModNetMessage( 666, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Horse up
      elif iData1 == 667 and iData2 == 667:
        CyAudioGame().Play2DSound('AS2D_HORSE_UP')
        CyMessageControl().sendModNetMessage( 667, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Bordell / Freudenhaus
      elif iData1 == 668 and iData2 == 668:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 668, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Gladiator
      elif iData1 == 669 and iData2 == 669:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 669, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Theater
      elif iData1 == 670 and iData2 == 670:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 670, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 671 frei

      # Auswanderer / Emigrant
      elif iData1 == 672 and iData2 == 672:
        CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_SETTLER')
        CyMessageControl().sendModNetMessage( 672, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Stadt auflösen / disband city
      elif iData1 == 673 and iData2 == 673 and bOption:
        CyMessageControl().sendModNetMessage( 673, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 674 vergeben durch Hunnen-PopUp (CvScreensInterface - popupHunsPayment)

      # ID 675 vergeben durch Revolten-PopUp (CvScreensInterface - popupRevoltPayment)

      # ID 676 vergeben durch freie Unit durch Tech (Kulte)

      # Gold in die Schatzkammer bringen
      elif iData1 == 677 and iData2 == 677:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 677, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 678 vergeben durch Provinz-PopUp

      # Sklave -> Schule
      elif iData1 == 679 and iData2 == 679:
        CyAudioGame().Play2DSound('AS2D_BUILD_UNIVERSITY')
        CyMessageControl().sendModNetMessage( 679, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Manufaktur Nahrung
      elif iData1 == 680 and iData2 == 680:
        CyAudioGame().Play2DSound('AS2D_BUILD_GRANARY')
        CyMessageControl().sendModNetMessage( 680, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Manufaktur Produktion
      elif iData1 == 681 and iData2 == 681:
        CyAudioGame().Play2DSound('AS2D_BUILD_FORGE')
        CyMessageControl().sendModNetMessage( 681, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

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

      # Sklave -> Palast
      elif iData1 == 692 and iData2 == 692:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 692, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave -> Tempel
      elif iData1 == 693 and iData2 == 693:
        CyAudioGame().Play2DSound('AS2D_BUILD_TAOIST')
        CyMessageControl().sendModNetMessage( 693, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sklave wird verkauft
      elif iData1 == 694 and iData2 == 694:
        CyAudioGame().Play2DSound('AS2D_COINS')
        CyMessageControl().sendModNetMessage( 694, iOwner, iUnitID, 0, 0 )

      # Unit wird verkauft
      elif iData1 == 695:
        # Confirmation required
        CyMessageControl().sendModNetMessage( 695, 0, 0, iOwner, iUnitID )

      # Sklave -> Feuerwehr
      elif iData1 == 696 and iData2 == 696:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 696, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Trojanisches Pferd
      elif iData1 == 697 and iData2 == 697:
        CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_UNIT')
        CyMessageControl().sendModNetMessage( 697, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 698 vergeben durch freie Unit durch Tech (Religion)

      # ID 699 Kauf einer Edlen Ruestung
      elif iData1 == 699 and bOption:
        CyAudioGame().Play2DSound('AS2D_COINS')
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 699, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 700 Pillage Road
      elif iData1 == 700 and iData2 == 700:
        CyAudioGame().Play2DSound('AS2D_PILLAGE')
        CyMessageControl().sendModNetMessage( 700, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 701 Kauf des Wellen-Oels
      elif iData1 == 701 and bOption:
        CyAudioGame().Play2DSound('AS2D_COINS')
        CyMessageControl().sendModNetMessage( 701, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # ID 702 PopUp Vassal Tech
      # ID 703 PopUp Vassal Tech2
      # ID 704 Religionsaustreibung

      # ID 705 Update Veteran Einheit zu neuer Elite Einheit
      # Bsp: Principes or Hastati Veterans -> Triarii
      elif iData1 == 705:
        CyAudioGame().Play2DSound("AS2D_IF_LEVELUP")
        CyAudioGame().Play2DSound("AS2D_WELOVEKING")
        CyMessageControl().sendModNetMessage( 705, 0, iData2, iOwner, iUnitID )

      # ID 706 PopUp Renegade City (keep or raze)

      # ID 707 Soeldner anheuern / Mercenaries hire or assign
      elif iData1 == 707 and iData2 == 707:
        CyMessageControl().sendModNetMessage( 707, pPlot.getPlotCity().getID(), -1, -1, iOwner )

      # ID 708-715 Hire/Assign Mercenaries
      # ID 716-717 Mercenary Torture

      # ID 718 Unit Formations
      elif iData2 == 718 and bOption:
        if g_pSelectedUnit.getUnitCombatType() == gc.getInfoTypeForString("UNITCOMBAT_NAVAL"):
          CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_GALLEY')
        else:
          CyAudioGame().Play2DSound('AS2D_BUILD_BARRACKS')
        CyMessageControl().sendModNetMessage( 718, 0, inputClass.getData1(), iOwner, iUnitID )

      # ID 719 Promotion Trainer Building (Forest 1, Hills1, ...)
      elif iData1 == 719:
        CyAudioGame().Play2DSound('AS2D_BUILD_BARRACKS')
        CyMessageControl().sendModNetMessage( 719, pPlot.getPlotCity().getID(), iData2, iOwner, iUnitID )

      # ID 720 Legendary Hero can become a Great General
      elif iData1 == 720:
        CyAudioGame().Play2DSound('AS2D_WELOVEKING')
        CyMessageControl().sendModNetMessage( 720, 0, 0, iOwner, iUnitID )

      # ID 721 Elefantenstall
      elif iData1 == 721:
        if iData2 == 1:
          CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_WAR_ELEPHANT')
          CyMessageControl().sendModNetMessage( 721, pPlot.getPlotCity().getID(), 1, iOwner, iUnitID )
        if iData2 == 4:
          CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_ARABIAN_CAMEL_ARCHER')
          CyMessageControl().sendModNetMessage( 721, pPlot.getPlotCity().getID(), 2, iOwner, iUnitID )


      # ID 722 Piraten-Feature
      # Data2=1: Pirat->Normal, Data2=2: Normal->Pirat
      elif iData1 == 722:
        if iData2 != 3:
          CyAudioGame().Play2DSound('AS2D_UNIT_BUILD_GALLEY')
          CyMessageControl().sendModNetMessage( 722, iData2, 0, iOwner, iUnitID )

      # ID 723 EspionageMission Info im TechChooser

      # ID 724 Veteran Unit -> Reservist in city
      elif iData1 == 724:
        CyAudioGame().Play2DSound("AS2D_GOODY_SETTLER")
        CyMessageControl().sendModNetMessage( 724, pPlot.getPlotCity().getID(), 0, iOwner, iUnitID )

      # ID 725 Reservist -> Veteran Unit
      elif iData1 == 725:
        CyMessageControl().sendModNetMessage( 725, pPlot.getPlotCity().getID(), iOwner, -1, 0 )

      # ID 726 Bonusverbreitung (Obsolete)
      #elif iData1 == 726:
      #  CyMessageControl().sendModNetMessage( 726, -1, -1, iOwner, iUnitID )

      # ID 727 Nahrung an Stadt liefern
      elif iData1 == 727:
        CyAudioGame().Play2DSound("AS2D_BUILD_GRANARY")
        CyMessageControl().sendModNetMessage( 727, pPlot.getPlotCity().getID(), 0, iOwner, iUnitID )

      # ID 728 Karte zeichnen
      elif iData1 == 728:
        CyMessageControl().sendModNetMessage( 728, -1, -1, iOwner, iUnitID )

      # Sklave -> Library
      elif iData1 == 729:
        CyAudioGame().Play2DSound('AS2D_BUILD_UNIVERSITY')
        CyMessageControl().sendModNetMessage( 729, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Release slaves
      elif iData1 == 730:
        CyMessageControl().sendModNetMessage( 730, pPlot.getPlotCity().getID(), 0, iOwner, -1 )

      # Send Missionary to a friendly city
      elif iData1 == 731:
        CyMessageControl().sendModNetMessage( 731, -1, -1, iOwner, iUnitID )

      # Send Trade merchant into next foreign city (Obsolete)
      #elif iData1 == 732:
      #  CyMessageControl().sendModNetMessage( 732, -1, -1, iOwner, iUnitID )

      # Build Limes PopUp
      elif iData1 == 733:
        CyMessageControl().sendModNetMessage( 733, -1, -1, iOwner, iUnitID )

      # Sklaven zu Feldsklaven oder Bergwerkssklaven
      elif iData1 == 734:
        if iData2 == 1:
          if bOption: CyMessageControl().sendModNetMessage( 734, pPlot.getPlotCity().getID(), 1, iOwner, iUnitID )
        elif iData2 == 2:
          if bOption: CyMessageControl().sendModNetMessage( 734, pPlot.getPlotCity().getID(), 2, iOwner, iUnitID )

      # Salae oder Dezimierung
      elif iData1 == 735:
        if iData2 == 1:
          if bOption: CyMessageControl().sendModNetMessage( 735, 1, 0, iOwner, iUnitID )
        elif iData2 == 2:
          if bOption: CyMessageControl().sendModNetMessage( 735, 2, 0, iOwner, iUnitID )

      # Handelsposten erstellen
      elif iData1 == 736:
        CyMessageControl().sendModNetMessage( 736, 0, 0, iOwner, iUnitID )

      # Provinzstatthalter / Tribut
      elif iData1 == 737:
        CyMessageControl().sendModNetMessage( 737, pPlot.getPlotCity().getID(), iOwner, -1, -1 )

      # Bonus cultivation (Boggy)
      elif iData1 == 738:
        # Karren aufladen
        if bOption: iIsCity = 1
        else: iIsCity = 0
        CyMessageControl().sendModNetMessage( 738, iOwner, iUnitID, iIsCity, -1)

      # Collect bonus (iData2: 0 = remove, 1 = kaufen)
      elif iData1 == 739:
        if bOption: CyMessageControl().sendModNetMessage( 739, -1, iData2, iOwner, iUnitID )

      # Buy bonus (in city)
      elif iData1 == 740:
        CyMessageControl().sendModNetMessage( 740, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Sell bonus (in city)
      elif iData1 == 741:
        CyMessageControl().sendModNetMessage( 741, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # 742 is used by CvScreensInterface.

      # Automated trade route - choose civ 1
      elif iData1 == 744:
        CyMessageControl().sendModNetMessage( 744, -1, -1, iOwner, iUnitID )

      # 745, 746, 747 are used by CvScreensInterface.

      elif iData1 == 748:
        CyMessageControl().sendModNetMessage( 748, -1, -1, iOwner, iUnitID )

      # 749: Generelle MouseOverInfos lediglich fuer (aktionslose) Buttons

      # 750: Unit Ethnic Info

      # Unit Rang Promo / Upgrade to new unit with new rank
      elif iData1 == 751:
       # Unit is in capital city
       if bOption:
          CyAudioGame().Play2DSound('AS2D_COINS')
          CyAudioGame().Play2DSound("AS2D_IF_LEVELUP")
          CyAudioGame().Play2DSound("AS2D_WELOVEKING")
          CyMessageControl().sendModNetMessage( 751, -1, -1, iOwner, iUnitID )

      # Bless units
      elif iData1 == 752:
        CyAudioGame().Play2DSound('AS2D_BUILD_CHRISTIAN')
        CyMessageControl().sendModNetMessage( 752, pPlot.getX(), pPlot.getY(), iOwner, iUnitID )

      # Slave -> Latifundium
      elif iData1 == 753:
        CyAudioGame().Play2DSound('AS2D_BUILD_GRANARY')
        CyMessageControl().sendModNetMessage( 753, 0, 0, iOwner, iUnitID )


# Zusatz: Eigenes Widget for Formations !!!
    if inputClass.getButtonType() == WidgetTypes.WIDGET_HELP_PROMOTION:
      # ID 718 Unit Formations
      if (inputClass.getNotifyCode() == 11 and inputClass.getData2() == 718 and inputClass.getOption()):
        CyAudioGame().Play2DSound('AS2D_BUILD_BARRACKS')
        CyMessageControl().sendModNetMessage( 718, 0, inputClass.getData1(), iOwner, iUnitID )


# Platy ScoreBoard - Start
    if inputClass.getFunctionName() == "ScoreRowPlus":
      self.iScoreRows -= 1
      self.updateScoreStrings()
    elif inputClass.getFunctionName() == "ScoreRowMinus":
      self.iScoreRows += 1
      self.updateScoreStrings()
    elif inputClass.getFunctionName() == "ScoreWidthPlus":
      self.iScoreWidth += 10
      self.updateScoreStrings()
    elif inputClass.getFunctionName() == "ScoreWidthMinus":
      self.iScoreWidth = max(0, self.iScoreWidth - 10)
      self.updateScoreStrings()
    elif inputClass.getFunctionName() == "ScoreHidePoints":
      if not self.iScoreHidePoints: self.iScoreHidePoints = True
      else:  self.iScoreHidePoints = False
      self.updateScoreStrings()

# Platy ScoreBoard - End

# PAE, Ramk - Fix jumping in build menu
    if inputClass.getButtonType() in self.buildWidges:
      if( inputClass.getFunctionName() == "BottomButtonContainer" ):
        screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
        """ This just work in fullscreen mode
        iRow = self.findIconRow( inputClass.getButtonType(), inputClass.getData1() )
        #This change could be False in window mode.
        if self.secondRowBorder < CyInterface().getMousePos().y:
          iRow -= 1
        """
        # Use mouse clicks to estimate border between both rows.
        iRow = self.findIconRow( inputClass.getButtonType(), inputClass.getData1() )
        y = CyInterface().getMousePos().y
        self.ySecondRow = max(self.ySecondRow, y)
        if( (y - self.ySecondRow + 100) > (self.ySecondRow - y) ):
          iRow -= 1
        CyInterface().setCityTabSelectionRow(iRow)
        screen.selectMultiList( "BottomButtonContainer", iRow )

    elif inputClass.getData1() == 88000:
      # CITY_TAB replacements
      screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
      iRow = self.cityTabsJumpmarks[inputClass.getData2()]
      CyInterface().setCityTabSelectionRow(iRow)
      screen.selectMultiList( "BottomButtonContainer", iRow )

# PAE, Ramk - End


    return 0

  def update(self, fDelta):
    return

  def forward(self):
                if (not CyInterface().isFocused() or CyInterface().isCityScreenUp()):
                        if (CyInterface().isCitySelection()):
                                CyGame().doControl(ControlTypes.CONTROL_NEXTCITY)
                        else:
                                CyGame().doControl(ControlTypes.CONTROL_NEXTUNIT)

  def back(self):
                if (not CyInterface().isFocused() or CyInterface().isCityScreenUp()):
                        if (CyInterface().isCitySelection()):
                                CyGame().doControl(ControlTypes.CONTROL_PREVCITY)
                        else:
                                CyGame().doControl(ControlTypes.CONTROL_PREVUNIT)

# BUG - field of view
  def setFieldofView(self, screen, bDefault):
    if bDefault:
      self._setFieldofView(screen, DEFAULT_FIELD_OF_VIEW)
    else:
      self._setFieldofView(screen, self.iField_View)

  def _setFieldofView(self, screen, iFoV):
    if self.iField_View_Prev != iFoV:
      gc.setDefineFLOAT("FIELD_OF_VIEW", float(iFoV))
      self.iField_View_Prev = iFoV

  def setFieldofView_Text(self, screen):
    zsFieldOfView_Text = "%s [%i]" % (self.sFieldOfView_Text, self.iField_View)
    screen.setLabel(self.szSliderTextId, "", zsFieldOfView_Text, CvUtil.FONT_RIGHT_JUSTIFY, self.iX_FoVSlider, self.iY_FoVSlider + 6, 0, FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
# BUG - field of view end


# PAE, Ramk - Position der Bauauftrag-Icons optimieren
  def sortButtons( self, buttons, maxNumIcons):
    if maxNumIcons < 1:
      return
    numRows = len(buttons)
    iRow = 0
    while iRow < numRows:
      # Entferne leere Zeilen
      if len(buttons[iRow]) == 0:
        del buttons[iRow]
        numRows -= 1
        continue

      # Entfernte None-Einträge nach ihrer Benutzung und bevor die Länge der Liste benutzt wird.
      if buttons[iRow][0] == None:
        del buttons[iRow][0]
        continue

      if len(buttons[iRow]) > maxNumIcons:
        if( iRow < numRows-1 and
            ( len(buttons[iRow+1]) == 0 or buttons[iRow+1][0] != None) ):
          #Shift to next row
          buttons[iRow+1] = buttons[iRow][maxNumIcons:] + buttons[iRow+1]
          del buttons[iRow][maxNumIcons:]
        else:
          #Insert new row
          buttons.insert(iRow+1, buttons[iRow][maxNumIcons:])
          del buttons[iRow][maxNumIcons:]
          numRows += 1
      iRow += 1


  # Ermittle, ob links weniger genutzt wird als vorhanden ist
  # und gebe es der rechten Seite, falls es dort benötigt wird.
  def optimalPartition( self, numIconsLeft, numIconsRight, leftButtons, rightButtons):
    if len(leftButtons) > 0:
      maxUsedWidthLeft = max( [ len(x) for x in leftButtons ] )
    else:
      maxUsedWidthLeft = 0
    if( maxUsedWidthLeft >= numIconsLeft ):
      return [numIconsLeft, numIconsRight]
      #return [maxUsedWidthLeft, numIconsRight - ( maxUsedWidthLeft - numIconsLeft )]

    if len(rightButtons) > 0:
      maxUsedWidthRight = max( [ len(x) for x in rightButtons ] )
    else:
      maxUsedWidthRight = 0
    if( maxUsedWidthRight >= numIconsRight ):
      return [maxUsedWidthLeft, numIconsRight + ( numIconsLeft - maxUsedWidthLeft )]

    return [numIconsLeft, numIconsRight]

  def insertButtons( self, leftButtons, rightButtons, numIconsLeft, numIcons):
    """ Remark: Structure of objects in *Buttons[i][j]:
     (
      [szButton, WidgetTypes.WIDGET_TRAIN, i, -1, False],
      isBuildable-Flag,
      cityTab-Index
     )
    """
    screen = CyGInterfaceScreen("MainInterface", CvScreenEnums.MAIN_INTERFACE)
    emptyButton = "Art/Interface/Buttons/empty.dds"
    lastRow = max(len(leftButtons),len(rightButtons))-1

    for iRow in range( lastRow+1 ):
      iCount = 0
      # Left Icons
      if iRow<len(leftButtons):
        for iconData in leftButtons[iRow]:
          if iconData == None:
            continue
          # Die Liste iconData[0] entspricht fast der Argumentliste von appendMultiListButton.
          # Es muss aber noch das dritte Argument eingefügt werden
          iconData[0].insert(1,iRow)
          screen.appendMultiListButton( "BottomButtonContainer", *(iconData[0]) )
          if not iconData[1]:
            screen.disableMultiListButton( "BottomButtonContainer", iRow, iCount, iconData[0][0])
          iCount += 1

      # Insert Dummy icon on empty positions. Add extra column to separate both groups.
      while iCount < numIconsLeft:
        screen.appendMultiListButton( "BottomButtonContainer", emptyButton, iRow, WidgetTypes.WIDGET_GENERAL, 99999, 99999, False )
        screen.disableMultiListButton( "BottomButtonContainer", iRow, iCount, emptyButton)
        iCount += 1

      # Right Icons
      if iRow<len(rightButtons):
        for iconData in rightButtons[iRow]:
          if iconData == None:
            continue
          if len(iconData[0]) != 5: # Ursache für teilweise falsche Listenlänge unbekannt.
            continue
          iconData[0].insert(1,iRow)
          screen.appendMultiListButton( "BottomButtonContainer", *(iconData[0]) )
          if not iconData[1]:
            screen.disableMultiListButton( "BottomButtonContainer", iRow, iCount, iconData[0][0])
          iCount += 1

      # Insert Dummy icon on empty positions to fill up whole row
      if iRow != lastRow:
        while iCount < numIcons:
          screen.appendMultiListButton( "BottomButtonContainer", emptyButton, iRow, WidgetTypes.WIDGET_GENERAL, 99999, 99999, False )
          screen.disableMultiListButton( "BottomButtonContainer", iRow, iCount, emptyButton)
          iCount += 1

  def findCityTabRow(self, buttons, cityTabIndex):
    for iRow in range(len(buttons)):
      for iconData in buttons[iRow]:
        if iconData == None:
          continue
        if iconData[2] == cityTabIndex:
          return iRow
        # Just test the first icon in each line
        break
    # index not founded
    return len(buttons)

  # Achtung, in iconData[0] wird in der insertButtons-Methode
  # vorne ein Element eingefügt. Das verschiebt Listenelemente nach hinten.
  def findIconRow(self, buildType, index ):
    offset = 0
    if buildType == WidgetTypes.WIDGET_TRAIN:
      buttons = self.iconsLeft
    else:
      buttons = self.iconsRight
      if self.m_iNumMenuButtons < 16:
        offset = len(self.iconsLeft)

    for iRow in range(len(buttons)):
      for iconData in buttons[iRow]:
        if iconData == None:
          continue
        if iconData[0][3] == index and iconData[0][2] == buildType:
          return iRow+offset
    return 0


  """PAE, Ramk:
    Die ursprünglichen CITY_TAB-Buttons koennen nur auf die Zeilen 0,1 und 2 springen und
    diese stehen immer für Einheiten, Gebaeude und Wunder.
    Daher sind die Buttons durch eigene (WIDGET_GENERAL) ausgetauscht worden.
  """
  def updateCityTabs(self, screen):
    iBtnX = self.xResolution - 324
    iBtnY = self.yResolution - 94
    iBtnWidth = 24
    iBtnAdvance = 24
    iBtnX = screen.getXResolution() - 324
    iBtnY = screen.getYResolution() - 94

    #screen.setButtonGFC( "CityTab0", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_CITY_TAB, jumpMarks[0], -1, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setButtonGFC( "CityTab0", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_GENERAL, 88000, 0, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setStyle( "CityTab0", "Button_HUDJumpUnit_Style" )
    #screen.hide( "CityTab0" )

    iBtnY += iBtnAdvance
    #screen.setButtonGFC( "CityTab1", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_CITY_TAB, jumpMarks[1], -1, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setButtonGFC( "CityTab1", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_GENERAL, 88000, 1, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setStyle( "CityTab1", "Button_HUDJumpBuilding_Style" )
    #screen.hide( "CityTab1" )

    iBtnY += iBtnAdvance
    #screen.setButtonGFC( "CityTab2", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_CITY_TAB, jumpMarks[2], -1, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setButtonGFC( "CityTab2", "", "", iBtnX, iBtnY, iBtnWidth, iBtnWidth, WidgetTypes.WIDGET_GENERAL, 88000, 2, ButtonStyles.BUTTON_STYLE_STANDARD )
    screen.setStyle( "CityTab2", "Button_HUDJumpWonder_Style" )
    #screen.hide( "CityTab2" )

# End PAE