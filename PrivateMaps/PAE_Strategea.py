#
#        FILE:         Strategea.py
#        AUTHOR:  Zerzes (Based on Boreal.py by Bob Thomas (Sirian))
#        PURPOSE: Strategic map with natural defense bottlenecks and encouraged resource trading
#-----------------------------------------------------------------------------

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import random
import sys
from math import sqrt
from CvMapGeneratorUtil import FractalWorld
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

def getDescription():
        return "TXT_KEY_MAP_SCRIPT_BOREAL_DESCR"

def isAdvancedMap():
        "This map should show up in simple mode"
        return 0

def isClimateMap():
        return 1

def isSeaLevelMap():
        return 0

def getNumCustomMapOptions():
        return 1

def getNumHiddenCustomMapOptions():
        return 1

def getCustomMapOptionName(argsList):
        translated_text = unicode(CyTranslator().getText("TXT_KEY_MAP_WORLD_WRAP", ()))
        return translated_text

def getNumCustomMapOptionValues(argsList):
        return 3

def getCustomMapOptionDescAt(argsList):
        iSelection = argsList[1]
        selection_names = ["TXT_KEY_MAP_WRAP_FLAT",
                           "TXT_KEY_MAP_WRAP_CYLINDER",
                           "TXT_KEY_MAP_WRAP_TOROID"]
        translated_text = unicode(CyTranslator().getText(selection_names[iSelection], ()))
        return translated_text

def getCustomMapOptionDefault(argsList):
        return 0

def isRandomCustomMapOption(argsList):
        return false

def getWrapX():
        map = CyMap()
        return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)

def getWrapY():
        map = CyMap()
        return (map.getCustomMapOption(0) == 2)

def getTopLatitude():
        return 95

def getBottomLatitude():
        return 5

def getGridSize(argsList):
        "Because this is such a land-heavy map, override getGridSize() to make the map smaller"
        grid_sizes = {
                WorldSizeTypes.WORLDSIZE_DUEL:                (7,5),
                WorldSizeTypes.WORLDSIZE_TINY:                (9,6),
                WorldSizeTypes.WORLDSIZE_SMALL:                (12,8),
                WorldSizeTypes.WORLDSIZE_STANDARD:        (15,10),
                WorldSizeTypes.WORLDSIZE_LARGE:                (18,12),
                WorldSizeTypes.WORLDSIZE_HUGE:                (22,15)
        }

        if (argsList[0] == -1): # (-1,) is passed to function on loads
                return []
        [eWorldSize] = argsList
        return grid_sizes[eWorldSize]

def minStartingDistanceModifier():
        return -27

def beforeGeneration():
        gc = CyGlobalContext()
        map = CyMap()
        dice = gc.getGame().getMapRand()
        iW = map.getGridWidth()
        iH = map.getGridHeight()

