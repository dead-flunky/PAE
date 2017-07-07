from CvPythonExtensions import *
import CvUtil
import ScreenInput
import CvScreenEnums
import WBEventScreen
import WBCityEditScreen
import WBUnitScreen
import WBPlayerScreen
import WBTeamScreen
import WBInfoScreen
import WBPlotScreen
import CvPlatyBuilderScreen
import CvEventManager
import CvRiverUtil
import Popup
gc = CyGlobalContext()

bAdd = True
bSensibility = True
bFord = False  # 0 - River, 1 - River with Furt
iSelectedSide = 0  # 0 - left river side, 1 - right river side (or similar)
iEditType = 0
iCounter = -1

bRiverAutomatic = False  # 1 - Select orientation, textures, etc. automaticly.
bRiverBranch = False  # 1 - Change whole branch of river
bRiverComplete = False  # 1 - Change whole river, includes bRiverBranch

#ButtonIconPath = ",Art/no_file.dds,Art/Interface/Buttons/TerrainFeatures/button_feature_darkice2.dds,"
ButtonIconPath = ",Art/no_file.dds,Art/Terrain/features/RiverPackV8/buttons.dds,"
ButtonIconCoords = {
    "RIVER_NS": "3,1",
    "RIVER_WE": "4,1",
    "RIVER_NW": "2,2",
    "RIVER_NE": "1,2",
    "RIVER_SW": "2,1",
    "RIVER_SE": "1,1",
    "DEST_N": "1,5",
    "DEST_W": "3,5",
    "DEST_S": "2,5",
    "DEST_E": "4,5",
    "SOURCE_N": "1,4",
    "SOURCE_W": "3,4",
    "SOURCE_S": "2,4",
    "SOURCE_E": "4,4",
    "BRANCH_N": "2,3",
    "BRANCH_W": "3,3",
    "BRANCH_S": "1,3",
    "BRANCH_E": "4,3",
    "Ford": "5,2",
    "Auto": "5,3",
    "All": "5,4",
    "Branch": "5,5",
}


def getRiverIcon(key):
    try:
        return ButtonIconPath+ButtonIconCoords[key]
    except KeyError:
        global riverIds
        return gc.getFeatureInfo((riverIds["features"][0])).getButton()


class WBRiverScreen:

    def __init__(self):
        self.iTable_Y = 110

        # Generate list to assoziate items of dropdown menu
        # with RiverDesc.
        rt = CvRiverUtil.RiverTypes
        self.lRiveralign = []
        for rtype, aligns in rt.iteritems():
            for align, versions in aligns.iteritems():
                self.lRiveralign.append((rtype, align))

    def interfaceScreen(self, pPlotX):
        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        global pPlot
        global iWidth
        pPlot = pPlotX
        iWidth = screen.getXResolution()/5 - 20

        # ScriptField is linked with other screen
        WBPlotScreen.iWidth = screen.getXResolution()/5 - 20
        WBPlotScreen.pPlot = pPlot

        global riverIds
        riverIds = {}
        """ # Dies produziert Fehler?!
        riverIds["terrains"] = [
            CvUtil.findInfoTypeNum(
                gc.getTerrainInfo,
                gc.getNumTerrainInfos(),
                'TERRAIN_RIVER'),
            CvUtil.findInfoTypeNum(
                gc.getTerrainInfo,
                gc.getNumTerrainInfos(),
                'TERRAIN_RIVER_FORD')
            ],
        riverIds["features"] = [
            CvUtil.findInfoTypeNum(
                gc.getFeatureInfo,
                gc.getNumFeatureInfos(),
                'FEATURE_RIVER'),
            CvUtil.findInfoTypeNum(
                gc.getFeatureInfo,
                gc.getNumFeatureInfos(),
                'FEATURE_RIVER_FORD')
        ],
        """
        riverIds["terrains"] = [
            gc.getInfoTypeForString("TERRAIN_RIVER"),
            gc.getInfoTypeForString("TERRAIN_RIVER_FORD")]
        riverIds["features"] = [
            gc.getInfoTypeForString("FEATURE_RIVER"),
            gc.getInfoTypeForString("FEATURE_RIVER_FORD")]
        riverIds["varieties"] = [1, 2, 3, 4]  # Not used

        # Closer look at plot
        """
        # Hm, Kamera wird bei offenem WB-Screen zurückgesetzt...
        CyCamera().SetZoom(0.1)
        """

        global bFord
        bFord = pPlot.getTerrainType() is riverIds["terrains"][1]

        screen.setRenderInterfaceOnly(True)
        screen.addPanel("MainBG", u"", u"", True, False, -
                        10, -
                        10, screen.getXResolution() +
                        20, screen.getYResolution() +
                        20, PanelStyles.PANEL_STYLE_MAIN)
        screen.showScreen(PopupStates.POPUPSTATE_IMMEDIATE, False)

        screen.setText("PlotExit", "Background", "<font=4>" + CyTranslator().
                       getText("TXT_KEY_PEDIA_SCREEN_EXIT", ()).upper() +
                       "</font>", CvUtil.FONT_RIGHT_JUSTIFY,
                       screen.getXResolution() - 30, screen.getYResolution() -
                       42, -0.1, FontTypes.TITLE_FONT,
                       WidgetTypes.WIDGET_CLOSE_SCREEN, -1, -1)

        iX = 10

        # Toggle buttons
        iX_right = screen.getXResolution() * 2/5 + 34
        # iY = 50
        # iY += 30
        # iY += 30
        iY = screen.getYResolution() - 280
        iButtonWidth = 28

        screen.addCheckBoxGFC(
            "SensibilityCheck",
            ",Art/Interface/Buttons/WorldBuilder/Gems.dds,Art/Interface/Buttons/FinalFrontier1_Atlas.dds,1,16",
            CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
            iX_right,
            iY,
            iButtonWidth,
            iButtonWidth,
            WidgetTypes.WIDGET_PYTHON,
            1029,
            24,
            ButtonStyles.BUTTON_STYLE_LABEL)
        screen.setState("SensibilityCheck", bSensibility)

        #sText = CyTranslator().getText("TXT_KEY_RIVER_SENSIBILITY_CHECK", ())
        sText = CyTranslator().getText("TXT_KEY_WB_SENSIBILITY", ())
        screen.setLabel(
            "SensiblityCheckText", "Background", "<font=3>" + sText + "</font>",
            CvUtil.FONT_LEFT_JUSTIFY, iX_right + 30, iY + 4, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        iY += 30
        screen.addCheckBoxGFC(
            "FordCheck",
            ButtonIconPath +
            ButtonIconCoords["Ford"],
            CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
            iX_right,
            iY,
            iButtonWidth,
            iButtonWidth,
            WidgetTypes.WIDGET_PYTHON,
            1029,
            35,
            ButtonStyles.BUTTON_STYLE_LABEL)
        screen.setState("FordCheck", bFord)

        sText = CyTranslator().getText("TXT_KEY_RIVER_FORD_CHECK", ())
        screen.setLabel(
            "FordCheckText", "Background", "<font=3>" + sText + "</font>",
            CvUtil.FONT_LEFT_JUSTIFY,
            iX_right + 30, iY + 4,
            -0.1, FontTypes.GAME_FONT,
            WidgetTypes.WIDGET_GENERAL, -1, -1)

        iY += 30
        screen.addCheckBoxGFC(
            "RiverAutomaticCheck",
            ButtonIconPath +
            ButtonIconCoords["Auto"],
            CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
            iX_right,
            iY,
            iButtonWidth,
            iButtonWidth,
            WidgetTypes.WIDGET_PYTHON,
            1029,
            36,
            ButtonStyles.BUTTON_STYLE_LABEL)
        screen.setState("RiverAutomaticCheck", bRiverAutomatic)

        sText = CyTranslator().getText("TXT_KEY_RIVER_AUTOMATIC_CHECK", ())
        screen.setLabel(
            "RiverAutomaticCheckText", "Background", "<font=3>" + sText +
            "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX_right + 30, iY + 4, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        iY += 30
        screen.addCheckBoxGFC(
            "RiverBranchCheck",
            ButtonIconPath +
            ButtonIconCoords["Branch"],
            CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
            iX_right,
            iY,
            iButtonWidth,
            iButtonWidth,
            WidgetTypes.WIDGET_PYTHON,
            1029,
            37,
            ButtonStyles.BUTTON_STYLE_LABEL)
        screen.setState("RiverBranchCheck", bRiverBranch)

        sText = CyTranslator().getText("TXT_KEY_RIVER_BRANCH_CHECK", ())
        screen.setLabel(
            "RiverBranchCheckText", "Background", "<font=3>" + sText + "</font>",
            CvUtil.FONT_LEFT_JUSTIFY, iX_right + 30, iY + 4, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        iY += 30
        screen.addCheckBoxGFC(
            "RiverCompleteCheck",
            ButtonIconPath +
            ButtonIconCoords["All"],
            CyArtFileMgr().getInterfaceArtInfo("BUTTON_HILITE_SQUARE").getPath(),
            iX_right,
            iY,
            iButtonWidth,
            iButtonWidth,
            WidgetTypes.WIDGET_PYTHON,
            1029,
            38,
            ButtonStyles.BUTTON_STYLE_LABEL)
        screen.setState("RiverCompleteCheck", bRiverComplete)

        sText = CyTranslator().getText("TXT_KEY_RIVER_COMPLETE_CHECK", ())
        screen.setLabel(
            "RiverCompleteCheckText", "Background", "<font=3>" + sText +
            "</font>", CvUtil.FONT_LEFT_JUSTIFY, iX_right + 30, iY + 4, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        # Seitenwechsler unten links
        screen.addDropDownBoxGFC(
            "CurrentPage", iX, screen.getYResolution() - 42, iWidth,
            WidgetTypes.WIDGET_GENERAL, -1, -1, FontTypes.GAME_FONT)
        screen.addPullDownString(
            "CurrentPage",
            CyTranslator().getText(
                "TXT_KEY_WB_PLOT_DATA",
                ()),
            12,
            12,
            False)
        screen.addPullDownString(
            "CurrentPage",
            CyTranslator().getText(
                "TXT_KEY_CONCEPT_EVENTS",
                ()),
            1,
            1,
            False)
        if pPlot.isOwned():
            screen.addPullDownString(
                "CurrentPage",
                CyTranslator().getText(
                    "TXT_KEY_WB_PLAYER_DATA",
                    ()),
                2,
                2,
                False)
            screen.addPullDownString(
                "CurrentPage",
                CyTranslator().getText(
                    "TXT_KEY_WB_TEAM_DATA",
                    ()),
                3,
                3,
                False)
            if pPlot.isCity():
                screen.addPullDownString(
                    "CurrentPage",
                    CyTranslator().getText(
                        "TXT_KEY_WB_CITY_DATA",
                        ()),
                    4,
                    4,
                    False)
        if pPlot.getNumUnits() > 0:
            screen.addPullDownString(
                "CurrentPage",
                CyTranslator().getText(
                    "TXT_KEY_WB_UNIT_DATA",
                    ()),
                5,
                5,
                False)
        screen.addPullDownString(
            "CurrentPage",
            CyTranslator().getText(
                "TXT_KEY_INFO_SCREEN",
                ()),
            11,
            11,
            False)
        screen.addPullDownString(
            "CurrentPage",
            CyTranslator().getText(
                "TXT_KEY_WB_RIVER_DATA",
                ()),
            0,
            0,
            True)

        iIndex = -1
        for i in xrange(CyMap().numPlots()):
            pLoopPlot = CyMap().plotByIndex(i)
            if pLoopPlot.getX() == pPlot.getX() and pLoopPlot.getY() == pPlot.getY():
                iIndex = i
                break
        sText = CyTranslator().getText("TXT_KEY_WB_RIVER_DATA", ())
        if pPlot.isCity():
            pCity = pPlot.getPlotCity()
            sText += " (" + pCity.getName() + ")"
        screen.setLabel(
            "PlotScreenHeader", "Background", "<font=4b>" + sText + "</font>",
            CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() / 2, 20, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
        sText = u"<font=3b>%s ID: %d, %s: %d</font>" % (
            CyTranslator().getText("TXT_KEY_WB_RIVER_DATA", ()), iIndex,
            CyTranslator().getText("TXT_KEY_WB_AREA_ID", ()), pPlot.getArea())
        screen.setLabel(
            "PlotScreenHeaderB", "Background", "<font=4b>" + sText + "</font>",
            CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() / 2, 50, -0.1,
            FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)

        screen.setImageButton(
            "NextPlotUpButton", CyArtFileMgr().getInterfaceArtInfo(
                "INTERFACE_GENERAL_UPARROW").getPath(), screen.getXResolution() /
            2 - 12, self.iTable_Y, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setImageButton("NextPlotDownButton", CyArtFileMgr().
                              getInterfaceArtInfo(
                                  "INTERFACE_GENERAL_DOWNARROW").getPath(),
                              screen.getXResolution() / 2 - 12, self.iTable_Y +
                              48, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setImageButton(
            "NextPlotLeftButton", CyArtFileMgr().getInterfaceArtInfo(
                "INTERFACE_BUTTONS_LEFT").getPath(), screen.getXResolution() / 2 -
            36, self.iTable_Y + 24, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.setImageButton(
            "NextPlotRightButton", CyArtFileMgr().getInterfaceArtInfo(
                "INTERFACE_BUTTONS_RIGHT").getPath(), screen.getXResolution() / 2 +
            12, self.iTable_Y + 24, 24, 24, WidgetTypes.WIDGET_GENERAL, -1, -1)

        self.placeScript()
        self.placeRiverFeature()

    def placeMap(self):
        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        iMapHeight = min(
            (screen.getYResolution() / 2 - 30 - (self.iTable_Y + 48 + 24)), iWidth *
            2 / 3)
        iMapWidth = iMapHeight * 3/2
        screen.addPlotGraphicGFC(
            "PlotView", screen.getXResolution() / 2 - iMapWidth / 2,
            screen.getYResolution() / 2 - 30 - iMapHeight, iMapWidth, iMapHeight,
            pPlot, 350, False, WidgetTypes.WIDGET_GENERAL, -1, -1)

    def placeRiverFeature(self, skip_redraw_steps_before=-1):
        global iSelectedSide
        rt = CvRiverUtil.RiverTypes
        rtk = CvRiverUtil.RiverKeymap

        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        iX = screen.getXResolution() * 0/5 + 10
        iY = self.iTable_Y
        iHeight = (screen.getYResolution()*3/4 - 32 - iY) / 24 * 24 + 2 + 24
        iFeature = pPlot.getFeatureType()
        iVariety = pPlot.getFeatureVariety()
        sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())

        pRiverData = CvRiverUtil.getRiverScriptData(None)
        if iFeature in riverIds["features"]:
            pRiverData = CvRiverUtil.getRiverScriptData(pPlot)
            sText = CyTranslator().getText(rtk[pRiverData.getKey()], ())
            sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())

        #  Step 0. List of Feature Variants
        if skip_redraw_steps_before < 1:
            iData1 = 9000 + int(bFord)
            screen.setLabel(
                "FeatureHeader", "Background", "<font=3b>" + sText + "</font>",
                CvUtil.FONT_CENTER_JUSTIFY, iX + screen.getXResolution() / 10 -
                10, iY - 30, -0.1, FontTypes.GAME_FONT,
                WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverFeature",
                1,
                iX,
                iY,
                iWidth,
                iHeight,
                False,
                False,
                24,
                24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverFeature", 0, "", iWidth)

            screen.appendTableRow("WBRiverFeature")
            screen.setTableText(
                "WBRiverFeature", 0, 0, "<font=3>" + sColor + CyTranslator().
                getText("TXT_KEY_CULTURELEVEL_NONE", ()) + "</font></color>",
                CyArtFileMgr().getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL").
                getPath(), WidgetTypes.WIDGET_PYTHON, iData1, -1,
                CvUtil.FONT_LEFT_JUSTIFY)

            sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
            if iFeature in riverIds["features"] and iVariety == 0:
                sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())
            screen.appendTableRow("WBRiverFeature")
            screen.setTableText(
                "WBRiverFeature",
                0,
                1,
                "<font=3>" +
                sColor +
                CyTranslator().getText(
                    rtk["EMPTY"],
                    ()) +
                "</font></color>",
                getRiverIcon("EMPTY"),
                WidgetTypes.WIDGET_PYTHON,
                iData1,
                1000 + int(bFord),
                CvUtil.FONT_LEFT_JUSTIFY)
            #  for rtype, aligns in rt.iteritems():
            #       for align, versions in aligns.iteritems():
            for (rtype, align) in self.lRiveralign:
                iRow = screen.appendTableRow("WBRiverFeature")
                sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                if rtype == pRiverData.rtype and align == pRiverData.align:
                    sColor = CyTranslator().getText(
                        "[COLOR_POSITIVE_TEXT]",
                        ())

                key = rtype + "_" + align
                screen.setTableText(
                    "WBRiverFeature", 0, iRow, "<font=3>" + sColor +
                    CyTranslator().getText(rtk[key], ()) +
                    "</font></color>",
                    getRiverIcon(key),
                    WidgetTypes.WIDGET_PYTHON, iData1, iRow - 2,
                    CvUtil.FONT_LEFT_JUSTIFY)

        riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
        if len(riverDesc.getVariantSides()) <= iSelectedSide:
            iSelectedSide = 0

        #  Step 1. Place river tile variant selector
        iX += iWidth + 10
        if skip_redraw_steps_before < 2:
            iFeature = pPlot.getFeatureType()
            iVariety = pPlot.getFeatureVariety()
            if not(iFeature in riverIds["features"] and iVariety in riverIds["varieties"]):
                screen.hide("WBRiverVariant")
                screen.hide("WBRiverSubtile")
                screen.hide("WBRiverTexture")
                return
            try:
                lVariants = CvRiverUtil.RiverTypes[
                    riverDesc.rtype][
                    riverDesc.align]
            except:
                return
            iHeightV = (0+len(lVariants))*24 + 2

            sText = CyTranslator().getText("TXT_KEY_RIVER_VARIANT", ())
            screen.setLabel(
                "VariantHeader", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverVariant",
                1,
                iX,
                iY,
                iWidth,
                iHeightV,
                False,
                False,
                24,
                24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverVariant", 0, "", iWidth)

            for variant in lVariants.keys():
                iRow = screen.appendTableRow("WBRiverVariant")
                sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                if variant == riverDesc.variant:
                    sColor = CyTranslator().getText(
                        "[COLOR_POSITIVE_TEXT]",
                        ())
                screen.setTableText(
                    "WBRiverVariant", 0, iRow, "<font=3>" + sColor +
                    "Variant " + str(variant) + "</font></color>",
                    None,
                    WidgetTypes.WIDGET_PYTHON, 9010, variant,
                    CvUtil.FONT_LEFT_JUSTIFY)

            screen.show("WBRiverVariant")

        #  Step 2. Place river tile subtile selector
        iY += iHeight/2 + 10
        lSides = riverDesc.getVariantSides()
        iHeight = (0+len(lSides))*24 + 2
        iY -= iHeight
        if skip_redraw_steps_before < 3:

            sText = CyTranslator().getText("TXT_KEY_RIVER_SUBTILE", ())
            screen.setLabel(
                "SubtileHeader", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverSubtile",
                1,
                iX,
                iY,
                iWidth,
                iHeight,
                False,
                False,
                24,
                24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader(
                "WBRiverSubtile",
                0,
                CyTranslator().getText(
                    "TXT_KEY_RIVER_SUBTILE",
                    ()),
                iWidth)

            for side in lSides:
                iRow = screen.appendTableRow("WBRiverSubtile")
                sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                if iRow == iSelectedSide:
                    sColor = CyTranslator().getText(
                        "[COLOR_POSITIVE_TEXT]",
                        ())
                screen.setTableText(
                    "WBRiverSubtile", 0, iRow, "<font=3>" + sColor +
                    "Subtile " + str(iRow) + "</font></color>",
                    None,
                    WidgetTypes.WIDGET_PYTHON, 9020, iRow,
                    CvUtil.FONT_LEFT_JUSTIFY)

            screen.show("WBRiverSubtile")

        #  Step 3. Place list of available textures for selected subtile
        iY += iHeight + 40
        if skip_redraw_steps_before < 4:
            side = riverDesc.getVariantSides()[iSelectedSide]
            lTextures = CvRiverUtil.RiverTextureGroups[side[1]]
            iSelectedTexture = riverDesc.textures[iSelectedSide]
            iHeight = (0+len(lTextures))*24 + 2

            sText = CyTranslator().getText("TXT_KEY_RIVER_TEXTURE", ())
            screen.setLabel(
                "TextureHeader", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverTexture",
                1,
                iX,
                iY,
                iWidth,
                iHeight,
                False,
                False,
                24,
                24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverTexture", 0, "", iWidth)

            for tex in lTextures:
                iRow = screen.appendTableRow("WBRiverTexture")
                sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                if iRow == iSelectedTexture:
                    sColor = CyTranslator().getText(
                        "[COLOR_POSITIVE_TEXT]",
                        ())
                screen.setTableText(
                    "WBRiverTexture",
                    0,
                    iRow,
                    "<font=3>" +
                    sColor +
                    CyTranslator().getText(
                        CvRiverUtil.RiverTextureKeymap[iRow],
                        ()) +
                    "</font></color>",
                    None,
                    WidgetTypes.WIDGET_PYTHON,
                    9030,
                    iRow,
                    CvUtil.FONT_LEFT_JUSTIFY)

            screen.show("WBRiverTexture")

        iX = screen.getXResolution() * 4/5 + 10
        iY = self.iTable_Y
        # Step 4:  List rapids selection if available
        rapid_key = riverDesc.getKey() + str(riverDesc.variant)
        iRapid = 1
        if rapid_key in CvRiverUtil.RapidTypes:
            iRapid += len(CvRiverUtil.RapidTypes[rapid_key][0])
        iHeight = (iRapid)*24 + 2

        if skip_redraw_steps_before < 5:
            screen.hide("WBRiverRapids")
            iSelectedRapid = riverDesc.rapids
            sText = CyTranslator().getText("TXT_KEY_RIVER_RAPIDS", ())
            screen.setLabel(
                "RapidsHeader", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC("WBRiverRapids",
                                      1, iX, iY,
                                      iWidth, iHeight,
                                      False, False,
                                      24, 24,
                                      TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverRapids", 0, "", iWidth)

            # Add entry for invisible rapids
            iRow = screen.appendTableRow("WBRiverRapids")
            sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
            if iRow == iSelectedRapid:
                sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())

            screen.setTableText(
                "WBRiverRapids",
                0,
                0,
                "<font=3>" +
                sColor +
                CyTranslator().getText(
                    "TXT_KEY_CULTURELEVEL_NONE",
                    ()) +
                "</font></color>",
                CyArtFileMgr(). getInterfaceArtInfo("INTERFACE_BUTTONS_CANCEL"). getPath(),
                WidgetTypes.WIDGET_PYTHON,
                9050,
                0,
                CvUtil.FONT_LEFT_JUSTIFY)
            if iRapid > 1:
                for r in CvRiverUtil.RapidTypes[rapid_key][0]:
                    iRow = screen.appendTableRow("WBRiverRapids")
                    sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                    if iRow == iSelectedRapid:
                        sColor = CyTranslator().getText(
                            "[COLOR_POSITIVE_TEXT]",
                            ())

                    if iRow < 4:
                        sText = CyTranslator().getText(
                            "TXT_KEY_RIVER_DIRECTION", (iRow,))
                    else:
                        # Plots with river branching has 6 variants. Last three
                        # inverts the directions
                        sText = CyTranslator().getText(
                            "TXT_KEY_RIVER_DIRECTION_REVERSE", (iRow-3,))
                    screen.setTableText(
                        "WBRiverRapids", 0, iRow,
                        "<font=3>" + sColor + sText + "</font></color>",
                        None,
                        WidgetTypes.WIDGET_PYTHON,
                        9050, iRow,
                        CvUtil.FONT_LEFT_JUSTIFY)

            screen.show("WBRiverRapids")

        iY += iHeight + 40
        # Step 5:  List water colors and orientations
        screen.hide("WBRiverWaterColors")
        screen.hide("WBRiverWaterRotations")
        if rapid_key in CvRiverUtil.RapidTypes:
            iLen = len(CvRiverUtil.WaterTypes)
            iHeight = (iLen)*24 + 2

            sText = CyTranslator().getText("TXT_KEY_RIVER_WATER_COLOR", ())
            screen.setLabel(
                "WaterColors", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverWaterColors",
                1, iX, iY,
                iWidth, iHeight,
                False, False,
                24, 24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverWaterColors", 0, "", iWidth)

            iWaterSelectedRow = 0
            iPlus = 0
            selectedWaterColor = ""
            if riverDesc.waterColor > 0:
                iWaterSelectedRow = (riverDesc.waterColor+1)/2
            if riverDesc.waterRotation > 0:
                iPlus = 1
            for waterColor in CvRiverUtil.WaterTypes:
                iRow = screen.appendTableRow("WBRiverWaterColors")
                sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                sWaterColor = CyTranslator().getText(waterColor[0], ())
                if iRow == iWaterSelectedRow:
                    selectedWaterColor = CyTranslator().getText(waterColor[0], ()).lower()
                    sColor = CyTranslator().getText(
                        "[COLOR_POSITIVE_TEXT]",
                        ())

                screen.setTableText(
                    "WBRiverWaterColors", 0, iRow,
                    "<font=3>" + sColor +
                    sWaterColor +
                    "</font></color>",
                    None,
                    WidgetTypes.WIDGET_PYTHON,
                    9060, 2*iRow+iPlus+1,
                    CvUtil.FONT_LEFT_JUSTIFY)

            screen.show("WBRiverWaterColors")

            iY += iHeight + 40

            rotations = CvRiverUtil.RapidTypes[rapid_key][1]
            if -1 in rotations:
                rotations = [0, 1, 2, 3, 4]
            iLen = len(rotations)
            iHeight = (iLen)*24 + 2
            rotationNames = []
            if 0 in rotations:
                rotationNames.append("TXT_KEY_RIVER_WATER_FULL")
            if 1 in rotations:
                rotationNames.append("TXT_KEY_RIVER_WATER_NORTH")
            if 2 in rotations:
                rotationNames.append("TXT_KEY_RIVER_WATER_WEST")
            if 3 in rotations:
                rotationNames.append("TXT_KEY_RIVER_WATER_SOUTH")
            if 4 in rotations:
                rotationNames.append("TXT_KEY_RIVER_WATER_EAST")

            sText = CyTranslator().getText("TXT_KEY_RIVER_WATER_BLENDING", ())
            screen.setLabel(
                "WaterRotations", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverWaterRotations",
                1, iX, iY,
                iWidth, iHeight,
                False, False,
                24, 24,
                TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverWaterRotations", 0, "", iWidth)

            if iWaterSelectedRow == 0:
                screen.hide("WBRiverWaterRotations")
                screen.hide("WaterRotations")
            else:
                for rotationName in rotationNames:
                    iRow = screen.appendTableRow("WBRiverWaterRotations")
                    sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                    if rotations[iRow] == riverDesc.waterRotation:
                        sColor = CyTranslator().getText(
                            "[COLOR_POSITIVE_TEXT]",
                            ())

                    screen.setTableText(
                        "WBRiverWaterRotations", 0, iRow,
                        "<font=3>" + sColor +
                        CyTranslator().getText(rotationName, (selectedWaterColor,)) +
                        "</font></color>",
                        None,
                        WidgetTypes.WIDGET_PYTHON,
                        9070, rotations[iRow],
                        CvUtil.FONT_LEFT_JUSTIFY)

                screen.show("WaterRotations")
                screen.show("WBRiverWaterRotations")

    def placeScript(self):
        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        global iScript_Y
        iScript_Y = screen.getYResolution() - 120
        sText = CyTranslator().getText(
            "[COLOR_SELECTED_TEXT]",
            ()) + "<font=3b>" + CyTranslator().getText(
            "TXT_KEY_WB_SCRIPT_DATA",
            ()) + "</color></font>"
        screen.setText("PlotEditScriptData", "Background", sText,
                       CvUtil.FONT_CENTER_JUSTIFY, screen.getXResolution() / 2,
                       iScript_Y, -0.1, FontTypes.TITLE_FONT,
                       WidgetTypes.WIDGET_GENERAL, -1, -1)
        screen.addPanel(
            "ScriptPanel", "", "",
            False, False,
            screen.getXResolution() / 2 - iWidth / 2,
            iScript_Y + 25,
            iWidth,
            screen.getYResolution() - iScript_Y - 70,
            PanelStyles.PANEL_STYLE_IN)
        screen.addMultilineText(
            "GameScriptDataText", pPlot.getScriptData(),
            screen.getXResolution() / 2 - iWidth / 2, iScript_Y + 25, iWidth,
            screen.getYResolution() - iScript_Y - 70, WidgetTypes.WIDGET_GENERAL,
            -1, -1, CvUtil.FONT_LEFT_JUSTIFY)

        self.placeRiverDecoration()

    def placeRiverDecoration(self):
        global iSelectedSide
        rtk = CvRiverUtil.RiverKeymap

        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        iX = screen.getXResolution() * 3/5 + 10
        iY = self.iTable_Y
        iHeight = (screen.getYResolution()*2/3 - 32 - iY) / 24 * 24 + 2
        iFeature = pPlot.getFeatureType()
        iVariety = pPlot.getFeatureVariety()
        sText = CyTranslator().getText("TXT_KEY_CULTURELEVEL_NONE", ())
        sColor = CyTranslator().getText("[COLOR_POSITIVE_TEXT]", ())

        screen.hide("WBRiverDecoration")

        if iFeature not in riverIds["features"] or iVariety not in riverIds["varieties"]:
            return

        pRiverData = CvRiverUtil.getRiverScriptData(pPlot)
        sText = CyTranslator().getText(rtk["DECORATION"], ())
        sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())

        if True:
            iData1 = 9040
            screen.setLabel(
                "DecorationHeader", "Background", "<font=3b>" + sText +
                "</font>", CvUtil.FONT_CENTER_JUSTIFY, iX +
                screen.getXResolution() / 10 - 10, iY - 30, -0.1,
                FontTypes.GAME_FONT, WidgetTypes.WIDGET_GENERAL, -1, -1)
            screen.addTableControlGFC(
                "WBRiverDecoration",
                1,
                iX,
                iY,
                iWidth,
                iHeight,
                False, False, 24, 24, TableStyles.TABLE_STYLE_STANDARD)
            screen.setTableColumnHeader("WBRiverDecoration", 0, "", iWidth)

            for dtype, aligns in CvRiverUtil.DecoTypes.iteritems():
                for align in aligns:
                    iRow = screen.appendTableRow("WBRiverDecoration")
                    sColor = CyTranslator().getText("[COLOR_WARNING_TEXT]", ())
                    if iRow in pRiverData.decorations:
                        sColor = CyTranslator().getText(
                            "[COLOR_POSITIVE_TEXT]",
                            ())

                    screen.setTableText(
                        "WBRiverDecoration", 0, iRow, "<font=3>" + sColor +
                        CyTranslator().getText(rtk[dtype], ()) + " " + align +
                        "</font></color>",
                        gc.getFeatureInfo(riverIds["features"][0]).getButton(),
                        WidgetTypes.WIDGET_PYTHON, iData1, iRow,
                        CvUtil.FONT_LEFT_JUSTIFY)

    def handleInput(self, inputClass):
        screen = CyGInterfaceScreen(
            "WBRiverScreen",
            CvScreenEnums.WB_PLOT_RIVER)
        global bAdd
        global bSensibility
        global bFord
        global iSelectedSide
        global iEditType
        global bRiverAutomatic
        global bRiverBranch
        global bRiverComplete

        if False:
            pass
        elif inputClass.getFunctionName() == "CurrentPage":
            iIndex = screen.getPullDownData(
                "CurrentPage",
                screen.getSelectedPullDownID("CurrentPage"))
            if iIndex == 1:
                WBEventScreen.WBEventScreen().interfaceScreen(pPlot)
            elif iIndex == 2:
                if pPlot.getOwner() != -1:
                    WBPlayerScreen.WBPlayerScreen().interfaceScreen(pPlot.getOwner())
            elif iIndex == 3:
                WBTeamScreen.WBTeamScreen().interfaceScreen(pPlot.getTeam())
            elif iIndex == 4:
                if pPlot.isCity():
                    WBCityEditScreen.WBCityEditScreen().interfaceScreen(
                        pPlot.getPlotCity())
            elif iIndex == 5:
                pUnit = pPlot.getUnit(0)
                if pUnit:
                    WBUnitScreen.WBUnitScreen(
                        CvPlatyBuilderScreen.CvWorldBuilderScreen()).interfaceScreen(pUnit)
            elif iIndex == 11:
                iPlayer = pPlot.getOwner()
                if iPlayer == -1:
                    iPlayer = CyGame().getActivePlayer()
                WBInfoScreen.WBInfoScreen().interfaceScreen(iPlayer)
            elif iIndex == 12:
                WBPlotScreen.WBPlotScreen().interfaceScreen(pPlot)

        elif inputClass.getFunctionName() == "NextPlotUpButton":
            pNewPlot = CyMap().plot(pPlot.getX(), pPlot.getY() + 1)
            if not pNewPlot.isNone():
                self.interfaceScreen(pNewPlot)
        elif inputClass.getFunctionName() == "NextPlotDownButton":
            pNewPlot = CyMap().plot(pPlot.getX(), pPlot.getY() - 1)
            if not pNewPlot.isNone():
                self.interfaceScreen(pNewPlot)
        elif inputClass.getFunctionName() == "NextPlotLeftButton":
            pNewPlot = CyMap().plot(pPlot.getX() - 1, pPlot.getY())
            if not pNewPlot.isNone():
                self.interfaceScreen(pNewPlot)
        elif inputClass.getFunctionName() == "NextPlotRightButton":
            pNewPlot = CyMap().plot(pPlot.getX() + 1, pPlot.getY())
            if not pNewPlot.isNone():
                self.interfaceScreen(pNewPlot)

        elif inputClass.getFunctionName() == "WBRiverFeature":
            iFeature = pPlot.getFeatureType()
            iVariety = pPlot.getFeatureVariety()

            bSkip = False
            if inputClass.getData2() < 0 or not bAdd:
                pPlot.setFeatureType(-1, 0)
                CvUtil.removeScriptData(pPlot, "r")
                bSkip = True

            if bSensibility and pPlot.getPlotType() is not PlotTypes.PLOT_OCEAN:
                bSkip = True

            if not bSkip:
                if inputClass.getData2() >= 1000:
                    if iFeature in riverIds["features"]:
                        CvUtil.removeScriptData(pPlot, "r")
                    pPlot.setTerrainType(
                        riverIds["terrains"][
                            inputClass.getData2() -
                            1000],
                        True,
                        True)
                    pPlot.setFeatureType(-1, 0)
                    pPlot.setFeatureType(
                        riverIds["features"][
                            inputClass.getData2() -
                            1000],
                        0)
                else:
                    ra = self.lRiveralign[inputClass.getData2()]
                    riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
                    riverDesc.rtype = ra[0]
                    riverDesc.align = ra[1]
                    if riverDesc.variant not in CvRiverUtil.RiverTypes[riverDesc.rtype][
                            riverDesc.align]:
                        riverDesc.variant = 1
                    if not len(riverDesc.getVariantSides()) > iSelectedSide:
                        iSelectedSide = 0
                    if iFeature not in riverIds["features"] or iVariety == 0:
                        CvRiverUtil.addRiverFeature(pPlot)
                    CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)

            self.placeScript()
            self.placeRiverFeature()

        elif inputClass.getFunctionName() == "WBRiverVariant":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            iOld = riverDesc.variant
            iNew = inputClass.getData2()
            if iNew is not iOld:
                riverDesc.variant = iNew
                if iSelectedSide >= len(riverDesc.getVariantSides()):
                    iSelectedSide = 0
                CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
                self.placeRiverFeature(0)

        elif inputClass.getFunctionName() == "WBRiverSubtile":
            iNew = inputClass.getData2()
            if iNew is not iSelectedSide:
                iSelectedSide = iNew
                self.placeRiverFeature(1)

        elif inputClass.getFunctionName() == "WBRiverTexture":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            iOld = riverDesc.textures[iSelectedSide]
            iNew = inputClass.getData2()
            if iNew is not iOld:
                riverDesc.textures[iSelectedSide] = iNew
                CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
                self.placeRiverFeature(2)
            if bRiverComplete or bRiverBranch:
                nearbyPlots = CvRiverUtil.getAdjacentTiles(
                    pPlot, not bRiverComplete)
                # Remove this plot (=first entry)
                nearbyPlots.pop(0)
                CvRiverUtil.setTexture(nearbyPlots, iSelectedSide, iNew)


        elif inputClass.getFunctionName() == "WBRiverDecoration":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            bActive = not (inputClass.getData2() in riverDesc.decorations)
            if bActive:
                riverDesc.decorations.append(inputClass.getData2())
            else:
                riverDesc.decorations.remove(inputClass.getData2())
            CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
            self.placeRiverDecoration()

        elif inputClass.getFunctionName() == "WBRiverRapids":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            riverDesc.rapids = inputClass.getData2()
            CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
            if bRiverComplete or bRiverBranch:
                nearbyPlots = CvRiverUtil.getAdjacentTiles(
                    pPlot, not bRiverComplete)
                """
                dmsg = ""
                for n in nearbyPlots:
                    dmsg += "(%i,%i)\n" % (n[0].getX(), n[0].getY())

                CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5,
                             dmsg, None, 2, None, ColorTypes(14), 0, 0,
                             False, False)
                """
                CvRiverUtil.setRapidDirection(nearbyPlots)

            self.placeRiverFeature(4)
            self.placeScript()
        elif inputClass.getFunctionName() == "WBRiverWaterColors":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            # order is [ full texture color 1, halve texture color 1, ... ]
            riverDesc.waterColor = max(0, inputClass.getData2() - 2)
            # Use halve texture if rotation is set
            CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
            if bRiverComplete or bRiverBranch:
                nearbyPlots = CvRiverUtil.getAdjacentTiles(
                    pPlot, not bRiverComplete)
                CvRiverUtil.setWaterColor(nearbyPlots)

            self.placeRiverFeature(5)
            self.placeScript()
        elif inputClass.getFunctionName() == "WBRiverWaterRotations":
            riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
            riverDesc.waterRotation = inputClass.getData2()
            if riverDesc.waterColor > 0:
                iPlus = 0
                if riverDesc.waterRotation > 0:
                    iPlus = 1
                riverDesc.waterColor = 2 * \
                    ((riverDesc.waterColor+1)/2) - 1 + iPlus

            CvRiverUtil.updateRiverFeature(pPlot, riverDesc, True)
            self.placeRiverFeature(5)
            self.placeScript()

        elif inputClass.getFunctionName() == "PlotEditScriptData":
            popup = Popup.PyPopup(5555, EventContextTypes.EVENTCONTEXT_ALL)
            popup.setHeaderString(
                CyTranslator().getText(
                    "TXT_KEY_WB_SCRIPT",
                    ()))
            popup.setUserData((pPlot.getX(), pPlot.getY()))
            popup.createEditBox(pPlot.getScriptData())
            popup.launch()

        elif inputClass.getFunctionName() == "SensibilityCheck":
            bSensibility = not bSensibility
            screen.setState("SensibilityCheck", bSensibility)

        elif inputClass.getFunctionName() == "FordCheck":
            bFord = not bFord
            iTerrain = pPlot.getTerrainType()
            iFeature = pPlot.getFeatureType()
            iVariety = pPlot.getFeatureVariety()
            if(iTerrain in riverIds["terrains"]
               and iTerrain is not riverIds["terrains"][int(bFord)]):
                pPlot.setTerrainType(
                    riverIds["terrains"][int(bFord)],
                    True, True)
            if(iFeature in riverIds["features"] and iVariety in riverIds["varieties"]
                    and iFeature is not riverIds["features"][int(bFord)]):
                pPlot.setFeatureType(-1, 0)
                pPlot.setFeatureType(
                    riverIds["features"][int(bFord)],
                    iVariety)

                riverDesc = CvRiverUtil.getRiverScriptData(pPlot)
                if not iVariety == 0:
                    CvRiverUtil.updateRiverFeature(pPlot, riverDesc, False)
            screen.setState("FordCheck", bFord)
            self.placeRiverFeature()

        elif inputClass.getFunctionName() == "RiverAutomaticCheck":
            bRiverAutomatic = not bRiverAutomatic
            screen.setState("RiverAutomaticCheck", bRiverAutomatic)

        elif inputClass.getFunctionName() == "RiverBranchCheck":
            bRiverBranch = not bRiverBranch
            screen.setState("RiverBranchCheck", bRiverBranch)

        elif inputClass.getFunctionName() == "RiverCompleteCheck":
            bRiverComplete = not bRiverComplete
            screen.setState("RiverCompleteCheck", bRiverComplete)

        return 1

    def update(self, fDelta):
        self.placeMap()
        global iCounter
        if iCounter > 0:
            iCounter -= 1
        elif iCounter == 0:
            iCounter = -1
        return 1