# Subclass
class BorealFractalWorld(CvMapGeneratorUtil.FractalWorld):
        def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=3):
                # Check for changes to User Input variances.
                print "Generate plot types"
                self.checkForOverrideDefaultUserInputVariances()

                self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, 2, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, 5, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                self.hillsFrac2 = CyFractal()
                self.hillsFrac2.fracInit(self.iNumPlotsX, self.iNumPlotsY, 2, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                print "Init fractals"
                water_percent += self.seaLevelChange
                water_percent = min(water_percent, self.seaLevelMax)
                water_percent = max(water_percent, self.seaLevelMin)

                iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
                iHillsBottom = self.peaksFrac.getHeightFromPercent(85)
                iPeakThreshold = self.peaksFrac.getHeightFromPercent(96)

                hill1 = self.hillsFrac.getHeightFromPercent(59)
                hill2 = self.hillsFrac.getHeightFromPercent(81)
                peak1 = self.hillsFrac.getHeightFromPercent(65)
                peak2 = self.hillsFrac.getHeightFromPercent(75)
                hill3 = self.hillsFrac2.getHeightFromPercent(12)
                hill4 = self.hillsFrac2.getHeightFromPercent(28)
                peak3 = self.hillsFrac2.getHeightFromPercent(15)
                peak4 = self.hillsFrac2.getHeightFromPercent(25)
                peak5 = self.hillsFrac2.getHeightFromPercent(80)
                peak6 = self.hillsFrac2.getHeightFromPercent(80)
                peak7 = self.hillsFrac.getHeightFromPercent(20)
                peak8 = self.hillsFrac.getHeightFromPercent(20)
                # hill1 = self.hillsFrac.getHeightFromPercent(10)
                # hill2 = self.hillsFrac.getHeightFromPercent(10)
                # peak1 = self.hillsFrac.getHeightFromPercent(10)
                # peak2 = self.hillsFrac.getHeightFromPercent(10)
                # hill3 = self.hillsFrac2.getHeightFromPercent(10)
                # hill4 = self.hillsFrac2.getHeightFromPercent(10)
                # peak3 = self.hillsFrac2.getHeightFromPercent(10)
                # peak4 = self.hillsFrac2.getHeightFromPercent(10)
                # peak5 = self.hillsFrac2.getHeightFromPercent(10)
                # peak6 = self.hillsFrac2.getHeightFromPercent(10)
                # peak7 = self.hillsFrac.getHeightFromPercent(10)
                # peak8 = self.hillsFrac.getHeightFromPercent(10)

                # Rocky special
                if self.map.getClimate() == 3:
                        print "Rocky world"
                        peak5 = self.hillsFrac2.getHeightFromPercent(74)
                        peak6 = self.hillsFrac2.getHeightFromPercent(84)
                        peak7 = self.hillsFrac.getHeightFromPercent(16)
                        peak8 = self.hillsFrac.getHeightFromPercent(26)

                for x in range(self.iNumPlotsX):
                        for y in range(self.iNumPlotsY):
                                i = y*self.iNumPlotsX + x
                                val = self.continentsFrac.getHeight(x,y)
                                if val <= iWaterThreshold:
                                        self.plotTypes[i] = PlotTypes.PLOT_OCEAN
                                else:
                                        hillVal = self.hillsFrac.getHeight(x,y)
                                        hillVal2 = self.hillsFrac2.getHeight(x,y)
                                        peakVal = self.peaksFrac.getHeight(x,y)
                                        # Set primary mountain ridges
                                        if hillVal >= hill1 and hillVal <= hill2:
                                                if (hillVal >= peak1 and hillVal <= peak2):
                                                        self.plotTypes[i] = PlotTypes.PLOT_PEAK
                                                else:
                                                        self.plotTypes[i] = PlotTypes.PLOT_HILLS
                                        elif hillVal >= peak7 and hillVal <= peak8:
                                                self.plotTypes[i] = PlotTypes.PLOT_PEAK
                                        elif peakVal >= iHillsBottom:
                                                if peakVal >= iPeakThreshold:
                                                        self.plotTypes[i] = PlotTypes.PLOT_PEAK
                                                else:
                                                        self.plotTypes[i] = PlotTypes.PLOT_HILLS
                                        else:
                                                self.plotTypes[i] = PlotTypes.PLOT_LAND
                                        # Set secondary mountain ridges
                                        if hillVal2 >= hill3 and hillVal2 <= hill4:
                                                if (hillVal2 >= peak3 and hillVal2 <= peak4):
                                                        self.plotTypes[i] = PlotTypes.PLOT_PEAK
                                                else:
                                                        self.plotTypes[i] = PlotTypes.PLOT_HILLS
                                        elif hillVal2 >= peak5 and hillVal2 <= peak6:
                                                self.plotTypes[i] = PlotTypes.PLOT_PEAK

                if shift_plot_types:
                        self.shiftPlotTypes()

                print "Plot types generated"
                return self.plotTypes

def generatePlotTypes():
        NiTextOut("Setting Plot Types (Python Boreal) ...")
        global fractal_world
        fractal_world = BorealFractalWorld()
        fractal_world.initFractal(continent_grain=3, rift_grain = -1, has_center_rift = False, polar = False)
        water_percent = 21
        if CyMap().getClimate() == 2:
                water_percent = 8
        plot_types = fractal_world.generatePlotTypes(water_percent)
        return plot_types

# subclass TerrainGenerator to redefine everything. This is a regional map.
class BorealTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
        def __init__(self, fracXExp=-1, fracYExp=-1):
                self.gc = CyGlobalContext()
                self.map = CyMap()

                self.iWidth = self.map.getGridWidth()
                self.iHeight = self.map.getGridHeight()

                self.mapRand = self.gc.getGame().getMapRand()

                self.iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.

                self.heat=CyFractal()

                self.fracXExp = fracXExp
                self.fracYExp = fracYExp

                self.initFractals()

        def initFractals(self):
                self.heat.fracInit(self.iWidth, self.iHeight, 2, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

                # Normal
                self.iDesert = self.heat.getHeightFromPercent(80)
                self.iPlains = self.heat.getHeightFromPercent(48)
                self.iGrass = self.heat.getHeightFromPercent(20)
                self.iTundra = self.heat.getHeightFromPercent(8)

                # Jungle
                if (self.map.getClimate() == 1):
                        self.iDesert = self.heat.getHeightFromPercent(85)
                        self.iPlains = self.heat.getHeightFromPercent(85)
                        self.iGrass = self.heat.getHeightFromPercent(0)
                        self.iTundra = self.heat.getHeightFromPercent(0)

                # Desert
                if (self.map.getClimate() == 2):
                        self.heat.fracInit(self.iWidth, self.iHeight, 3, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                        self.iDesert = self.heat.getHeightFromPercent(15)
                        self.iPlains = self.heat.getHeightFromPercent(0)
                        self.iGrass = self.heat.getHeightFromPercent(0)
                        self.iTundra = self.heat.getHeightFromPercent(0)

                # Cold
                if (self.map.getClimate() == 4):
                        self.heat.fracInit(self.iWidth, self.iHeight, 4, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                        self.iDesert = self.heat.getHeightFromPercent(110)
                        self.iPlains = self.heat.getHeightFromPercent(110)
                        self.iGrass = self.heat.getHeightFromPercent(92)
                        self.iTundra = self.heat.getHeightFromPercent(35)

                self.terrainDesert = self.gc.getInfoTypeForString("TERRAIN_DESERT")
                self.terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
                self.terrainPlains = self.gc.getInfoTypeForString("TERRAIN_PLAINS")
                self.terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
                self.terrainIce = self.gc.getInfoTypeForString("TERRAIN_SNOW")

        def generateTerrainAtPlot(self,iX,iY):
#                terrainVal = self.terrainPlains
#                return terrainVal
                pPlot = self.map.plot(iX, iY)
                if (pPlot.isWater()):
                        return pPlot.getTerrainType()

                heatVal = self.heat.getHeight(iX, iY)
                # if (self.map.getClimate() == 2):
                        # terrainVal = self.terrainDesert
                if heatVal >= self.iDesert:
                        terrainVal = self.terrainDesert
                elif heatVal >= self.iPlains:
                        terrainVal = self.terrainPlains
                elif heatVal >= self.iGrass:
                        terrainVal = self.terrainGrass
                elif heatVal >= self.iTundra:
                        terrainVal = self.terrainTundra
                else:
                        terrainVal = self.terrainIce

                # Desert special
                if (self.map.getClimate() == 2):
                        if (self.map.findWater(pPlot, 1, false)):
                                plainsLimit = self.heat.getHeightFromPercent(50)
                                grassLimit = self.heat.getHeightFromPercent(25)
                                if heatVal < grassLimit:
                                        terrainVal = self.terrainGrass
                                elif heatVal < plainsLimit:
                                        terrainVal = self.terrainPlains

                if (terrainVal == TerrainTypes.NO_TERRAIN):
                        return self.map.plot(iX, iY).getTerrainType()

                return terrainVal

def generateTerrainTypes():
        NiTextOut("Generating Terrain (Python Boreal) ...")
        terraingen = BorealTerrainGenerator()
        terrainTypes = terraingen.generateTerrain()
        return terrainTypes

class BorealFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
        def __init__(self, forest_grain=5, fracXExp=-1, fracYExp=-1):
                self.gc = CyGlobalContext()
                self.map = CyMap()
                self.mapRand = self.gc.getGame().getMapRand()
                self.forests = CyFractal()
                self.oasis = CyFractal()

                self.iFlags = 0

                self.iGridW = self.map.getGridWidth()
                self.iGridH = self.map.getGridHeight()

                self.forest_grain = 3 # forest_grain + self.gc.getWorldInfo(self.map.getWorldSize()).getFeatureGrainChange()

                self.fracXExp = fracXExp
                self.fracYExp = fracYExp

                self.__initFractals()
                self.__initFeatureTypes()

        def __initFractals(self):
                self.forests.fracInit(self.iGridW, self.iGridH, self.forest_grain, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
                self.oasis.fracInit(self.iGridW, self.iGridH, 8, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

                # Normal
                self.iForestLevel = self.forests.getHeightFromPercent(80)
                self.iForestLevelPlains = self.forests.getHeightFromPercent(30)
                self.iJungleLevel = self.forests.getHeightFromPercent(60)
                self.iOasisLevel = self.oasis.getHeightFromPercent(25)

                # Jungle
                if (self.map.getClimate() == 1):
                        self.iForestLevel = self.forests.getHeightFromPercent(80)
                        self.iForestLevelPlains = self.forests.getHeightFromPercent(0)
                        self.iJungleLevel = self.forests.getHeightFromPercent(100)
                        self.iOasisLevel = self.oasis.getHeightFromPercent(40)

                # Desert
                # Jungle are made from grass plots instead of desert plots
                if (self.map.getClimate() == 2):
                        self.iForestLevel = self.forests.getHeightFromPercent(100)
                        self.iForestLevelPlains = self.forests.getHeightFromPercent(0)
                        self.iJungleLevel = self.forests.getHeightFromPercent(100)
                        self.iOasisLevel = self.oasis.getHeightFromPercent(40)

                # Cold
                if (self.map.getClimate() == 4):
                        self.iForestLevel = self.forests.getHeightFromPercent(90)
                        self.iForestLevelPlains = self.forests.getHeightFromPercent(0)
                        self.iJungleLevel = self.forests.getHeightFromPercent(0)
                        self.iOasisLevel = self.oasis.getHeightFromPercent(0)

        def __initFeatureTypes(self):
                self.featureForest = self.gc.getInfoTypeForString("FEATURE_FOREST")
                self.featureJungle = self.gc.getInfoTypeForString("FEATURE_JUNGLE")
                self.featureOasis = self.gc.getInfoTypeForString("FEATURE_OASIS")
                self.featureFlood = self.gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
                # PAE
                self.featureSavanna = self.gc.getInfoTypeForString("FEATURE_SAVANNA")
                self.featureDenseForest = self.gc.getInfoTypeForString("FEATURE_DICHTERWALD")

        def addFeaturesAtPlot(self, iX, iY):
                pPlot = self.map.sPlot(iX, iY)
                dice = self.gc.getGame().getMapRand()
                if pPlot.isPeak() or pPlot.isWater(): pass

                else:
                        diceSize = 30
                        diceRoll = dice.get(2 * diceSize, "Dice roll - CA test PYTHON")
                        # Make cold river tiles more fertile
                        if pPlot.isRiver():
                                if pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_SNOW"):
                                        print('Changing River Ice Plot to Tundra')
                                        terrainTundra = self.gc.getInfoTypeForString("TERRAIN_TUNDRA")
                                        pPlot.setTerrainType(terrainTundra, true, true)
                                elif pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_TUNDRA"):
                                        print('Changing River Tundra Plot to Grass')
                                        newTerrain = self.gc.getInfoTypeForString("TERRAIN_GRASS")
                                        pPlot.setTerrainType(newTerrain, true, true)

                        # Add forests and jungles
                        if pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_DESERT"):
                                if self.forests.getHeight(iX, iY) >= self.iJungleLevel - diceSize + diceRoll and dice.get(100, "Dice Roll") > 8:
                                        terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
                                        pPlot.setTerrainType(terrainGrass, true, true)
                                        pPlot.setFeatureType(self.featureJungle, 1)
                        elif pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_PLAINS"):
                                if self.forests.getHeight(iX, iY) >= self.iJungleLevel - diceSize + diceRoll and dice.get(100, "Dice Roll") > 8:
                                        if self.forests.getHeight(iX, iY) > self.iForestLevel - diceSize + diceRoll:
                                                terrainGrass = self.gc.getInfoTypeForString("TERRAIN_GRASS")
                                                pPlot.setTerrainType(terrainGrass, true, true)
                                                pPlot.setFeatureType(self.featureJungle, 1)
                                        else:
                                                pPlot.setFeatureType(self.featureSavanna, 1) # PAE Savanna
                                elif self.forests.getHeight(iX, iY) <= self.iForestLevelPlains - diceSize + diceRoll and dice.get(100, "Dice Roll") > 8:
                                        pPlot.setFeatureType(self.featureForest, 1)
                        elif pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_GRASS"):
                                if self.forests.getHeight(iX, iY) <= self.iForestLevel - diceSize + diceRoll and dice.get(100, "Dice Roll") > 8:
                                        if self.map.getClimate() == 2 or self.map.getClimate() == 1:
                                                pPlot.setFeatureType(self.featureJungle, 1)
                                        else:
                                                # PAE Dense Forest
                                                if dice.get(2, "Dice Roll") < 1:
                                                  pPlot.setFeatureType(self.featureForest, 1)
                                                else:
                                                  pPlot.setFeatureType(self.featureDenseForest, 0)
                        elif pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_TUNDRA"):
                                if self.forests.getHeight(iX, iY) <= self.iForestLevel - diceSize + diceRoll and dice.get(100, "Dice Roll") > 8:
                                        pPlot.setFeatureType(self.featureForest, 2)

                        # Add flood plains and oasis to desert
                        if pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_DESERT"):
                                if pPlot.isFlatlands():
                                        if pPlot.isRiver():
                                                pPlot.setFeatureType(self.featureFlood, 1)
                                        else:
                                                if self.oasis.getHeight(iX, iY) <= self.iOasisLevel and pPlot.canHaveFeature(self.featureOasis):
                                                        pPlot.setFeatureType(self.featureOasis, 1)

                        # PAE: Add swamp to tundra or grass
                        if pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_TUNDRA") or pPlot.getTerrainType() == self.gc.getInfoTypeForString("TERRAIN_GRASS"):
                                if pPlot.isFlatlands():
                                        if pPlot.isRiver() and dice.get(100, "Dice Roll") < 30:
                                                pPlot.setTerrainType(self.gc.getInfoTypeForString("TERRAIN_SWAMP"), true, true)


def addFeatures():
        NiTextOut("Adding Features (Python Boreal) ...")
        featuregen = BorealFeatureGenerator()
        featuregen.addFeatures()
        return 0

def assignStartingPlots():
        # This function borrowed from Highlands. Just as insurance against duds.
        # Lake fill-ins changed to tundra instead of plains.
        # - Sirian - June 2, 2007
        #
        #
        # In order to prevent "pockets" from forming, where civs can be blocked in
        # by Peaks or lakes, causing a "dud" map, pathing must be checked for each
        # new start plot before it hits the map. Any pockets that are detected must
        # be opened. The following process takes care of this need. Soren created a
        # useful function that already lets you know how far a given plot is from
        # the closest nearest civ already on the board. MinOriginalStartDist is that
        # function. You can get-- or setMinoriginalStartDist() as a value attached
        # to each plot. Any value of -1 means no valid land-hills-only path exists to
        # a civ already placed. For Highlands, that means we have found a pocket
        # and it must be opened. A valid legal path from all civs to all other civs
        # is required for this map to deliver reliable, fun games every time.
        #
        # - Sirian - 2005
        #
        gc = CyGlobalContext()
        map = CyMap()
        dice = gc.getGame().getMapRand()
        iW = map.getGridWidth()
        iH = map.getGridHeight()
        iPlayers = gc.getGame().countCivPlayersEverAlive()
        iNumStartsAllocated = 0
        start_plots = []
        print "==="
        print "Number of players:", iPlayers
        print "==="
        terrainFill = gc.getInfoTypeForString("TERRAIN_GRASS")
        if map.getClimate() == 2:
                terrainFill = gc.getInfoTypeForString("TERRAIN_DESERT")
        if map.getClimate() == 4:
                terrainFill = gc.getInfoTypeForString("TERRAIN_TUNDRA")

        # Calculate minimum allowed distance between starting locations
        plotsPerPlayer = iW * iH / iPlayers
        minDistance = sqrt(plotsPerPlayer) / 1.8
        print("Minimum starting location distance:", minDistance)

        # Obtain player numbers. (Account for possibility of Open slots!)
        player_list = []
        for plrCheckLoop in range(18):
                if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
                        player_list.append(plrCheckLoop)
        # Shuffle players so that who goes first (and gets the best start location) is randomized.
        shuffledPlayers = []
        for playerLoopTwo in range(gc.getGame().countCivPlayersEverAlive()):
                iChoosePlayer = dice.get(len(player_list), "Shuffling Players - Highlands PYTHON")
                shuffledPlayers.append(player_list[iChoosePlayer])
                del player_list[iChoosePlayer]

        # Loop through players, assigning starts for each.
        for assign_loop in range(iPlayers):
                playerID = shuffledPlayers[assign_loop]
                player = gc.getPlayer(playerID)

                # Use the absolute approach for findStart from CvMapGeneratorUtil, which
                # ignores areaID quality and finds the best local situation on the board.
                # findstart = CvMapGeneratorUtil.findStartingPlot(playerID)

                # Find starting location
                print("Finding start location for player ", playerID)
                done = 0
                loops = 0
                xPos = 0
                yPos = 0
                while done == 0 and loops < 1000:
                        xPos = 2 + dice.get(iW - 6, "Dice roll - CA test PYTHON")
                        yPos = 2 + dice.get(iH - 6, "Dice roll - CA test PYTHON")
                        testPlot = map.plot(xPos, yPos)
                        #print("Testing plot:", testPlot.getX(), testPlot.getY())
                        # Check minDistance to other civs
                        if testPlot.getMinOriginalStartDist() != -1 and testPlot.getMinOriginalStartDist() < minDistance:
                                #print("Too close to another civ", testPlot.getMinOriginalStartDist())
                                loops += 1
                                continue
                        if testPlot.isPeak() or testPlot.isWater():
                                #print("Inhabitable plot!")
                                loops += 1
                                continue
                        if map.getClimate() == 2:
                                if (testPlot.getFeatureType() != gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")):
                                        #print("Not flood plains!")
                                        # Require flood plain start for desert map
                                        loops += 1
                                        continue
                        # Check that surroundings are good enough
                        #print("Checking surroundings")
                        iRegionNetYield = 0
                        hillCount = 0
                        fertilePlots = 0
                        for dy in range(-2, 3):
                                for dx in range(-2, 3):
                                        if abs(dx) + abs(dy) == 4:
                                                continue
                                        testPlot = map.plot(xPos + dx, yPos + dy)
                                        #print("Plot:", testPlot.getX(), testPlot.getY())
                                        iPlotYield = testPlot.calculateTotalBestNatureYield(TeamTypes.NO_TEAM)
                                        #print("Yield:", iPlotYield)
                                        iFertileCheck = testPlot.calculateBestNatureYield(YieldTypes.YIELD_FOOD, TeamTypes.NO_TEAM)
                                        if map.getClimate() == 4:
                                                if testPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_PLAINS"):
                                                        iFertileCheck += 1
                                        #print("FertileCheck:", iFertileCheck)
                                        if iFertileCheck > 1: # If the plot has extra food, count the extra as double value!
                                                iPlotYield += (iFertileCheck - 1)
                                                fertilePlots += 1
                                        iRegionNetYield += iPlotYield
                                        if testPlot.isHills():
                                                iRegionNetYield += 1 # Add a bonus point for Hills plots.
                                                hillCount += 1
                                        #print("YieldSum:", iRegionNetYield)
                        print("Net yield for plot ", xPos, yPos, ":", iRegionNetYield)
                        if iRegionNetYield < 60 or fertilePlots < 4:
                                loops += 1
                                continue
                        # We found a valid starting location!
                        done = 1
                        # Make sure there are at least two hills
                        if hillCount < 2:
                                print("Adding hills:", 2 - hillCount)
                                for i in range(0, 2 - hillCount):
                                        for loop1 in range(0, 100):
                                                dx = -2 + dice.get(5, "")
                                                dy = -2 + dice.get(5, "")
                                                if abs(dx) + abs(dy) == 4:
                                                        continue
                                                testPlot = map.plot(xPos + dx, yPos + dy)
                                                if testPlot.isWater() or testPlot.isPeak():
                                                        continue
                                                if testPlot.getBonusType(-1) == -1:
                                                        testPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
                                                        testPlot.setFeatureType(-1,1)
                                                        print "Added hill"
                                                        break
                                        if loop1 >= 100:
                                                print "Failed to add hill"

                        # Desert special
                        if map.getClimate() == 2:
                                print "Desert special"
                                res1 = dice.get(2, "")
                                res2 = dice.get(2, "")
                                resource1 = 'BONUS_IVORY'
                                resource2 = 'BONUS_WHEAT'
                                if res1 == 1:
                                        resource1 = 'BONUS_COW'
                                if res2 == 1:
                                        resource2 = 'BONUS_CORN'
                                found1 = 0
                                found2 = 0
                                for loop1 in range(0, 100):
                                        dx = -2 + dice.get(5, "")
                                        dy = -2 + dice.get(5, "")
                                        if abs(dx) + abs(dy) == 4:
                                                continue
                                        testPlot = map.plot(xPos + dx, yPos + dy)
                                        if testPlot.getBonusType(-1) == -1:
                                                if testPlot.canHaveBonus(gc.getInfoTypeForString(resource1), true) or testPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS"):
                                                        testPlot.setBonusType(gc.getInfoTypeForString(resource1))
                                                        found1 = 1
                                                        break
                                for loop2 in range(0, 100):
                                        dx = -2 + dice.get(5, "")
                                        dy = -2 + dice.get(5, "")
                                        if abs(dx) + abs(dy) == 4:
                                                continue
                                        testPlot = map.plot(xPos + dx, yPos + dy)
                                        if testPlot.getBonusType(-1) == -1:
                                                if testPlot.canHaveBonus(gc.getInfoTypeForString(resource2), true) or testPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS"):
                                                        testPlot.setBonusType(gc.getInfoTypeForString(resource2))
                                                        found2 = 1
                                                        break
                                if found1 == 0 or found2 == 0:
                                        print "Could not find desert bonus location..."

                sPlot = map.plot(xPos, yPos)
                if loops >= 1000:
                        print("Did not find a random location, using default impl instead")
                        findStart = CvMapGeneratorUtil.findStartingPlot(playerID)
                        sPlot = map.plotByIndex(findStart)
                print("Found location at:", xPos, yPos, "Loops:", loops)


                player1Plot = sPlot

                # Record the plot number to the data array for use if needed to open a "pocket".
                iStartX = sPlot.getX()
                iStartY = sPlot.getY()

                # If first player placed, no need to check for pathing yet.
                if assign_loop == 0:
                        start_plots.append([iStartX, iStartY])
                        player.setStartingPlot(sPlot, true) # True flag causes data to be refreshed for MinOriginalStartDist data cells in plots on the same land mass.
                        print "-+-+-"
                        print "Player"
                        print playerID
                        print "First player assigned."
                        print "-+-+-"
                        continue

                # Check the pathing in the start plot.
                # Find closest previous start plot
                [iEndX, iEndY] = start_plots[0]
                fMinDistance = sqrt(((iStartX - iEndX) ** 2) + ((iStartY - iEndY) ** 2))
                for check_loop in range(1, len(start_plots)):
                        [iX, iY] = start_plots[check_loop]
                        if fMinDistance > sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2)):
                                # Closer start plot found!
                                [iEndX, iEndY] = start_plots[check_loop]
                                fMinDistance = sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2))
                playerPlot = map.plot(iEndX, iEndY)
                # print("plot:", iStartX, iStartY, sPlot.getMinOriginalStartDist(), map.calculatePathDistance(sPlot, playerPlot))
                if map.calculatePathDistance(sPlot, playerPlot) != -1:
                        print "-+-+-"
                        print "Player"
                        print playerID
                        print "Open Path, no problems. Dist:", sPlot.getMinOriginalStartDist()
                        print "-+-+-"
                        start_plots.append([iStartX, iStartY])
                        player.setStartingPlot(sPlot, true)
                        continue

                # If the process has reached this point, then this player is stuck
                # in a "pocket". This could be an island, a valley surrounded by peaks,
                # or an area blocked off by peaks. Could even be that a major line
                # of peaks and lakes combined is bisecting the entire map.
                print "-----"
                print "Player"
                print playerID
                print "Pocket detected, attempting to resolve..."
                print "-----"
                #
                # First step is to identify which existing start plot is closest.
                print "Pocket Plot"
                print iStartX, iStartY
                print "---"
                [iEndX, iEndY] = start_plots[0]
                fMinDistance = sqrt(((iStartX - iEndX) ** 2) + ((iStartY - iEndY) ** 2))
                for check_loop in range(1, len(start_plots)):
                        [iX, iY] = start_plots[check_loop]
                        if fMinDistance > sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2)):
                                # Closer start plot found!
                                [iEndX, iEndY] = start_plots[check_loop]
                                fMinDistance = sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2))
                print "Nearest player (path destination)"
                print iEndX, iEndY
                print "---"
                print "Absolute distance:"
                print fMinDistance
                print "-----"

                # Now we draw an invisible line, plot by plot, one plot wide, from
                # the current start to the nearest start, converting peaks along the
                # way in to hills, and lakes in to flatlands, until a path opens.

                # Bulldoze the path until it opens!
                startPlot = map.plot(iStartX, iStartY)
                endPlot = map.plot(iEndX, iEndY)
                step = 1
                if abs(iEndY-iStartY) < abs(iEndX-iStartX):
                        # line is closer to horizontal
                        startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
                        dx = endX-startX
                        dy = endY-startY
                        if dx < 0:
                                step = -1
                        if dx == 0 or dy == 0:
                                slope = 0
                        else:
                                slope = float(dy)/float(dx)
                        print("Slope: ", slope)
                        y = startY
                        for x in range(startX, endX, step):
                                print "Checking plot"
                                print x, int(round(y))
                                print "---"
                                if map.isPlot(x, int(round(y))):
                                        i = map.plotNum(x, int(round(y)))
                                        pPlot = map.plotByIndex(i)
                                        y += slope * step
                                        print("y plus slope: ", y)
                                        if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
                                        if pPlot.isPeak():
                                                print "Peak found! Bulldozing this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break
                                        elif pPlot.isWater():
                                                print "Lake found! Filling in this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
                                                pPlot.setTerrainType(terrainFill, true, true)
                                                if pPlot.getBonusType(-1) != -1:
                                                        print "########################"
                                                        print "A sea-based Bonus is now present on the land! EEK!"
                                                        print "########################"
                                                        pPlot.setBonusType(-1)
                                                        print "OK, nevermind. The resource has been removed."
                                                        print "########################"
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break

                else:
                        # line is closer to vertical
                        startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
                        dx, dy = endX-startX, endY-startY
                        if dy < 0:
                                step = -1
                        if dx == 0 or dy == 0:
                                slope = 0
                        else:
                                slope = float(dx)/float(dy)
                        print("Slope: ", slope)
                        x = startX
                        for y in range(startY, endY+1, step):
                                print "Checking plot"
                                print int(round(x)), y
                                print "---"
                                if map.isPlot(int(round(x)), y):
                                        i = map.plotNum(int(round(x)), y)
                                        pPlot = map.plotByIndex(i)
                                        x += slope * step
                                        print("x plus slope: ", x)
                                        if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
                                        if pPlot.isPeak():
                                                print "Peak found! Bulldozing this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break
                                        elif pPlot.isWater():
                                                print "Lake found! Filling in this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
                                                pPlot.setTerrainType(terrainFill, true, true)
                                                if pPlot.getBonusType(-1) != -1:
                                                        print "########################"
                                                        print "A sea-based Bonus is now present on the land! EEK!"
                                                        print "########################"
                                                        pPlot.setBonusType(-1)
                                                        print "OK, nevermind. The resource has been removed."
                                                        print "########################"
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break

                # Now that all the pathing for this player is resolved, set the start plot.
                start_plots.append([iStartX, iStartY])
                player.setStartingPlot(sPlot, true)

        # All done!
        print "**********"
        print "All start plots assigned!"
        print "**********"

        print("NrAreas:", map.getNumAreas())
        # ****************
        # ****************
        # Eliminate other duds on the map with the same method
        # ****************
        # ****************
        print "Find other duds on the map"
        maxIndex = iW * iH
        for index in range(maxIndex):
                sPlot = map.plotByIndex(index)
                if sPlot.isWater() or sPlot.isPeak():
                        continue
                iStartX = sPlot.getX()
                iStartY = sPlot.getY()
                # Find closest start plot
                [iEndX, iEndY] = start_plots[0]
                fMinDistance = sqrt(((iStartX - iEndX) ** 2) + ((iStartY - iEndY) ** 2))
                for check_loop in range(1, len(start_plots)):
                        [iX, iY] = start_plots[check_loop]
                        if fMinDistance > sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2)):
                                # Closer start plot found!
                                [iEndX, iEndY] = start_plots[check_loop]
                                fMinDistance = sqrt(((iStartX - iX) ** 2) + ((iStartY - iY) ** 2))
                playerPlot = map.plot(iEndX, iEndY)
                # print("plot:", iStartX, iStartY, sPlot.getMinOriginalStartDist(), map.calculatePathDistance(sPlot, playerPlot))
                if map.calculatePathDistance(sPlot, playerPlot) != -1:
                        continue

                # If the process has reached this point, then this plot is stuck
                # in a "pocket". This could be an island, a valley surrounded by peaks,
                # or an area blocked off by peaks. Could even be that a major line
                # of peaks and lakes combined is bisecting the entire map.
                #

                print "-----"
                print "Pocket detected, attempting to resolve..."
                print "-----"
                print "Pocket Plot"
                print iStartX, iStartY
                print "---"
                print "Nearest player (path destination)"
                print iEndX, iEndY
                print "---"
                print "Absolute distance:"
                print fMinDistance
                print "-----"

                # Now we draw an invisible line, plot by plot, one plot wide, from
                # the current start to the nearest start, converting peaks along the
                # way in to hills, and lakes in to flatlands, until a path opens.

                # Bulldoze the path until it opens!
                startPlot = map.plot(iStartX, iStartY)
                endPlot = map.plot(iEndX, iEndY)
                step = 1
                if abs(iEndY-iStartY) < abs(iEndX-iStartX):
                        # line is closer to horizontal
                        startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
                        dx = endX-startX
                        dy = endY-startY
                        if dx < 0:
                                step = -1
                        if dx == 0 or dy == 0:
                                slope = 0
                        else:
                                slope = float(dy)/float(dx)
                        print("Slope: ", slope)
                        y = startY
                        for x in range(startX, endX, step):
                                print "Checking plot"
                                print x, int(round(y))
                                print "---"
                                if map.isPlot(x, int(round(y))):
                                        i = map.plotNum(x, int(round(y)))
                                        pPlot = map.plotByIndex(i)
                                        y += slope * step
                                        print("y plus slope: ", y)
                                        if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
                                        if pPlot.isPeak():
                                                print "Peak found! Bulldozing this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break
                                        elif pPlot.isWater():
                                                print "Lake found! Filling in this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
                                                pPlot.setTerrainType(terrainFill, true, true)
                                                if pPlot.getBonusType(-1) != -1:
                                                        print "########################"
                                                        print "A sea-based Bonus is now present on the land! EEK!"
                                                        print "########################"
                                                        pPlot.setBonusType(-1)
                                                        print "OK, nevermind. The resource has been removed."
                                                        print "########################"
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break

                else:
                        # line is closer to vertical
                        startX, startY, endX, endY = iStartX, iStartY, iEndX, iEndY
                        dx, dy = endX-startX, endY-startY
                        if dy < 0:
                                step = -1
                        if dx == 0 or dy == 0:
                                slope = 0
                        else:
                                slope = float(dx)/float(dy)
                        print("Slope: ", slope)
                        x = startX
                        for y in range(startY, endY+1, step):
                                print "Checking plot"
                                print int(round(x)), y
                                print "---"
                                if map.isPlot(int(round(x)), y):
                                        i = map.plotNum(int(round(x)), y)
                                        pPlot = map.plotByIndex(i)
                                        x += slope * step
                                        print("x plus slope: ", x)
                                        if pPlot.isHills() or pPlot.isFlatlands(): continue # on to next plot!
                                        if pPlot.isPeak():
                                                print "Peak found! Bulldozing this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break
                                        elif pPlot.isWater():
                                                print "Lake found! Filling in this plot."
                                                print "---"
                                                pPlot.setPlotType(PlotTypes.PLOT_LAND, true, true)
                                                pPlot.setTerrainType(terrainFill, true, true)
                                                if pPlot.getBonusType(-1) != -1:
                                                        print "########################"
                                                        print "A sea-based Bonus is now present on the land! EEK!"
                                                        print "########################"
                                                        pPlot.setBonusType(-1)
                                                        print "OK, nevermind. The resource has been removed."
                                                        print "########################"
                                                currentDistance = map.calculatePathDistance(pPlot, endPlot)
                                                if currentDistance != -1: # The path has been opened!
                                                        print "Pocket successfully opened!"
                                                        print "-----"
                                                        break


        # ****************
        # ****************
        # Ready!!!
        # ****************
        # ****************
        print "*************"
        print "Entire map checked for duds!"
        print "*************"
        return None

def normalizeRemovePeaks():
        return None

def normalizeRemoveBadTerrain():
        return None

def normalizeAddGoodTerrain():
        return None

def normalizeAddExtras():
        return None

# Sirian's "Sahara Regional Bonus Placement" system.

def addBonusType(argsList):
        print('*******')
        [iBonusType] = argsList
        gc = CyGlobalContext()
        map = CyMap()
        dice = gc.getGame().getMapRand()
        type_string = gc.getBonusInfo(iBonusType).getType()
        iW = map.getGridWidth()
        iH = map.getGridHeight()
        nrPlayers = gc.getGame().countCivPlayersEverAlive()

        # Init all bonuses.
        bonusRare = ('BONUS_GOLD', 'BONUS_DYE', 'BONUS_RICE', 'BONUS_INCENSE', 'BONUS_SILK',
                     'BONUS_IVORY', 'BONUS_GEMS', 'BONUS_GRAPES', 'BONUS_SILVER', 'BONUS_SPICES', 'BONUS_HORSE')
        bonusNormal = ('BONUS_COAL', 'BONUS_ZINN', 'BONUS_COW', 'BONUS_SHEEP')
        bonusCommon = ('BONUS_COPPER', 'BONUS_IRON', 'BONUS_WHEAT', 'BONUS_FISH', 'BONUS_PIG')
        bonusExtraCommon = ('BONUS_COPPER')
        bonusFractal = ('BONUS_DEER', 'BONUS_FUR', 'BONUS_STONE', 'BONUS_BANANA', 'BONUS_MARBLE')
        needsChopping = ('BONUS_SHEEP', 'BONUS_GRAPES', 'BONUS_WHEAT', 'BONUS_IVORY', 'BONUS_COW')
        needHills = ('BONUS_COAL', 'BONUS_IRON', 'BONUS_COPPER', 'BONUS_GOLD', 'BONUS_SILVER')
        extraTactical = ('BONUS_OIL')
        deer = ('BONUS_DEER')
        fur = ('BONUS_FUR')
        banana = ('BONUS_BANANA')
        stone = ('BONUS_STONE')
        marble = ('BONUS_MARBLE')
        floodPlainsExtra = ('BONUS_COW', 'BONUS_WHEAT', 'BONUS_IVORY', 'BONUS_HORSE')
        resourcesToEliminate = ('BONUS_PIG', 'BONUS_CLAM', 'BONUS_SPICES', 'BONUS_SILVER')
        if  map.getClimate() == 1:
                resourcesToEliminate = ('BONUS_SILK', 'BONUS_FUR', 'BONUS_SHEEP', 'BONUS_WHEAT', 'BONUS_SILVER', 'BONUS_CRAB', 'BONUS_DEER')
                extraTactical = ('BONUS_GEMS', 'BONUS_RICE', 'BONUS_DYE')
        if  map.getClimate() == 2:
                resourcesToEliminate = ('BONUS_PIG', 'BONUS_RICE', 'BONUS_SILK', 'BONUS_FUR', 'BONUS_DYE')
        if  map.getClimate() == 4:
                resourcesToEliminate = ('BONUS_PIG', 'BONUS_RICE', 'BONUS_SILK', 'BONUS_DYE', 'BONUS_SUGAR', 'BONUS_WHEAT',
                                                                'BONUS_SPICES', 'BONUS_IVORY', 'BONUS_BANANA', 'BONUS_INCENSE')
                needHills = ('BONUS_GEMS', 'BONUS_COAL', 'BONUS_IRON', 'BONUS_COPPER', 'BONUS_GOLD', 'BONUS_SILVER')
                bonusRare = ('BONUS_GOLD', 'BONUS_SILVER')
                bonusCommon = ('BONUS_COPPER', 'BONUS_IRON', 'BONUS_FISH', 'BONUS_GEMS')
                bonusExtraCommon = ('BONUS_COPPER', 'BONUS_FISH')

        print('---', type_string, '---')

        if (type_string in resourcesToEliminate):
                print('-NONE-', type_string, '-NONE-')
                return None # These bonus types will not appear, unless given as starting location bonus.

        # Generate fractal featured resources
        if (type_string in bonusFractal):
                print("Fractal resource implementation:", type_string)
                furDist = CyFractal()
                furDist.fracInit(iW, iH, 7, gc.getGame().getMapRand(), 0, -1, -1)
                furLevelBottom = furDist.getHeightFromPercent(80)
                furLevelTop = furDist.getHeightFromPercent(90)
                deerDist = CyFractal()
                deerDist.fracInit(iW, iH, 7, gc.getGame().getMapRand(), 0, -1, -1)
                deerLevelBottom = deerDist.getHeightFromPercent(75)
                deerLevelTop = deerDist.getHeightFromPercent(90)
                bananaDist = CyFractal()
                bananaDist.fracInit(iW, iH, 7, gc.getGame().getMapRand(), 0, -1, -1)
                bananaLevelBottom = bananaDist.getHeightFromPercent(75)
                bananaLevelTop = bananaDist.getHeightFromPercent(90)
                stoneDist = CyFractal()
                stoneDist.fracInit(iW, iH, 7, gc.getGame().getMapRand(), 0, -1, -1)
                stoneLevelBottom = stoneDist.getHeightFromPercent(80)
                stoneLevelTop = stoneDist.getHeightFromPercent(90)
                marbleDist = CyFractal()
                marbleDist.fracInit(iW, iH, 7, gc.getGame().getMapRand(), 0, -1, -1)
                marbleLevelBottom = marbleDist.getHeightFromPercent(80)
                marbleLevelTop = marbleDist.getHeightFromPercent(90)
                # Desert
                if (map.getClimate() == 2):
                        bananaLevelBottom = bananaDist.getHeightFromPercent(65)
                        stoneLevelBottom = stoneDist.getHeightFromPercent(70)
                        marbleLevelBottom = marbleDist.getHeightFromPercent(85)
                # Cold
                if (map.getClimate() == 4):
                        deerDist.fracInit(iW, iH, 8, gc.getGame().getMapRand(), 0, -1, -1)
                        deerLevelBottom = deerDist.getHeightFromPercent(65)
                        deerLevelTop = deerDist.getHeightFromPercent(82)
                        furLevelBottom = furDist.getHeightFromPercent(68)
                        furLevelTop = furDist.getHeightFromPercent(80)

                for y in range(iH):
                        for x in range(iW):
                                # Fractalized placement
                                pPlot = map.plot(x,y)
                                if pPlot.getBonusType(-1) != -1 or pPlot.isPeak():
                                        continue
                                if (type_string in deer):
                                        if pPlot.isFlatlands() and (pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST") or (map.getClimate() == 2 and pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_PLAINS"))):
                                                distVal = deerDist.getHeight(x,y)
                                                if (distVal >= deerLevelBottom and distVal < deerLevelTop):
                                                        map.plot(x,y).setBonusType(iBonusType)
                                if (type_string in fur):
                                        if pPlot.getTerrainType() != gc.getInfoTypeForString("TERRAIN_PLAINS") and pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
                                                distVal = furDist.getHeight(x,y)
                                                if (distVal >= furLevelBottom and distVal < furLevelTop):
                                                        map.plot(x,y).setBonusType(iBonusType)
                                if (type_string in banana):
                                        if pPlot.isFlatlands() and pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                                                distVal = bananaDist.getHeight(x,y)
                                                if (distVal >= bananaLevelBottom and distVal < bananaLevelTop):
                                                        map.plot(x,y).setBonusType(iBonusType)
                                if (type_string in stone):
                                        if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT") and pPlot.getFeatureType() == -1:
                                                distVal = stoneDist.getHeight(x,y)
                                                if (distVal >= stoneLevelBottom and distVal < stoneLevelTop):
                                                        map.plot(x,y).setBonusType(iBonusType)
                                if (type_string in marble):
                                        if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_TUNDRA") or pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_SNOW") or ((map.getClimate() == 2 or map.getClimate() == 1) and pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_DESERT")):
                                                distVal = marbleDist.getHeight(x,y)
                                                if (distVal >= marbleLevelBottom and distVal < marbleLevelTop):
                                                        pPlot.setFeatureType(-1,1)
                                                        map.plot(x,y).setBonusType(iBonusType)

        # Generate special featured resources
        if (type_string in bonusCommon or type_string in bonusRare or type_string in bonusNormal):
                print("Special resource implementation:", type_string)

                # Default limits
                maxCount = nrPlayers + 1
                maxNrClusters = 1
                maxClusterCount = 4
                if map.getWorldSize() >= 3:
                        maxNrClusters += 1
                clusterProb = 30
                plotProb = 70

                # Resource specific limits
                if (type_string in bonusCommon):
                        maxCount += map.getWorldSize() + 1
                        maxNrClusters = 3
                        maxClusterCount = 3
                        if (type_string in bonusExtraCommon):
                                maxCount += 2 * (map.getWorldSize() + 1)
                                maxNrClusters += 2
                        if map.getWorldSize() >= 2:
                                maxNrClusters += 1
                        if map.getWorldSize() >= 4:
                                maxNrClusters += 1
                        clusterProb = 20
                if (type_string in needHills):
                        clusterProb = 40
                if (type_string in bonusRare):
                        print("Rare resource")
                        maxCount /= 2
                        maxNrClusters = 1
                        clusterProb = 60
                        maxClusterCount = 6
                if (type_string in extraTactical):
                        maxNrClusters += 1
                        maxCount += 1

                # Place resource
                count = 0
                nrClusters = 0
                orgClusterProb = clusterProb
                for count in range(maxCount):
                        done = 0
                        loops = 0
                        while done == 0 and loops < 1000:
                                xPos = dice.get(iW,"")
                                yPos = dice.get(iH,"")
                                dx = 0
                                dy = 0
                                for localLoop in range(0, 10):
                                        pPlot = map.plot(xPos + dx, yPos + dy)
                                        if pPlot.getBonusType(-1) == -1:
                                                if (type_string in needHills):
                                                        if pPlot.isHills():
                                                                pPlot.setBonusType(iBonusType)
                                                                done = 1
                                                elif (type_string in floodPlainsExtra and pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")):
                                                        if map.getClimate() == 2:
                                                                pPlot.setBonusType(iBonusType)
                                                                done = 1
                                                elif (type_string in needsChopping):
                                                        changedForest = 0
                                                        resourceSet = 0
                                                        if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
                                                                pPlot.setFeatureType(-1,1)
                                                                changedForest = 1
                                                        if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                                                                pPlot.setFeatureType(-1,1)
                                                                changedForest = 2
                                                        if pPlot.canHaveBonus(iBonusType, true):
                                                                pPlot.setBonusType(iBonusType)
                                                                resourceSet = 1
                                                                done = 1
                                                        if changedForest == 1 and resourceSet == 0: # Put forest back
                                                                variety = 1
                                                                if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_TUNDRA"):
                                                                        variety = 2
                                                                pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"), variety)
                                                        if changedForest == 2 and resourceSet == 0: # Put jungle back
                                                                pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_JUNGLE"), 1)
                                                else:
                                                        if pPlot.canHaveBonus(iBonusType, true):
                                                                pPlot.setBonusType(iBonusType)
                                                                done = 1
                                        if done == 1:
                                                break
                                        dx = -3 + dice.get(7, "")
                                        dy = -3 + dice.get(7, "")
                                        if xPos + dx >= iW or xPos + dx < 0:
                                                dx = 0
                                        if yPos + dy >= iH or yPos + dy < 0:
                                                dy = 0
                                if done == 0:
                                        loops = loops + 1
                        if loops >= 1000:
                                print("Could not find spot for resource")
                                return None
                        xPos += dx
                        yPos += dy
                        print("Special resource at:", xPos, yPos)
                        neededTerrain = pPlot.getTerrainType()
                        xPos = min(iW - 3, xPos - 1)
                        yPos = min(iH - 3, yPos - 1)
                        xPos = max(xPos, 0)
                        yPos = max(yPos, 0)

                        # Fill in possible cluster
                        clusterCount = 1 # middle plot is already assigned
                        diceRoll = dice.get(100, "Dice roll")
                        if diceRoll <= clusterProb and nrClusters < maxNrClusters:
                                print("Clustering special resource")
                                for y in range(yPos, yPos + 3):
                                        for x in range(xPos, xPos + 3):
                                                pPlot = map.plot(x,y)
                                                diceRoll = dice.get(100, "Dice roll - CA test PYTHON")
                                                if pPlot.getBonusType(-1) == -1:
                                                        if (type_string in needHills):
                                                                if pPlot.isHills():
                                                                        if diceRoll <= plotProb and clusterCount < maxClusterCount:
                                                                                pPlot.setBonusType(iBonusType)
                                                                                clusterCount = clusterCount + 1
                                                        elif (type_string in floodPlainsExtra and pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")):
                                                                if map.getClimate() == 2:
                                                                        if diceRoll <= plotProb and clusterCount < maxClusterCount:
                                                                                pPlot.setBonusType(iBonusType)
                                                                                clusterCount = clusterCount + 1
                                                        elif (type_string in needsChopping):
                                                                changedForest = 0
                                                                resourceSet = 0
                                                                if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_FOREST"):
                                                                        pPlot.setFeatureType(-1,1)
                                                                        print("Chopping forest at", x, y)
                                                                        changedForest = 1
                                                                if pPlot.getFeatureType() == gc.getInfoTypeForString("FEATURE_JUNGLE"):
                                                                        pPlot.setFeatureType(-1,1)
                                                                        print("Chopping jungle at", x, y)
                                                                        changedForest = 2
                                                                if pPlot.canHaveBonus(iBonusType, true):
                                                                        if diceRoll <= plotProb and clusterCount < maxClusterCount:
                                                                                pPlot.setBonusType(iBonusType)
                                                                                clusterCount = clusterCount + 1
                                                                                resourceSet = 1
                                                                if changedForest == 1 and resourceSet == 0: # Put forest back
                                                                        variety = 1
                                                                        if pPlot.getTerrainType() == gc.getInfoTypeForString("TERRAIN_TUNDRA"):
                                                                                variety = 2
                                                                        pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_FOREST"), variety)
                                                                if changedForest == 2 and resourceSet == 0: # Put jungle back
                                                                        pPlot.setFeatureType(gc.getInfoTypeForString("FEATURE_JUNGLE"), 1)

                                                        else:
                                                                if pPlot.canHaveBonus(iBonusType, true):
                                                                        if diceRoll <= plotProb and clusterCount < maxClusterCount:
                                                                                pPlot.setBonusType(iBonusType)
                                                                                clusterCount = clusterCount + 1
                                if clusterCount == 1:
                                        print ("Failed creating cluster")
                                        clusterProb = 100
                                else:
                                        nrClusters = nrClusters + 1
                                        clusterProb = orgClusterProb


        # Generate standard resources
        if (not type_string in bonusRare and not type_string in bonusFractal and not type_string in bonusCommon and not type_string in bonusNormal):
                print("Standard resource implementation:", type_string)
                CyPythonMgr().allowDefaultImpl() # Let C handle this bonus in the default way.

        return None
